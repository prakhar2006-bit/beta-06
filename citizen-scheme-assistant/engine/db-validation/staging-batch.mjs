// Collection CLI: strictly in-memory PGlite, dry-run by default.
import { createLocalStaging, loadCollection, order } from './staging-import.mjs';
const args = process.argv.slice(2);
if (args.length < 1 || args.length > 2 || (args[1] && args[1] !== '--rehearse-local'))
  throw new Error('Usage: node db-validation/staging-batch.mjs COLLECTION_JSON [--rehearse-local]');
const bundles = loadCollection(args[0]);
const staging = await createLocalStaging();
try {
  const preview = await staging.importBatch(bundles);
  const previewAgain = await staging.importBatch([...bundles].reverse());
  if (JSON.stringify(preview) !== JSON.stringify(previewAgain)) throw new Error('Non-deterministic dry-run');
  console.log(JSON.stringify({ dryRun: preview }));
  if (args[1]) {
    const imported = await staging.importBatch(bundles, { commitLocal: true });
    const repeated = await staging.importBatch(bundles, { commitLocal: true });
    if (repeated.recordsWritten !== 0 || repeated.results.some(r => r.outcome !== 'already_imported'))
      throw new Error('Repeat added records');
    const receipts = (await staging.db.query('SELECT payload FROM local_rehearsal.receipts')).rows;
    const versions = (await staging.db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows;
    const published = (await staging.db.query('SELECT * FROM scheme_catalog.published_versions')).rows;
    if (receipts.length !== bundles.length || versions.length !== bundles.length || published.length || versions.some(v => v.status !== 'draft'))
      throw new Error('Draft/receipt invariant failed');
    const sortedJSON = value => JSON.stringify(value, (_, v) => v && typeof v === 'object' && !Array.isArray(v)
      ? Object.fromEntries(Object.entries(v).sort(([a],[b]) => a.localeCompare(b, 'en'))) : v);
    if (receipts.some(r => !bundles.some(b => sortedJSON(b.payload) === sortedJSON(r.payload))) ||
        receipts.some(r => r.payload.rule_review.some(rule => rule.enabled !== false)))
      throw new Error('Sidecar/rule preservation failed');
    const counts = {};
    for (const table of [...order, 'ingestion_runs']) counts[table] = Number((await staging.db.query(`SELECT count(*) AS n FROM scheme_catalog.${table}`)).rows[0].n);
    console.log(JSON.stringify({ imported, repeated, counts, catalogueRows: Object.entries(counts).reduce((n,[t,c]) => n+(t === 'ingestion_runs' ? 0 : c),0),
      fullPayloadsPreserved: true, publishedVersions: 0, unapprovedRulesEnabled: 0, liveDatabaseAccess: false }));
  }
} finally { await staging.close(); }
