import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import net from 'node:net';
import tls from 'node:tls';
import { createLocalStaging, loadBundle, loadCollection } from './staging-import.mjs';

const engine = fileURLToPath(new URL('../', import.meta.url));
let root, paths, bundles, collection;
before(async () => {
  root = await mkdtemp(join(tmpdir(), 'scheme-batch-'));
  const python = resolve(engine, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
  const code = `import sys,json
from pathlib import Path
sys.path.insert(0,'tests')
from test_verification import fixture
from ingestion.verification import prepare_verified
from ingestion.prepare import encode,digest
p=Path(sys.argv[1]);entries=[];paths=[]
for i in range(5):
 d=p/str(i);d.mkdir();m,l,b=fixture()
 m['records'][0]['original_record']['scheme_id']='IN-CEN-90000'+str(i)
 m['records'][0]['original_record']['conflicts']=[{'assertions':['Synthetic A','Synthetic B']}]
 l['external_scheme_id']='IN-CEN-90000'+str(i)
 l['input_record_sha256']=digest(encode(m['records'][0]['original_record']))
 l['rows']['schemes'][0]['stable_id']='test-only-'+str(i)
 (d/'source.txt').write_bytes(b);(d/'manifest.json').write_bytes(encode(m));(d/'ledger.json').write_bytes(encode(l))
 draft=prepare_verified(d/'manifest.json',d/'ledger.json',d/'out')/'draft.json';paths.append(str(draft))
 entries.append({'stable_id':'test-only-'+str(i),'path':draft.relative_to(p).as_posix(),'sha256':digest(draft.read_bytes())})
(p/'collection.json').write_bytes(encode({'mode':'local_draft_collection','publish_allowed':False,'schemes':entries}))
print(json.dumps(paths))`;
  const result = spawnSync(python, ['-c', code, root], { cwd: engine, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr || String(result.error));
  paths = JSON.parse(result.stdout);
  collection = join(root, 'collection.json');
  bundles = loadCollection(collection);
});
after(async () => { await rm(root, { recursive: true }); });
async function isolated(fn) { const s = await createLocalStaging(); try { await fn(s); } finally { await s.close(); } }
const count = async (s,t) => Number((await s.db.query(`SELECT count(*) AS n FROM ${t}`)).rows[0].n);
async function changedLast(mutator) {
  const p = JSON.parse(await readFile(paths[4], 'utf8')); mutator(p);
  const file = join(dirname(paths[4]), 'changed.json');
  await writeFile(file, JSON.stringify(p));
  return [...bundles.slice(0,4), loadBundle(file)];
}

test('five schemes share provenance IDs and preserve conflicts without duplicates', () => isolated(async s => {
  const imported = await s.importBatch(bundles, { commitLocal: true });
  assert.equal(imported.schemes, 5);
  assert.equal(await count(s,'scheme_catalog.schemes'), 5);
  assert.equal(await count(s,'scheme_catalog.organizations'), 1);
  assert.equal(await count(s,'scheme_catalog.official_sources'), 1);
  assert.equal(await count(s,'scheme_catalog.source_snapshots'), 1);
  assert.equal(await count(s,'scheme_catalog.evidence'), 1);
  const repeated = await s.importBatch([...bundles].reverse(), { commitLocal: true });
  assert.equal(repeated.recordsWritten, 0);
  assert.ok(repeated.results.every(r => r.outcome === 'already_imported'));
  assert.equal(await count(s,'scheme_catalog.ingestion_runs'), 5);
  const receipts = (await s.db.query('SELECT payload FROM local_rehearsal.receipts')).rows;
  assert.equal(receipts.length, 5);
  for (const b of bundles) assert.deepEqual(receipts.find(r => r.payload.external_scheme_id === b.payload.external_scheme_id).payload,b.payload);
  assert.ok(receipts.every(r => r.payload.rule_review.every(rule => rule.enabled === false)));
  assert.equal(await count(s,'scheme_catalog.published_versions'), 0);
}));
test('batch dry-run is deterministic across order and leaves no rows', () => isolated(async s => {
  assert.deepEqual(await s.importBatch(bundles), await s.importBatch([...bundles].reverse()));
  assert.equal(await count(s,'scheme_catalog.schemes'), 0);
  assert.equal(await count(s,'local_rehearsal.receipts'), 0);
}));
test('last-scheme constraint failure rolls back all earlier schemes and receipts', () => isolated(async s => {
  const bad = await changedLast(p => p.rows.rule_evidence.push({...p.rows.rule_evidence[0],id:'aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa'}));
  await assert.rejects(s.importBatch(bad, { commitLocal: true }));
  assert.equal(await count(s,'scheme_catalog.organizations'), 0);
  assert.equal(await count(s,'scheme_catalog.scheme_versions'), 0);
  assert.equal(await count(s,'scheme_catalog.ingestion_runs'), 0);
  assert.equal(await count(s,'local_rehearsal.receipts'), 0);
  await s.importBatch(bundles, { commitLocal: true });
  assert.equal(await count(s,'scheme_catalog.schemes'), 5);
}));
test('late version conflict rolls back new schemes and preserves pre-existing draft', () => isolated(async s => {
  await s.importDraft(bundles[4], { commitLocal: true });
  const changed = await changedLast(p => p.blockers.push('Synthetic revised review note'));
  await assert.rejects(s.importBatch(changed, { commitLocal: true }), /Version conflict/);
  assert.equal(await count(s,'scheme_catalog.schemes'), 1);
  assert.equal(await count(s,'scheme_catalog.scheme_versions'), 1);
  assert.equal(await count(s,'local_rehearsal.receipts'), 1);
  await s.importBatch(changed, { commitLocal: true, expectedVersions: {'test-only-4': 1} });
  assert.equal(await count(s,'scheme_catalog.scheme_versions'), 6);
}));
test('duplicate identifiers, invalid references and changed collection hashes are rejected', () => isolated(async s => {
  await assert.rejects(s.importBatch([...bundles, bundles[0]], { commitLocal: true }), /Duplicate/);
  await assert.rejects(changedLast(p => p.rows.evidence[0].snapshot_id='aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa'));
  const index = JSON.parse(await readFile(collection,'utf8'));
  index.schemes[0].sha256 = '0'.repeat(64);
  const path = join(root,'bad-index.json'); await writeFile(path,JSON.stringify(index));
  assert.throws(() => loadCollection(path), /validation failed/);
  assert.equal(await count(s,'scheme_catalog.schemes'), 0);
}));
test('multi-scheme imports cannot activate rules, publish, or access network', async () => {
  await assert.rejects(changedLast(p => p.rule_review[0].enabled=true));
  await assert.rejects(changedLast(p => p.rows.scheme_versions[0].status='published'));
  const original = [net.connect,net.createConnection,tls.connect,globalThis.fetch];
  const forbidden = () => { throw new Error('Network forbidden'); };
  net.connect=net.createConnection=tls.connect=globalThis.fetch=forbidden;
  try {
    await isolated(async s => {
      await s.importBatch(bundles, { commitLocal: true });
      assert.equal(await count(s,'scheme_catalog.published_versions'),0);
      assert.ok((await s.db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows.every(r => r.status==='draft'));
      assert.ok((await s.db.query('SELECT confidence FROM scheme_catalog.eligibility_rules')).rows.every(r => r.confidence==='UNCERTAIN'));
    });
  } finally { [net.connect,net.createConnection,tls.connect,globalThis.fetch]=original; }
});
