"""Safely audit an archive and produce a non-executable, unpublished manifest."""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import unicodedata
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

VERSION = 'phase3-preparation-1'
MAX_ARCHIVE = 50 * 1024 * 1024
MAX_FILE = 10 * 1024 * 1024
MAX_ENTRIES = 1000
SCRIPTS = {'.py', '.ps1', '.sh', '.bat', '.cmd', '.js', '.vbs'}
EXECUTABLES = {'.exe', '.dll', '.com', '.msi', '.scr', '.lnk'}
ACTIVE = 'output/batch_001/'


class InputError(ValueError):
    pass


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')


def safe_name(name: str) -> str:
    if not name or any(c in name for c in '\\:<>"|?*') or any(ord(c) < 32 for c in name):
        raise InputError('Unsafe archive path')
    if name.startswith('/') or any(p in ('', '.', '..') for p in name.rstrip('/').split('/')):
        raise InputError('Unsafe archive path')
    for part in PurePosixPath(name).parts:
        if part.endswith((' ', '.')) or re.match(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)', part, re.I):
            raise InputError('Unsafe Windows archive path')
    return unicodedata.normalize('NFC', name.rstrip('/')).casefold()


def parse_json(data: bytes):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError('Duplicate JSON object key')
            result[key] = value
        return result
    try:
        return json.loads(data.decode('utf-8-sig'), object_pairs_hook=pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(InputError('Non-finite JSON number')))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError('Malformed JSON: ' + type(exc).__name__) from None


def inspect_archive(data: bytes, label='', depth=0, budget=None):
    if len(data) > MAX_ARCHIVE or depth > 2:
        raise InputError('Archive size/depth limit exceeded')
    budget = budget if budget is not None else {'bytes': 0, 'entries': 0}
    inventory, files = [], {}
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            seen = set()
            # Preflight the complete directory before decompressing any entry.
            for info in archive.infolist():
                canonical = safe_name(info.filename)
                if canonical in seen:
                    raise InputError('Duplicate/case-colliding archive path')
                seen.add(canonical)
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode) or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise InputError('Archive links/special files are forbidden')
                if info.flag_bits & 1 or info.file_size > MAX_FILE or info.file_size > max(info.compress_size, 1) * 200:
                    raise InputError('Encrypted/oversized/high-ratio entry')
                if PurePosixPath(info.filename).suffix.lower() in EXECUTABLES:
                    raise InputError('Executable binary entry rejected')
                budget['bytes'] += info.file_size
                budget['entries'] += 1
                if budget['bytes'] > MAX_ARCHIVE or budget['entries'] > MAX_ENTRIES:
                    raise InputError('Expanded archive budget exceeded')
            for info in archive.infolist():
                entry = {'path': label + info.filename, 'bytes': info.file_size, 'compressed_bytes': info.compress_size,
                         'directory': info.is_dir(), 'quarantined': PurePosixPath(info.filename).suffix.lower() in SCRIPTS}
                inventory.append(entry)
                if info.is_dir():
                    continue
                # ZipFile.read verifies CRC; directory sizes were bounded above.
                contents = archive.read(info)
                entry['sha256'] = digest(contents)
                files[info.filename] = contents
                if info.filename.lower().endswith('.zip'):
                    child, _ = inspect_archive(contents, label + info.filename + '!/', depth + 1, budget)
                    inventory.extend(child)
    except (BadZipFile, RuntimeError, NotImplementedError, EOFError) as exc:
        raise InputError('Unreadable/corrupt ZIP: ' + type(exc).__name__) from None
    return inventory, files


def parse_artifacts(files: dict[str, bytes]):
    parsed, inventory = {}, []
    for path, contents in sorted(files.items()):
        suffix = PurePosixPath(path).suffix.lower()
        row = {'path': path, 'sha256': digest(contents), 'bytes': len(contents)}
        if suffix == '.json':
            parsed[path] = parse_json(contents)
            row['format'] = 'json'
        elif suffix == '.csv':
            try:
                rows = list(csv.reader(io.StringIO(contents.decode('utf-8-sig'), newline=''), strict=True))
                rows = [r for r in rows if r]  # CRCRLF produces blank physical lines.
                if not rows or len(set(rows[0])) != len(rows[0]) or any(len(r) != len(rows[0]) for r in rows[1:]):
                    raise InputError('CSV header/row width mismatch')
                for values in rows[1:]:
                    for cell in values:
                        if cell.lstrip().startswith(('[', '{')):
                            parse_json(cell.encode('utf-8'))
                row.update(format='csv', rows=len(rows) - 1, columns=rows[0])
            except (UnicodeError, csv.Error):
                raise InputError('Malformed CSV') from None
        elif suffix in ('.md', '.txt'):
            try:
                contents.decode('utf-8-sig')
            except UnicodeError:
                raise InputError('Malformed UTF-8 text') from None
            row['format'] = 'text'
        inventory.append(row)
    return parsed, inventory


