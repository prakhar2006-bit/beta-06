"""Offline verification-ledger to schema-mapped draft preparation; never SQL execution."""
import argparse
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
import re
from uuid import UUID

from ingestion.prepare import InputError, digest, encode, parse_json, validate_records

ENGINE = Path(__file__).resolve().parents[1]


def table_columns():
    """Read the actual foundation migration, without importing runtime DB code."""
    sql = (ENGINE / 'supabase/migrations/20261030000100_catalog.sql').read_text(encoding='utf-8')
    tables = {}
    for table, block in re.findall(r'CREATE TABLE scheme_catalog\.(\w+) \((.*?)\n\);', sql, re.S):
        tables[table] = {match.group(1) for line in block.splitlines()
                         if (match := re.match(r'    ([a-z_][a-z_0-9]*)\s+(?:uuid|text|integer|date|timestamptz|numeric|jsonb)\b', line))}
    return tables


def unique(items, key, label):
    values = [item[key] for item in items]
    if len(set(values)) != len(values):
        raise InputError('Duplicate ' + label)


def validate_draft(payload):
    if (payload.get('mode') != 'local_draft_only' or payload.get('publish_allowed') is not False
            or payload.get('eligible_for_execution') is not False or payload.get('database_operations') != []):
        raise InputError('Only unpublished local preparation is supported')
    rows = payload['rows']
    allowed = table_columns()
    if set(rows) - set(allowed):
        raise InputError('Unknown database table')
    identities = {}
    for table, records in rows.items():
        if not isinstance(records, list):
            raise InputError('Table rows must be an array')
        unique(records, 'id', table + ' UUID')
        identities[table] = {row['id'] for row in records}
        for row in records:
            if set(row) - allowed[table]:
                raise InputError('Unsupported columns in ' + table)
            for key, value in row.items():
                if key in {'id', 'parent_id', 'organization_id', 'source_id', 'snapshot_id', 'scheme_id',
                           'scheme_version_id', 'jurisdiction_id', 'evidence_id', 'rule_id', 'ingestion_run_id'} and value is not None:
                    UUID(value)
            if table == 'scheme_versions' and (row.get('status') != 'draft' or row.get('reviewed_at') is not None or row.get('published_at') is not None):
                raise InputError('Version must remain unreviewed draft')
            if table == 'translations' and row.get('review_status') != 'draft':
                raise InputError('Translations require human review')
            if table == 'eligibility_rules' and row.get('confidence') != 'UNCERTAIN':
                raise InputError('Draft rule confidence must remain UNCERTAIN')
    for table, key in [('schemes', 'stable_id'), ('organizations', 'code'), ('jurisdictions', 'code'), ('official_sources', 'original_url')]:
        unique(rows.get(table, []), key, table + '.' + key)
    for table, records in rows.items():
        for row in records:
            references = {'organization_id': 'organizations', 'source_id': 'official_sources',
                          'snapshot_id': 'source_snapshots', 'scheme_id': 'schemes',
                          'scheme_version_id': 'scheme_versions', 'jurisdiction_id': 'jurisdictions',
                          'evidence_id': 'evidence', 'rule_id': 'eligibility_rules', 'ingestion_run_id': 'ingestion_runs'}
            for field, target in references.items():
                if row.get(field) is not None and row[field] not in identities.get(target, set()):
                    raise InputError('Unresolved draft FK ' + table + '.' + field)
    for table, key in [('benefits', 'item_key'), ('application_routes', 'item_key'), ('required_documents', 'item_key'), ('eligibility_rules', 'rule_key'), ('translations', 'language_code')]:
        unique([{'pair': (r['scheme_version_id'], r[key])} for r in rows.get(table, [])], 'pair', table + ' version key')
    claims = payload['verification']['claims']
    unique(claims, 'claim_id', 'claim identifier')
    sources = {s['source_id']: s for s in payload['verification']['sources']}
    unique(payload['verification']['sources'], 'source_id', 'verification source identifier')
    for claim in claims:
        date.fromisoformat(claim['checked_date'])
        if claim['status'] not in ('verified_official_guidance', 'unresolved', 'unverified'):
            raise InputError('Unknown verification status')
        if any(s not in sources for s in claim['source_ids']):
            raise InputError('Unknown claim source')
    claim_map = {c['claim_id']: c for c in claims}
    unique(payload['rule_review'], 'rule_key', 'rule review key')
    rule_rows = {r['rule_key']: r for r in rows.get('eligibility_rules', [])}
    for rule in payload['rule_review']:
        if rule['enabled'] is not False:
            raise InputError('Draft rules must remain disabled')
        if rule['rule_key'] not in rule_rows:
            raise InputError('Rule review lacks database mapping')
        if rule_rows[rule['rule_key']]['node_type'] == 'predicate' and not rule['claim_ids']:
            raise InputError('Predicate needs a verified supporting claim')
        for claim_id in rule['claim_ids']:
            if claim_id not in claim_map or claim_map[claim_id]['status'] != 'verified_official_guidance':
                raise InputError('Mapped deterministic rule relies on unverified claim')
    if set(rule_rows) != {r['rule_key'] for r in payload['rule_review']}:
        raise InputError('Every rule requires explicit disabled review metadata')
    for record in rows.get('eligibility_rules', []):
        if record['node_type'] == 'predicate':
            if not record.get('attribute') or record.get('operator') not in ('eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'exists') or record.get('expected_value') is None:
                raise InputError('Invalid predicate shape')
            if not any(e['rule_id'] == record['id'] for e in rows.get('rule_evidence', [])):
                raise InputError('Predicate needs evidence')
        if record.get('parent_id') is not None:
            parent = next((p for p in rows['eligibility_rules'] if p['id'] == record['parent_id']), None)
            if parent is None or parent['scheme_version_id'] != record['scheme_version_id']:
                raise InputError('Invalid rule parent/version')
    for version in rows.get('scheme_versions', []):
        rules = [r for r in rows.get('eligibility_rules', []) if r['scheme_version_id'] == version['id']]
        if rules and len([r for r in rules if r.get('parent_id') is None]) != 1:
            raise InputError('Rule tree requires exactly one root')
        for rule in rules:
            seen, current = set(), rule
            while current.get('parent_id'):
                if current['id'] in seen:
                    raise InputError('Rule tree cycle')
                seen.add(current['id'])
                current = next(r for r in rules if r['id'] == current['parent_id'])
            children = sum(r.get('parent_id') == rule['id'] for r in rules)
            if (rule['node_type'] == 'predicate' and children != 0 or rule['node_type'] == 'not' and children != 1
                    or rule['node_type'] in ('and', 'or') and children == 0):
                raise InputError('Invalid rule arity')
    return payload


def build_verified_draft(manifest, ledger, ledger_dir):
    ledger = deepcopy(ledger)
    records = [r['original_record'] for r in manifest['records']]
    validate_records(records, manifest['source_register'])
    matches = [r for r in records if r['scheme_id'] == ledger['external_scheme_id']]
    if len(matches) != 1:
        raise InputError('Expected exactly one existing scheme')
    if digest(encode(matches[0])) != ledger['input_record_sha256']:
        raise InputError('Verification ledger is bound to a different source record')
    attachments = []
    for source in ledger['sources']:
        if not source.get('snapshot'):
            continue
        snapshot = source['snapshot']
        relative = Path(snapshot['artifact_path'])
        base = ledger_dir.resolve()
        path = (base / relative).resolve()
        if relative.is_absolute() or not path.is_relative_to(base):
            raise InputError('Unsafe snapshot path')
        if path.stat().st_size > 3_000_000:
            raise InputError('Snapshot size limit')
        data = path.read_bytes()
        if digest(data) != snapshot['content_sha256']:
            raise InputError('Source snapshot hash mismatch')
        datetime.fromisoformat(snapshot['fetched_at'])
        if source.get('reuse_status') != 'attribution_permitted':
            raise InputError('Snapshot reuse not established')
        attachments.append({'source_id': source['source_id'], 'bytes': data,
                            'sha256': digest(data), 'extension': path.suffix})
    payload = {'mode': 'local_draft_only', 'publish_allowed': False, 'eligible_for_execution': False, 'database_operations': [],
               'provisional_identifiers': True, 'manifest_sha256': digest(encode(manifest)),
               'ledger_sha256': digest(encode(ledger)), 'external_scheme_id': ledger['external_scheme_id'],
               'original_record': matches[0], 'archive_source_register': manifest['source_register'],
               'unresolved_archive_conflicts': matches[0]['conflicts'],
               'verification': {k: v for k, v in ledger.items() if k not in ('rows', 'rule_review', 'bilingual_content')},
               'rows': ledger['rows'], 'rule_review': ledger['rule_review'],
               'bilingual_content': ledger['bilingual_content'],
               'blockers': ledger['blockers']}
    snapshots = payload['rows'].get('source_snapshots', [])
    for snapshot in snapshots:
        if snapshot['content_sha256'] not in {a['sha256'] for a in attachments}:
            raise InputError('Database snapshot has no captured bytes')
        source_row = next((s for s in payload['rows'].get('official_sources', []) if s['id'] == snapshot['source_id']), None)
        original = next((s['snapshot'] for s in ledger['sources'] if s.get('snapshot')
                         and source_row and s['url'] == source_row['original_url']), None)
        if not original or original['content_sha256'] != snapshot['content_sha256'] or original['fetched_at'] != snapshot['fetched_at']:
            raise InputError('Snapshot source URL/hash/time attribution mismatch')
        snapshot['artifact_path'] = 'snapshots/' + snapshot['content_sha256'] + '.bin'
    validate_draft(payload)
    return payload, attachments


def prepare_verified(manifest_path, ledger_path, output_root):
    manifest = parse_json(manifest_path.read_bytes())
    ledger = parse_json(ledger_path.read_bytes())
    payload, attachments = build_verified_draft(manifest, ledger, ledger_path.parent)
    for p in (output_root.absolute(), *output_root.absolute().parents):
        if p.is_symlink() or p.exists() and p.is_junction():
            raise InputError('Output links are forbidden')
    output_root.mkdir(parents=True, exist_ok=True)
    target = output_root / digest(encode(payload))[:16]
    target.mkdir(exist_ok=False)
    (target / 'draft.json').write_bytes(encode(payload))
    (target / 'snapshots').mkdir()
    saved = set()
    for attachment in attachments:
        if attachment['sha256'] not in saved:
            (target / 'snapshots' / (attachment['sha256'] + '.bin')).write_bytes(attachment['bytes'])
            saved.add(attachment['sha256'])
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, default=ENGINE / '.phase3-output/phase3b')
    parser.add_argument('--dry-run', action='store_true', required=True)
    args = parser.parse_args(argv)
    try:
        target = prepare_verified(args.manifest, args.ledger, args.output_root)
    except (InputError, OSError, KeyError, ValueError, TypeError) as exc:
        print('Verification preparation rejected:', type(exc).__name__)
        return 1
    print('Validated local draft:', target)
    print('No database connection, write or publication performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
