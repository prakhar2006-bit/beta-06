import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import net from 'node:net';
import tls from 'node:tls';
import { createLocalStaging, loadBundle } from './staging-import.mjs';

const engine = fileURLToPath(new URL('../', import.meta.url));
let root, draft, payload;
before(async () => {
  root = await mkdtemp(join(tmpdir(), 'scheme-staging-'));
  const python = resolve(engine, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
  const script = `import sys
from pathlib import Path
sys.path.insert(0, 'tests')
from test_verification import fixture
from ingestion.verification import prepare_verified
from ingestion.prepare import encode
p=Path(sys.argv[1]); m,l,b=fixture()
(p/'source.txt').write_bytes(b)
(p/'manifest.json').write_bytes(encode(m))
(p/'ledger.json').write_bytes(encode(l))
print(prepare_verified(p/'manifest.json',p/'ledger.json',p/'output')/'draft.json')`;
  const result = spawnSync(python, ['-c', script, root], { cwd: engine, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  draft = result.stdout.trim();
  payload = JSON.parse(await readFile(draft, 'utf8'));
});
after(async () => { await rm(root, { recursive: true }); });
async function changed(mutator) {
  const copy = structuredClone(payload); mutator(copy);
  const path = join(dirname(draft), 'changed.json');
  await writeFile(path, JSON.stringify(copy));
  return loadBundle(path);
}
async function isolated(fn) {
  const s = await createLocalStaging();
  try { await fn(s); } finally { await s.close(); }
}
const count = async (s, table) => Number((await s.db.query(`SELECT count(*) AS n FROM ${table}`)).rows[0].n);

test('default dry-run rolls back all catalogue rows and receipts', () => isolated(async s => {
  assert.equal((await s.importDraft(loadBundle(draft))).outcome, 'dry_run_rolled_back');
  assert.equal(await count(s, 'scheme_catalog.organizations'), 0);
  assert.equal(await count(s, 'scheme_catalog.ingestion_runs'), 0);
  assert.equal(await count(s, 'local_rehearsal.receipts'), 0);
}));
test('local success, repeat idempotency, provenance and full conflict sidecar preservation', () => isolated(async s => {
  const b = loadBundle(draft);
  assert.equal((await s.importDraft(b, { commitLocal: true })).outcome, 'imported_local');
  assert.equal((await s.importDraft(b, { commitLocal: true })).outcome, 'already_imported');
  assert.equal(await count(s, 'scheme_catalog.scheme_versions'), 1);
  assert.equal(await count(s, 'scheme_catalog.ingestion_runs'), 1);
  const receipt = (await s.db.query('SELECT payload FROM local_rehearsal.receipts')).rows[0].payload;
  assert.deepEqual(receipt, payload);
  assert.equal((await s.db.query('SELECT original_url FROM scheme_catalog.official_sources')).rows[0].original_url, payload.rows.official_sources[0].original_url);
  assert.equal(await count(s, 'scheme_catalog.published_versions'), 0);
  assert.equal((await s.db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows[0].status, 'draft');
  assert.ok(receipt.rule_review.every(r => r.enabled === false));
}));
test('late SQL constraint failure rolls back shared rows and receipts', () => isolated(async s => {
  const b = await changed(p => p.rows.rule_evidence.push({ ...p.rows.rule_evidence[0], id: 'aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa' }));
  await assert.rejects(s.importDraft(b, { commitLocal: true }));
  assert.equal(await count(s, 'scheme_catalog.organizations'), 0);
  assert.equal(await count(s, 'scheme_catalog.scheme_versions'), 0);
  assert.equal(await count(s, 'local_rehearsal.receipts'), 0);
  assert.equal((await s.importDraft(loadBundle(draft), { commitLocal: true })).outcome, 'imported_local');
}));
test('invalid source reference fails before any import', async () => {
  await assert.rejects(changed(p => p.rows.evidence[0].snapshot_id = 'aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa'), /validation failed/);
});
test('lost conflicts, changed snapshot attribution and corrupted captured bytes are rejected', async () => {
  await assert.rejects(changed(p => p.unresolved_archive_conflicts = ['Lost original assertions']));
  await assert.rejects(changed(p => p.rows.source_snapshots[0].fetched_at = '2020-01-01T00:00:00+00:00'));
  const artifact = join(dirname(draft), payload.rows.source_snapshots[0].artifact_path);
  const bytes = await readFile(artifact);
  try {
    await writeFile(artifact, 'Corrupted capture');
    assert.throws(() => loadBundle(draft), /validation failed/);
  } finally { await writeFile(artifact, bytes); }
});
test('version conflict rejects stale preview; explicit new version preserves previous rows', () => isolated(async s => {
  await s.importDraft(loadBundle(draft), { commitLocal: true });
  const b = await changed(p => p.blockers.push('Additional review note'));
  await assert.rejects(s.importDraft(b, { commitLocal: true }), /Version conflict/);
  assert.equal(await count(s, 'scheme_catalog.scheme_versions'), 1);
  assert.equal((await s.importDraft(b, { commitLocal: true, expectedVersion: 1 })).versionNumber, 2);
  assert.equal(await count(s, 'scheme_catalog.official_sources'), 1);
  assert.equal(await count(s, 'scheme_catalog.evidence'), 1);
  assert.equal(await count(s, 'scheme_catalog.published_versions'), 0);
}));
test('existing natural-key identifier remapping and conflicting content rejection', () => isolated(async s => {
  const org = payload.rows.organizations[0];
  const id = 'bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb';
  await s.db.query('INSERT INTO scheme_catalog.organizations(id,code,name,government_level,official_url) VALUES ($1,$2,$3,$4,$5)', [id, org.code, org.name, org.government_level, org.official_url]);
  await s.importDraft(loadBundle(draft), { commitLocal: true });
  assert.equal(await count(s, 'scheme_catalog.organizations'), 1);
  assert.equal((await s.db.query('SELECT organization_id FROM scheme_catalog.schemes')).rows[0].organization_id, id);
  const b = await changed(p => p.rows.organizations[0].name = 'Conflicting name');
  await assert.rejects(s.importDraft(b, { commitLocal: true, expectedVersion: 1 }), /Existing content conflict/);
}));
test('published/enabled input and mutated imported content cannot be silently accepted', () => isolated(async s => {
  await assert.rejects(changed(p => p.rows.scheme_versions[0].status = 'published'));
  await assert.rejects(changed(p => p.rule_review[0].enabled = true));
  const b = loadBundle(draft);
  await s.importDraft(b, { commitLocal: true });
  await s.db.query("UPDATE scheme_catalog.eligibility_rules SET uncertainty_reason='Changed externally'");
  await assert.rejects(s.importDraft(b, { commitLocal: true }), /content drift/);
}));
test('local-only implementation ignores credentials and performs no network access', async () => {
  const originals = [net.connect, net.createConnection, tls.connect, globalThis.fetch];
  const forbidden = () => { throw new Error('Network forbidden'); };
  const previous = process.env.DATABASE_URL;
  process.env.DATABASE_URL = 'postgresql://scheme_api:synthetic@invalid.invalid/test';
  net.connect = net.createConnection = tls.connect = globalThis.fetch = forbidden;
  try {
    await isolated(async s => {
      await s.importDraft(loadBundle(draft), { commitLocal: true });
      await assert.rejects(s.importDraft({ payload }), /loadBundle/);
    });
  } finally {
    [net.connect, net.createConnection, tls.connect, globalThis.fetch] = originals;
    if (previous === undefined) delete process.env.DATABASE_URL; else process.env.DATABASE_URL = previous;
  }
});