def walk(value, path='$'):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, path + '.' + key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f'{path}[{index}]')


def official_host(url):
    try:
        host = (urlsplit(url).hostname or '').lower()
        return host.endswith(('.gov.in', '.nic.in'))
    except ValueError:
        return False


def validate_records(records, sources):
    if not isinstance(records, list) or not isinstance(sources, list):
        raise InputError('Records and sources must be arrays')
    source_map = {}
    for source in sources:
        if not isinstance(source, dict) or not all(isinstance(source.get(k), str) and source[k].strip() for k in ('source_id', 'url', 'title', 'publisher')):
            raise InputError('Malformed source row')
        if source['source_id'] in source_map:
            raise InputError('Duplicate source identifier')
        parsed = urlsplit(source['url'])
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            raise InputError('Unsafe source URL')
        source_map[source['source_id']] = source
    seen = set()
    arrays = ('source_ids', 'discovery_evidence', 'benefits', 'eligibility_conditions', 'exclusions', 'documents',
              'guidelines', 'translations', 'missing_information', 'conflicts', 'unresolved_questions')
    required_text = ('scheme_id', 'official_name', 'classification', 'jurisdiction', 'record_stage')
    for record in records:
        if not isinstance(record, dict) or not all(isinstance(record.get(k), str) and record[k].strip() for k in required_text):
            raise InputError('Missing required record identity fields')
        key = record['scheme_id'].casefold()
        if key in seen:
            raise InputError('Duplicate scheme identifier')
        seen.add(key)
        if record['classification'] not in ('central', 'state', 'ut', 'local'):
            raise InputError('Invalid government classification')
        if not re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', record['scheme_id']):
            raise InputError('Unsafe scheme identifier')
        if not all(isinstance(record.get(k), list) for k in arrays) or not isinstance(record.get('application'), dict):
            raise InputError('Missing or malformed record collections')
        if any(s not in source_map for s in record['source_ids']):
            raise InputError('Unknown source identifier')
        for name in ('benefits', 'exclusions', 'documents', 'conflicts', 'translations', 'guidelines', 'discovery_evidence'):
            if not all(isinstance(item, dict) for item in record[name]):
                raise InputError('Record collection must contain objects: ' + name)
        for name in ('benefits', 'documents', 'exclusions'):
            if not all(isinstance(item.get('text'), str) and item['text'].strip() for item in record[name]):
                raise InputError('Missing source assertion text: ' + name)
        rule_ids = set()
        for rule in record['eligibility_conditions']:
            if not isinstance(rule, dict) or not all(isinstance(rule.get(k), str) and rule[k].strip() for k in ('rule_id', 'text')):
                raise InputError('Malformed eligibility condition')
            if rule['rule_id'] in rule_ids:
                raise InputError('Duplicate rule identifier')
            rule_ids.add(rule['rule_id'])
            for key in ('field', 'operator'):
                if key in rule and rule[key] is not None and not isinstance(rule[key], str):
                    raise InputError('Malformed structured rule attribute')
            if 'evidence' in rule and not isinstance(rule['evidence'], list):
                raise InputError('Malformed rule evidence')
        for path, item in walk(record):
            if 'source_id' in item:
                required = ('url',) if path.startswith('$.guideline_metadata[') else ('url', 'locator')
                if item['source_id'] not in source_map or not all(isinstance(item.get(k), str) and item[k].strip() for k in required):
                    raise InputError('Incomplete citation at ' + path)
                if item['url'] != source_map[item['source_id']]['url']:
                    raise InputError('Citation URL differs from source register at ' + path)
    return source_map


def classify_condition(rule, record):
    operator = rule.get('operator')
    value = rule.get('value')
    numeric = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    valid_value = (operator in ('=', '!=') and isinstance(value, (str, int, float, bool))
                   or operator in ('<', '<=', '>', '>=') and numeric(value)
                   or operator == 'inclusive_range' and isinstance(value, list)
                   and len(value) == 2 and all(numeric(v) for v in value) and value[0] <= value[1])
    structured = (bool(rule.get('field')) and 'value' in rule
                  and valid_value)
    ambiguous = operator == 'range_as_worded' or any(
        word in (rule.get('reference_date') or '').lower() for word in ('not specified', 'not stated', 'not collected'))
    category = ('ambiguous_or_conflicting' if ambiguous or record.get('conflicts') else
                'machine_evaluable_after_review' if structured else 'human_verification_required')
    return {'rule_id': rule['rule_id'], 'category': category, 'enabled': False,
            'mechanically_representable_after_review': structured and not ambiguous,
            'confidence': 'UNCERTAIN', 'requires_additional_citizen_information': True,
            'citizen_attribute': rule.get('field'), 'operator_as_supplied': operator,
            'value_as_supplied': rule.get('value'), 'currency': rule.get('currency'),
            'period': rule.get('period'), 'scope': rule.get('scope'), 'reference_date': rule.get('reference_date'),
            'source_assertion': rule, 'record_conflicts_require_review': bool(record.get('conflicts')),
            'uncertainty_reason': 'Source assertions and amendment chain require human verification; no eligibility execution permitted.'}


