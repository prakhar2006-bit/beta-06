// Local-only draft importer. No network driver, DSN, .env or remote write mode.
import { PGlite } from '@electric-sql/pglite';
import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const engine = fileURLToPath(new URL('../', import.meta.url));
const bundles = new WeakSet();
export const order = ['organizations', 'jurisdictions', 'official_sources', 'source_snapshots',
  'evidence', 'schemes', 'scheme_versions', 'scheme_jurisdictions', 'translations',
  'benefits', 'application_routes', 'required_documents', 'eligibility_rules', 'rule_evidence'];
const natural = { organizations: ['code'], jurisdictions: ['code'], official_sources: ['original_url'],
  source_snapshots: ['source_id', 'content_sha256'], evidence: ['snapshot_id', 'locator'], schemes: ['stable_id'] };
const references = { organization_id: 'organizations', source_id: 'official_sources', snapshot_id: 'source_snapshots',
  scheme_id: 'schemes', scheme_version_id: 'scheme_versions', jurisdiction_id: 'jurisdictions',
  evidence_id: 'evidence', rule_id: 'eligibility_rules' };
const canonical = value => JSON.stringify(value, (_, v) => v && typeof v === 'object' && !Array.isArray(v)
  ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => a.localeCompare(b, 'en'))) : v);
const hash = value => createHash('sha256').update(value).digest('hex');
const uuid = value => { const h = hash(value); return `${h.slice(0,8)}-${h.slice(8,12)}-5${h.slice(13,16)}-a${h.slice(17,20)}-${h.slice(20,32)}`; };
const parameter = (key, value) => key === 'expected_value' && value !== null ? JSON.stringify(value) : value;

