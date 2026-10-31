import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import { PGlite } from '@electric-sql/pglite';

// Synthetic constraint fixtures only; these are not government scheme records.
const db = new PGlite();
// Model the built-in Supabase API roles, including default grants from an
// existing environment; the access migration must explicitly remove these.
await db.exec('CREATE ROLE anon; CREATE ROLE authenticated; CREATE ROLE service_role BYPASSRLS');
const migrationDir = new URL('../supabase/migrations/', import.meta.url);
for (const file of (await readdir(migrationDir)).filter(f => f.endsWith('.sql')).sort()) {
  await db.exec(await readFile(new URL(file, migrationDir), 'utf8'));
  if (file.startsWith('20261030000200')) {
    await db.exec('GRANT USAGE ON SCHEMA scheme_catalog TO anon, authenticated, service_role; GRANT ALL ON ALL TABLES IN SCHEMA scheme_catalog TO anon, authenticated, service_role');
  }
}
const id = n => `00000000-0000-4000-8000-${String(n).padStart(12, '0')}`;
const insert = async (table, values) => {
  const keys = Object.keys(values);
  return db.query(`INSERT INTO scheme_catalog.${table} (${keys.join(',')}) VALUES (${keys.map((_, i) => `$${i + 1}`).join(',')})`, Object.values(values));
};
async function fixture() {
  await insert('organizations', { id: id(1), code: 'test-only', name: 'Synthetic test organization', government_level: 'state', official_url: 'https://example.invalid' });
  await insert('jurisdictions', { id: id(2), code: 'TEST', name: 'Synthetic jurisdiction', kind: 'state' });
  await insert('official_sources', { id: id(3), organization_id: id(1), original_url: 'https://example.invalid/test', title: 'Synthetic source', source_kind: 'guideline' });
  await insert('ingestion_runs', { id: id(4), source_id: id(3), idempotency_key: 'fixture-v1', importer_version: 'test' });
  await insert('source_snapshots', { id: id(5), source_id: id(3), ingestion_run_id: id(4), content_sha256: 'a'.repeat(64), media_type: 'text/plain' });
  await insert('evidence', { id: id(6), snapshot_id: id(5), locator: 'test section', supporting_text: 'Synthetic assertion', last_checked_date: '2026-10-30' });
  await insert('schemes', { id: id(7), stable_id: 'synthetic-test', organization_id: id(1), government_level: 'state' });
  await insert('scheme_versions', { id: id(8), scheme_id: id(7), version_number: 1 });
}
async function failure(action, pattern) {
  await db.exec('SAVEPOINT expected_failure');
  await assert.rejects(action, pattern);
  await db.exec('ROLLBACK TO SAVEPOINT expected_failure');
  await db.exec('RELEASE SAVEPOINT expected_failure');
}
async function isolated(body) {
  await db.exec('BEGIN');
  try { await fixture(); await body(); } finally { await db.exec('ROLLBACK'); }
}

test('migrations create 15 UUID-keyed, RLS-protected tables and no records', async () => {
  const { rows } = await db.query("SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'scheme_catalog'");
  assert.equal(rows.length, 15);
  for (const row of rows) {
    assert.equal(row.rowsecurity, true);
    const result = await db.query(`SELECT count(*)::int AS n FROM scheme_catalog.${row.tablename}`);
    assert.equal(result.rows[0].n, 0);
  }
  const keys = await db.query(`SELECT count(*)::int AS n FROM information_schema.columns
    WHERE table_schema = 'scheme_catalog' AND column_name = 'id' AND data_type = 'uuid'
    AND table_name IN (SELECT tablename FROM pg_tables WHERE schemaname = 'scheme_catalog')`);
  assert.equal(keys.rows[0].n, 15);
  await db.exec('CREATE ROLE synthetic_client');
  await db.exec('SET ROLE synthetic_client');
  await assert.rejects(() => db.query('SELECT * FROM scheme_catalog.schemes'), /permission denied/);
  await db.exec('RESET ROLE');
});

test('idempotency keys, hashes, stable identities, FKs and lifecycle constraints', () => isolated(async () => {
  await failure(() => insert('ingestion_runs', { source_id: id(3), idempotency_key: 'fixture-v1', importer_version: 'test' }), /unique/);
  await failure(() => insert('source_snapshots', { source_id: id(3), content_sha256: 'a'.repeat(64), media_type: 'text/plain' }), /unique/);
  await failure(() => insert('scheme_versions', { scheme_id: id(7), version_number: 1 }), /unique/);
  await failure(() => insert('scheme_versions', { scheme_id: id(99), version_number: 2 }), /foreign key/);
  await failure(() => db.query("UPDATE scheme_catalog.schemes SET stable_id = 'changed'"), /identity/);
  await failure(() => db.query("UPDATE scheme_catalog.official_sources SET original_url = 'https://example.invalid/changed'"), /identity/);
  await failure(() => db.query("UPDATE scheme_catalog.ingestion_runs SET status = 'succeeded'"), /check constraint/);
  await failure(() => db.query("UPDATE scheme_catalog.evidence SET supporting_text = 'changed'"), /append-only/);
  await failure(() => db.query("DELETE FROM scheme_catalog.source_snapshots"), /append-only/);
  await db.query("UPDATE scheme_catalog.ingestion_runs SET status = 'succeeded', finished_at = now()");
}));