def build_manifest(records, sources, archive_hash, artifacts, inventory):
    validate_records(records, sources)
    prepared = []
    for record in sorted(records, key=lambda r: r['scheme_id']):
        detailed = bool(record['eligibility_conditions'] and record['benefits'] and record['guidelines'])
        missing = list(record['missing_information'])
        if not record.get('description'):
            missing.append('No explicit scheme description field; intended_beneficiaries is not a substitute.')
        if not record.get('official_hindi_name'):
            missing.append('Hindi name missing.')
        missing.extend(['English/Hindi description and eligibility translations are not established.',
                        'Original source-document byte snapshots and current access/reuse permission not established.',
                        'Human verification and reviewed publication prerequisites outstanding.'])
        conditions = [classify_condition(rule, record) for rule in record['eligibility_conditions']]
        incomplete = [rule['rule_id'] for rule in record['eligibility_conditions']
                      if not rule.get('evidence') or not rule.get('original_source_wording')
                      or not rule.get('field') or not rule.get('operator') or 'value' not in rule]
        normalized = record['scheme_id'].lower()
        prepared.append({'external_scheme_id': record['scheme_id'], 'proposed_stable_id': normalized,
            'record_sha256': digest(encode(record)),
            'readiness': 'detailed_draft_requiring_verification' if detailed else 'discovery_only',
            'target_status': 'draft', 'publish_allowed': False, 'eligible_for_execution': False,
            'original_record': record, 'missing_information': missing,
            'conflicts_preserved': record['conflicts'], 'condition_proposals': conditions,
            'incomplete_condition_ids': incomplete,
            'language_availability': {'english_name': bool(record['official_name']),
                'hindi_name': bool(record.get('official_hindi_name')), 'hindi_name_role': record.get('hindi_name_evidence'),
                'translations_as_supplied': record['translations']},
            'proposed_questions': [{'question_id': c['rule_id'], 'prompt_source_text': c['source_assertion']['text'],
                'question_template_en': question_template(c['citizen_attribute']),
                'template_is_official_translation': False,
                'field': c['citizen_attribute'], 'answer_type': 'review_required', 'enabled': False,
                'evidence': c['source_assertion'].get('evidence', []), 'requires_human_review': True} for c in conditions]})
    candidates = sorted([r for r in prepared if r['readiness'].startswith('detailed')],
                        key=lambda r: (len(r['conflicts_preserved']), r['external_scheme_id']))[:5]
    official = [s for s in sources if official_host(s['url'])]
    references = [item for record in records for _, item in walk(record)
                  if all(k in item for k in ('source_id', 'url', 'locator'))]
    counts = Counter(r['readiness'] for r in prepared)
    return {'tool_version': VERSION, 'mode': 'dry_run_only', 'database_operations': [],
        'archive_sha256': archive_hash, 'archive_inventory': inventory, 'artifact_inventory': artifacts,
        'source_register': sources, 'records': prepared,
        'summary': {'schemes': len(prepared), 'detailed_drafts': counts['detailed_draft_requiring_verification'],
            'discovery_only': counts['discovery_only'], 'publication_ready': 0, 'human_review_required': len(prepared),
            'source_register_rows': len(sources), 'unique_source_urls': len({s['url'] for s in sources}),
            'official_host_source_rows': len(official), 'official_host_unique_urls': len({s['url'] for s in official}),
            'citation_occurrences': len(references),
            'official_host_citation_occurrences': sum(official_host(r['url']) for r in references),
            'conflicts': sum(len(r['conflicts_preserved']) for r in prepared),
            'conditions': sum(len(r['condition_proposals']) for r in prepared),
            'missing_hindi_names': sum(not r['language_availability']['hindi_name'] for r in prepared)},
        'best_five_for_review': [r['external_scheme_id'] for r in candidates],
        'warnings': ['Archive statuses are untrusted; zero records approved for publication.',
                     'Artifact hashes authenticate local files only, not government source documents.',
                     'Official-domain classification is a hostname heuristic, not source authentication.',
                     'All original assertions and unknown fields retained; no translations or thresholds invented.']}


