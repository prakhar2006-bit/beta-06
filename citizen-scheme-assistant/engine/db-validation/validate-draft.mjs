// Opt-in local payload validation: never connects to Supabase or reads .env.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { PGlite } from '@electric-sql/pglite';

const path = process.argv[2];
if (!path) throw new Error('Usage: node db-validation/validate-draft.mjs PATH_TO_DRAFT_JSON');
const payload = JSON.parse(await readFile(path, 'utf8'));
const order = ['organizations', 'jurisdictions', 'official_sources', 'ingestion_runs',
  'source_snapshots', 'evidence', 'schemes', 'scheme_versions', 'scheme_jurisdictions',
  'translations', 'benefits', 'application_routes', 'required_documents', 'eligibility_rules', 'rule_evidence'];

test('draft rows satisfy actual migrations and remain unpublished', async () => {
  assert.equal(payload.mode, 'local_draft_only');
  assert.equal(payload.publish_allowed, false);
  assert.equal(payload.eligible_for_execution, false);
  assert.deepEqual(payload.database_operations, []);
  assert.ok(payload.rule_review.every(rule => rule.enabled === false));
  assert.ok(Object.keys(payload.rows).every(table => order.includes(table)));
  const db = new PGlite();
  try {
    const dir = new URL('../supabase/migrations/', import.meta.url);
    for (const file of (await readdir(dir)).filter(f => f.endsWith('.sql')).sort()) {
      await db.exec(await readFile(new URL(file, dir), 'utf8'));
    }
    await db.exec('BEGIN');
    for (const table of order) {
      for (const row of payload.rows[table] ?? []) {
        const fields = Object.keys(row);
        assert.ok(fields.every(field => /^[a-z_][a-z_0-9]*$/.test(field)));
        const values = fields.map(field => field === 'expected_value' && row[field] !== null ? JSON.stringify(row[field]) : row[field]);
        await db.query(`INSERT INTO scheme_catalog.${table} (${fields.join(',')}) VALUES (${fields.map((_, i) => '$' + (i + 1)).join(',')})`, values);
      }
    }
    await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
    const versions = (await db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows;
    assert.ok(versions.length > 0 && versions.every(v => v.status === 'draft'));
    assert.equal((await db.query('SELECT * FROM scheme_catalog.published_versions')).rows.length, 0);
    await db.exec('ROLLBACK');
  } finally {
    await db.close();
  }
});