test('benefit amounts, application URLs, document conditions and language constraints', () => isolated(async () => {
  const common = { scheme_version_id: id(8), item_key: 'test', evidence_id: id(6) };
  await failure(() => insert('benefits', { ...common, benefit_type: 'synthetic', description: 'Test only', amount_min: 20, amount_max: 10, currency: 'INR' }), /check constraint/);
  await failure(() => insert('benefits', { ...common, benefit_type: 'synthetic', description: 'Test only', amount_min: 10 }), /check constraint/);
  await failure(() => insert('application_routes', { ...common, mode: 'online', instructions: 'Test only', last_checked_date: '2026-10-30' }), /check constraint/);
  await failure(() => insert('required_documents', { ...common, document_type: 'Synthetic', requirement: 'conditional' }), /check constraint/);
  await failure(() => insert('translations', { scheme_version_id: id(8), language_code: 'xx', title: 'Test', summary: 'Test only', translation_origin: 'human', evidence_id: id(6) }), /check constraint/);
  await insert('required_documents', { ...common, document_type: 'Synthetic', requirement: 'unknown' });
}));

test('rule typing, cross-version parents, cycles and NOT arity', () => isolated(async () => {
  const rule = { scheme_version_id: id(8), rule_key: 'test', node_type: 'predicate', attribute: 'synthetic_value', operator: 'gte', expected_value: '10', confidence: 'VERIFIED' };
  await failure(() => insert('eligibility_rules', { ...rule, expected_value: '"ten"' }), /check constraint/);
  await failure(() => insert('eligibility_rules', { ...rule, confidence: 'UNCERTAIN' }), /check constraint/);
  await insert('scheme_versions', { id: id(9), scheme_id: id(7), version_number: 2 });
  await insert('eligibility_rules', { ...rule, id: id(10) });
  await failure(async () => {
    await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
    await insert('eligibility_rules', { ...rule, scheme_version_id: id(9), parent_id: id(10) });
  }, /foreign key/);
  await failure(async () => {
    await db.query('DELETE FROM scheme_catalog.eligibility_rules');
    await insert('eligibility_rules', { id: id(11), scheme_version_id: id(8), rule_key: 'a', node_type: 'and', parent_id: id(12), confidence: 'VERIFIED' });
    await insert('eligibility_rules', { id: id(12), scheme_version_id: id(8), rule_key: 'b', node_type: 'and', parent_id: id(11), confidence: 'VERIFIED' });
    await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
  }, /cycle/);
  await failure(async () => {
    await db.query('DELETE FROM scheme_catalog.eligibility_rules');
    await insert('eligibility_rules', { scheme_version_id: id(8), rule_key: 'not', node_type: 'not', confidence: 'VERIFIED' });
    await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
  }, /arity/);
}));

test('review gates bilingual evidence and freezes published content', () => isolated(async () => {
  const review = () => db.query("UPDATE scheme_catalog.scheme_versions SET status = 'reviewed', reviewed_at = now(), reviewer_reference = 'synthetic-review', last_checked_date = '2026-10-30' WHERE id = $1", [id(8)]);
  await failure(review, /translations/);
  for (const language_code of ['en', 'hi']) {
    await insert('translations', { scheme_version_id: id(8), language_code, title: 'Synthetic test', summary: 'Fixture only', translation_origin: 'human', review_status: 'reviewed', evidence_id: id(6) });
  }
  await failure(review, /jurisdiction/);
  await insert('scheme_jurisdictions', { scheme_version_id: id(8), jurisdiction_id: id(2) });
  await failure(review, /rule tree/);
  await insert('eligibility_rules', { id: id(10), scheme_version_id: id(8), rule_key: 'root', node_type: 'predicate', attribute: 'synthetic_value', operator: 'eq', expected_value: 'true', confidence: 'VERIFIED' });
  await failure(review, /evidence/);
  await insert('rule_evidence', { scheme_version_id: id(8), rule_id: id(10), evidence_id: id(6) });
  await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
  await review();
  await failure(() => db.query("UPDATE scheme_catalog.translations SET title = 'changed'"), /draft/);
  await failure(() => db.query("DELETE FROM scheme_catalog.rule_evidence"), /draft/);
  await db.query("UPDATE scheme_catalog.scheme_versions SET status = 'published', published_at = now() WHERE id = $1", [id(8)]);
  await failure(() => db.query("UPDATE scheme_catalog.scheme_versions SET status = 'draft', published_at = NULL"), /immutable/);
  await failure(() => db.query("DELETE FROM scheme_catalog.scheme_versions"), /immutable/);
}));