def question_template(field):
    # Generic proposed UX prompts, not new scheme rules or official translations.
    return {'age_years': 'What is the applicant age in years at the reviewed reference date?',
            'income': 'What is the applicant income for the reviewed currency, period and person/household scope?',
            'employment_category': 'What is the applicant employment category?',
            'enrolment_accounts': 'How many accounts are enrolled in this scheme?',
            'bpl_status': 'Has household BPL status been established under the applicable official process?',
            'bpl_list_omission': 'Is the household missing from the applicable BPL list?'
            }.get(field, 'Reviewer must define a question and evidence requirements for this source assertion.')


def prepare(archive_path: Path, output_root: Path):
    if archive_path.stat().st_size > MAX_ARCHIVE:
        raise InputError('Archive too large')
    data = archive_path.read_bytes()
    inventory, files = inspect_archive(data)
    parsed, artifacts = parse_artifacts(files)
    # Parse and check nested copies as historical artifacts, never merge schemes.
    nested_checks = []
    for path, contents in sorted(files.items()):
        if path.endswith('.zip'):
            _, nested_files = inspect_archive(contents)
            _, nested_artifacts = parse_artifacts(nested_files)
            nested_checks.append({'path': path, 'files': len(nested_files), 'artifacts': nested_artifacts})
    required = [ACTIVE + n for n in ('scheme_records.json', 'sources.json', 'detailed_scheme_records.json', 'record_schema.json')]
    if any(n not in parsed for n in required):
        raise InputError('Expected one current output/batch_001 dataset; do not guess another batch')
    records_doc = parsed[required[0]]
    if not isinstance(records_doc, dict) or not isinstance(records_doc.get('records'), list):
        raise InputError('Invalid records envelope')
    records = records_doc['records']
    source_rows = parsed[required[1]]
    validate_records(records, source_rows)
    detailed = parsed[required[2]]
    if not isinstance(detailed, dict) or not isinstance(detailed.get('records'), list):
        raise InputError('Invalid detailed records envelope')
    current = {r['scheme_id']: r for r in records}
    for record in detailed['records']:
        if current.get(record.get('scheme_id')) != record:
            raise InputError('Detailed subset differs from canonical record; reconcile rather than overwrite')
    schema = parsed[required[3]]
    if not isinstance(schema, dict) or not isinstance(schema.get('required'), list):
        raise InputError('Invalid archival schema')
    for record in records:
        if any(k not in record for k in schema['required']):
            raise InputError('Archive schema required field missing')
    artifact_manifest = parsed.get(ACTIVE + 'artifact_manifest.json', {})
    for row in artifact_manifest.get('files', []):
        path = ACTIVE + row['name']
        if path not in files or digest(files[path]) != row['sha256'] or len(files[path]) != row['bytes']:
            raise InputError('Artifact manifest checksum mismatch')
    manifest = build_manifest(records, source_rows, digest(data), artifacts, inventory)
    manifest['nested_archive_checks'] = nested_checks
    manifest['batch_metadata'] = {k: v for k, v in records_doc.items() if k != 'records'}
    manifest['validation_scope'] = 'Independent structural checks and archival required-key checks; not a full JSON Schema evaluator or factual verification.'
    # Preserve ALL auxiliary evidence/review/identity/coverage data, not just selected rows.
    manifest['supporting_artifacts'] = {k: v for k, v in parsed.items() if k != required[0]}
    for ancestor in (output_root.absolute(), *output_root.absolute().parents):
        if ancestor.is_symlink() or (ancestor.exists() and ancestor.is_junction()):
            raise InputError('Output path cannot contain links/junctions')
    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    destination = root / digest(data)[:16]
    # Exclusive directory prevents overwriting any existing project or prior run.
    destination.mkdir(exist_ok=False)
    for path, contents in sorted(files.items()):
        quarantine = PurePosixPath(path).suffix.lower() in SCRIPTS
        target = destination / ('quarantine' if quarantine else 'extracted') / path
        if quarantine:
            target = target.with_name(target.name + '.disabled')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as handle:
            handle.write(contents)
    (destination / 'manifest.json').write_bytes(encode(manifest))
    (destination / 'readiness.json').write_bytes(encode({k: manifest[k] for k in ('summary', 'best_five_for_review', 'warnings')}))
    return destination, manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, default=Path(__file__).resolve().parents[1] / '.phase3-output')
    parser.add_argument('--dry-run', action='store_true', required=True, help='Required; database execution does not exist')
    args = parser.parse_args(argv)
    try:
        destination, manifest = prepare(args.archive, args.output_root)
    except (InputError, OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print('Preparation rejected:', str(exc))
        return 1
    print(json.dumps({'output': str(destination), 'summary': manifest['summary']}, ensure_ascii=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
