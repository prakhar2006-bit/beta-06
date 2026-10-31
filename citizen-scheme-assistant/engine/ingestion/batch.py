"""Offline collection preparation using the existing single-scheme verifier."""
import argparse
from pathlib import Path
import re

from ingestion.prepare import InputError, digest, encode, parse_json
from ingestion.verification import prepare_verified
from ingestion.staging_validate import validate_bundle


def prepare_collection(manifest_path, ledger_paths, output_root):
    ledgers = [(path, parse_json(path.read_bytes())) for path in ledger_paths]
    ids = [ledger['external_scheme_id'].lower() for _, ledger in ledgers]
    if not ids or len(ids) > 100 or len(ids) != len(set(ids)):
        raise InputError('Expected 1–100 unique stable scheme identifiers')
    # Existing verifier owns all preparation/content checks; collection adds no facts.
    index_rows = []
    for path, ledger in sorted(ledgers, key=lambda item: item[1]['external_scheme_id']):
        stable_id = ledger['external_scheme_id'].lower()
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', stable_id):
            raise InputError('Invalid stable identifier')
        target = prepare_verified(manifest_path, path, output_root / 'schemes' / stable_id)
        draft = target / 'draft.json'
        bundle = validate_bundle(draft)
        if bundle['payload']['rows']['schemes'][0]['stable_id'] != stable_id:
            raise InputError('Ledger and mapped stable identifier disagree')
        index_rows.append({'stable_id': stable_id, 'path': draft.relative_to(output_root).as_posix(),
                           'sha256': digest(draft.read_bytes())})
    index = {'mode': 'local_draft_collection', 'publish_allowed': False, 'schemes': index_rows}
    with (output_root / 'collection.json').open('xb') as stream:
        stream.write(encode(index))
    return output_root / 'collection.json'


def validate_collection(path):
    index = parse_json(path.read_bytes())
    if index.get('mode') != 'local_draft_collection' or index.get('publish_allowed') is not False:
        raise InputError('Only local draft collections supported')
    entries = index['schemes']
    if not 1 <= len(entries) <= 100 or len({e['stable_id'] for e in entries}) != len(entries):
        raise InputError('Duplicate/empty/oversized collection')
    bundles = []
    for entry in sorted(entries, key=lambda e: e['stable_id']):
        relative = Path(entry['path'])
        draft = (path.parent / relative).resolve()
        if relative.is_absolute() or not draft.is_relative_to(path.parent.resolve()):
            raise InputError('Unsafe collection path')
        if digest(draft.read_bytes()) != entry['sha256']:
            raise InputError('Collection draft checksum mismatch')
        bundle = validate_bundle(draft)
        if bundle['payload']['rows']['schemes'][0]['stable_id'] != entry['stable_id']:
            raise InputError('Collection stable identifier mismatch')
        bundles.append(bundle)
    return bundles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--ledger', type=Path, action='append')
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--validate', type=Path)
    args = parser.parse_args()
    if args.validate:
        print(encode(validate_collection(args.validate)).decode('utf-8'))
    elif args.manifest and args.ledger and args.output_root:
        print(prepare_collection(args.manifest, args.ledger, args.output_root))
    else:
        parser.error('Specify --validate or --manifest, repeated --ledger and --output-root')