test.after(async () => { await db.close(); });

test('Supabase client roles cannot read or mutate any catalogue relation', async () => {
  const { rows } = await db.query("SELECT tablename FROM pg_tables WHERE schemaname = 'scheme_catalog'");
  for (const role of ['anon', 'authenticated', 'service_role']) {
    await db.exec(`SET ROLE ${role}`);
    try {
      for (const { tablename } of rows) {
        for (const statement of [`SELECT * FROM scheme_catalog.${tablename}`,
          `DELETE FROM scheme_catalog.${tablename}`, `UPDATE scheme_catalog.${tablename} SET id = id`,
          `INSERT INTO scheme_catalog.${tablename} DEFAULT VALUES`, `TRUNCATE scheme_catalog.${tablename}`]) {
          await assert.rejects(() => db.exec(statement), /permission denied/);
        }
      }
      await assert.rejects(() => db.exec('SELECT * FROM scheme_catalog.published_versions'), /permission denied/);
    } finally { await db.exec('RESET ROLE'); }
  }
});

test('backend reader sees published data and citations only, never drafts or base tables', () => isolated(async () => {
  for (const language_code of ['en', 'hi']) {
    await insert('translations', { scheme_version_id: id(8), language_code, title: 'Test only', summary: 'Fixture', translation_origin: 'human', review_status: 'reviewed', evidence_id: id(6) });
  }
  await insert('scheme_jurisdictions', { scheme_version_id: id(8), jurisdiction_id: id(2) });
  await insert('eligibility_rules', { id: id(10), scheme_version_id: id(8), rule_key: 'root', node_type: 'predicate', attribute: 'synthetic', operator: 'eq', expected_value: 'true', confidence: 'VERIFIED' });
  await insert('rule_evidence', { scheme_version_id: id(8), rule_id: id(10), evidence_id: id(6) });
  await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
  await db.exec('SET LOCAL ROLE scheme_catalog_reader');
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_versions')).rows.length, 0);
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_evidence')).rows.length, 0);
  await db.exec('RESET ROLE');
  await db.exec("UPDATE scheme_catalog.scheme_versions SET status = 'reviewed', reviewed_at = now(), reviewer_reference = 'test', last_checked_date = '2026-10-30'");
  await db.exec("UPDATE scheme_catalog.scheme_versions SET status = 'published', published_at = now()");
  await insert('scheme_versions', { scheme_id: id(7), version_number: 2 });
  await db.exec('SET LOCAL ROLE scheme_catalog_reader');
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_versions')).rows.length, 1);
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_translations')).rows.length, 2);
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_schemes')).rows.length, 1);
  const evidence = (await db.query('SELECT * FROM scheme_catalog.published_evidence')).rows;
  assert.equal(evidence.length, 1);
  assert.equal(evidence[0].original_url, 'https://example.invalid/test');
  assert.equal('artifact_path' in evidence[0], false);
  await failure(() => db.exec('SELECT * FROM scheme_catalog.scheme_versions'), /permission denied/);
  await failure(() => db.exec('DELETE FROM scheme_catalog.published_versions'), /permission denied/);
  await failure(() => db.exec('CREATE TABLE scheme_catalog.unwanted (id int)'), /permission denied/);
  await db.exec('RESET ROLE');
}));

test('transactional migration-history replay is a no-op; raw replay fails closed', async () => {
  const fresh = new PGlite();
  try {
    // This verifies the history contract locally, not the actual Supabase CLI.
    await fresh.exec('CREATE TABLE applied_migrations (version text PRIMARY KEY)');
    const files = (await readdir(migrationDir)).filter(f => f.endsWith('.sql')).sort();
    async function applyPending() {
      let applied = 0;
      for (const file of files) {
        if ((await fresh.query('SELECT FROM applied_migrations WHERE version = $1', [file])).rows.length) continue;
        await fresh.transaction(async tx => {
          await tx.exec(await readFile(new URL(file, migrationDir), 'utf8'));
          await tx.query('INSERT INTO applied_migrations VALUES ($1)', [file]);
        });
        applied++;
      }
      return applied;
    }
    assert.equal(await applyPending(), 3);
    assert.equal(await applyPending(), 0);
    await assert.rejects(() => fresh.exec(awaitableSql), /already exists/);
  } finally { await fresh.close(); }
});
const awaitableSql = await readFile(new URL('20261030000100_catalog.sql', migrationDir), 'utf8');