function validated(path, collection = false) {
  const python = resolve(engine, process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
  const result = spawnSync(python, ['-m', collection ? 'ingestion.batch' : 'ingestion.staging_validate', ...(collection ? ['--validate'] : []), resolve(path)],
    { cwd: engine, encoding: 'utf8', maxBuffer: 8_000_000, env: { ...process.env, PYTHONIOENCODING: 'utf-8' } });
  if (result.status !== 0) throw new Error('Offline bundle validation failed');
  const bundle = JSON.parse(result.stdout);
  // Caller cannot mutate a validated bundle after validation.
  const freeze = v => { if (v && typeof v === 'object') { Object.values(v).forEach(freeze); Object.freeze(v); } };
  freeze(bundle);
  for (const item of collection ? bundle : [bundle]) bundles.add(item);
  return bundle;
}
export const loadBundle = path => validated(path);
export const loadCollection = path => validated(path, true);

async function matches(db, table, row) {
  const keys = Object.keys(row);
  const result = await db.query(`SELECT id FROM scheme_catalog.${table} WHERE ${keys.map((k,i) => `${k} IS NOT DISTINCT FROM $${i+1}`).join(' AND ')}`,
    keys.map(k => parameter(k, row[k])));
  return result.rows.length === 1;
}

export async function createLocalStaging() {
  const db = new PGlite(); // Deliberately no configurable location or remote adapter.
  try {
    const dir = new URL('../supabase/migrations/', import.meta.url);
    for (const file of (await readdir(dir)).filter(f => f.endsWith('.sql')).sort())
      await db.exec(await readFile(new URL(file, dir), 'utf8'));
    // Rehearsal-only receipt storage, NOT a proposed or applied Supabase migration.
    await db.exec('CREATE SCHEMA local_rehearsal; CREATE TABLE local_rehearsal.receipts (digest text PRIMARY KEY, payload jsonb NOT NULL, mapped_rows jsonb NOT NULL)');
  } catch (error) { await db.close(); throw error; }
  let busy = false;
  async function importOne(bundle, { commitLocal = false, expectedVersion = 0 } = {}, nested = false) {
      if (!bundles.has(bundle)) throw new Error('Use loadBundle to validate captured bytes first');
      if (!Number.isInteger(expectedVersion) || expectedVersion < 0) throw new Error('Invalid expected version');
      const payload = bundle.payload;
      const digest = hash(canonical(payload));
      const key = `phase3c-v1:${digest}`;
      let active = false;
      try {
        if (!nested) { await db.exec('BEGIN'); active = true; }
        else await db.exec('SET CONSTRAINTS ALL DEFERRED');
        const previous = (await db.query('SELECT * FROM local_rehearsal.receipts WHERE digest=$1', [digest])).rows[0];
        if (previous) {
          for (const table of order) for (const row of previous.mapped_rows[table] ?? [])
            if (!await matches(db, table, row)) throw new Error('Imported content drift: ' + table);
          const receipt = (await db.query('SELECT status FROM scheme_catalog.ingestion_runs WHERE idempotency_key=$1', [key])).rows;
          if (receipt.length !== 1 || receipt[0].status !== 'succeeded') throw new Error('Receipt drift');
          if (!nested) { await db.exec('ROLLBACK'); active = false; }
          return { outcome: 'already_imported', digest, published: false, recordsWritten: 0 };
        }
        const rows = structuredClone(payload.rows);
        const maps = Object.fromEntries(order.map(t => [t, new Map()]));
        let written = 0;
        let versionNumber;
        for (const table of order) {
          // Preallocate local UUIDs so deferred parent references can point forward.
          for (const row of rows[table] ?? []) maps[table].set(row.id, uuid(`${digest}:${table}:${row.id}:${expectedVersion}`));
          for (const row of rows[table] ?? []) {
            const provisional = row.id;
            row.id = maps[table].get(provisional);
            for (const [field, target] of Object.entries(references)) if (row[field] != null) {
              if (!maps[target].has(row[field])) throw new Error('Unresolved source/reference');
              row[field] = maps[target].get(row[field]);
            }
            if (row.parent_id != null) {
              if (!maps[table].has(row.parent_id)) throw new Error('Unresolved parent');
              row.parent_id = maps[table].get(row.parent_id);
            }
            if (table === 'scheme_versions') {
              const current = Number((await db.query('SELECT coalesce(max(version_number),0) AS n FROM scheme_catalog.scheme_versions WHERE scheme_id=$1', [row.scheme_id])).rows[0].n);
              if (current !== expectedVersion) throw new Error('Version conflict: preview again with the current maximum');
              versionNumber = row.version_number = current + 1;
            }
            const keys = natural[table];
            if (keys) {
              const existing = (await db.query(`SELECT id FROM scheme_catalog.${table} WHERE ${keys.map((k,i) => `${k}=$${i+1}`).join(' AND ')}`, keys.map(k => row[k]))).rows[0];
              if (existing) {
                row.id = existing.id;
                if (!await matches(db, table, row)) throw new Error('Existing content conflict: ' + table);
                maps[table].set(provisional, row.id);
                continue;
              }
            }
            const fields = Object.keys(row);
            if (!fields.every(f => bundle.columns[table].includes(f))) throw new Error('Unknown column');
            await db.query(`INSERT INTO scheme_catalog.${table} (${fields.join(',')}) VALUES (${fields.map((_, i) => '$'+(i+1)).join(',')})`, fields.map(f => parameter(f, row[f])));
            written++;
          }
        }
        await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
        await db.query(`INSERT INTO scheme_catalog.ingestion_runs (source_id,idempotency_key,importer_version,status,finished_at,records_read,records_written) VALUES ($1,$2,'phase3c-local-v1','succeeded',now(),1,$3)`, [rows.official_sources[0].id, key, written]);
        await db.query('INSERT INTO local_rehearsal.receipts VALUES ($1,$2,$3)', [digest, JSON.stringify(payload), JSON.stringify(rows)]);
        const version = (await db.query('SELECT status FROM scheme_catalog.scheme_versions WHERE id=$1', [rows.scheme_versions[0].id])).rows[0];
        if (version.status !== 'draft') throw new Error('Draft invariant failed');
        if (!nested) { await db.exec(commitLocal ? 'COMMIT' : 'ROLLBACK'); active = false; }
        return { outcome: commitLocal ? 'imported_local' : 'dry_run_rolled_back', digest, versionNumber,
          published: false, recordsWritten: commitLocal ? written : 0, plannedRows: written };
      } catch (error) { if (active) await db.exec('ROLLBACK'); throw error; }
  }
  async function exclusive(action) {
    if (busy) throw new Error('Concurrent local import rejected');
    busy = true;
    try { return await action(); } finally { busy = false; }
  }
  return {
    // Local fixture access only. No external DB/client is accepted by this factory.
    db,
    close: () => db.close(),
    importDraft: (bundle, options) => exclusive(() => importOne(bundle, options)),
    importBatch: (input, { commitLocal = false, expectedVersions = {} } = {}) => exclusive(async () => {
      if (!Array.isArray(input) || input.length === 0 || input.length > 100 || input.some(b => !bundles.has(b)))
        throw new Error('Expected 1–100 validated bundles');
      const sorted = [...input].sort((a,b) => a.payload.rows.schemes[0].stable_id.localeCompare(b.payload.rows.schemes[0].stable_id));
      const ids = sorted.map(b => b.payload.rows.schemes[0].stable_id);
      if (new Set(ids).size !== ids.length) throw new Error('Duplicate stable scheme identifier in batch');
      if (Object.keys(expectedVersions).some(id => !ids.includes(id))) throw new Error('Unknown version preview identifier');
      await db.exec('BEGIN');
      try {
        const results = [];
        for (const bundle of sorted) results.push(await importOne(bundle, {
          commitLocal: true, expectedVersion: expectedVersions[bundle.payload.rows.schemes[0].stable_id] ?? 0
        }, true));
        await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
        await db.exec(commitLocal ? 'COMMIT' : 'ROLLBACK');
        const plannedRows = results.reduce((n,r) => n + (r.plannedRows ?? 0), 0);
        return { outcome: commitLocal ? 'batch_imported_local' : 'batch_dry_run_rolled_back',
          schemes: ids.length, plannedRows, recordsWritten: commitLocal ? plannedRows : 0,
          published: false, results: results.map(r => commitLocal ? r : { ...r, outcome: 'dry_run_rolled_back', recordsWritten: 0 }) };
      } catch (error) { await db.exec('ROLLBACK'); throw error; }
    })
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  if (args.length < 1 || args.length > 2 || (args[1] && args[1] !== '--rehearse-local'))
    throw new Error('Usage: node db-validation/staging-import.mjs DRAFT [--rehearse-local]; remote writes unsupported');
  const bundle = loadBundle(args[0]);
  const staging = await createLocalStaging();
  try {
    console.log(JSON.stringify(await staging.importDraft(bundle), null, 2));
    if (args[1]) {
      console.log(JSON.stringify(await staging.importDraft(bundle, { commitLocal: true }), null, 2));
      console.log(JSON.stringify(await staging.importDraft(bundle, { commitLocal: true }), null, 2));
      const receipts = (await staging.db.query('SELECT payload FROM local_rehearsal.receipts')).rows;
      const published = (await staging.db.query('SELECT * FROM scheme_catalog.published_versions')).rows;
      if (receipts.length !== 1 || canonical(receipts[0].payload) !== canonical(bundle.payload) || published.length !== 0)
        throw new Error('Rehearsal preservation/publication assertion failed');
      console.log(JSON.stringify({ fullPayloadPreserved: true, publishedVersions: 0, liveDatabaseAccess: false }));
    }
  } finally { await staging.close(); }
}
