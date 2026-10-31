// Local isolation only. Publication guards run against disposable metadata copies.
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { createLocalStaging, loadCollection } from './staging-import.mjs';

export async function probeWorkflow(db) {
  await db.exec('BEGIN');
  try {
    const before=(await db.query('SELECT * FROM scheme_catalog.scheme_versions ORDER BY id')).rows;
    const versions=(await db.query(`SELECT s.stable_id,v.id,v.version_number,v.status
      FROM scheme_catalog.scheme_versions v JOIN scheme_catalog.schemes s ON s.id=v.scheme_id
      ORDER BY s.stable_id,v.version_number`)).rows;
    await db.exec(`CREATE TEMP TABLE reviewer_version_probe (LIKE scheme_catalog.scheme_versions INCLUDING CONSTRAINTS);
      INSERT INTO reviewer_version_probe SELECT * FROM scheme_catalog.scheme_versions;
      CREATE TRIGGER reviewer_guard BEFORE UPDATE ON reviewer_version_probe
      FOR EACH ROW EXECUTE FUNCTION scheme_catalog.guard_version()`);
    const output=[];
    for (const version of versions) {
      const target=version.status==='draft'?'reviewed':version.status==='reviewed'?'published':null;
      let passed=null,blocker=null;
      if (target) {
        await db.exec('SAVEPOINT reviewer_check');
        try {
          // Only a temporary copy is changed. No real scheme version is updated.
          await db.query(`UPDATE pg_temp.reviewer_version_probe SET status=$1,
            published_at=CASE WHEN $1='published' THEN transaction_timestamp() ELSE published_at END WHERE id=$2`,[target,version.id]);
          await db.exec('SET CONSTRAINTS ALL IMMEDIATE');
          passed=true;
        } catch(error) {
          passed=false;
          blocker=error.code==='P0001'?error.message:'Database metadata/check constraint prevented transition';
        } finally {
          await db.exec('ROLLBACK TO SAVEPOINT reviewer_check');
          await db.exec('RELEASE SAVEPOINT reviewer_check');
        }
      }
      output.push({scheme_id:version.stable_id,version_number:version.version_number,
        current_status:version.status,transition:target?`${version.status}_to_${target}`:'already_published',
        guard_passed:passed,blocker});
    }
    await db.exec('ROLLBACK');
    const after=(await db.query('SELECT * FROM scheme_catalog.scheme_versions ORDER BY id')).rows;
    if (JSON.stringify(before)!==JSON.stringify(after)) throw new Error('Original version metadata changed');
    return {scope:'isolated_pglite_metadata_copies',live_database_access:false,original_versions_unchanged:true,versions:output};
  } catch(error) { await db.exec('ROLLBACK'); throw error; }
}

if (process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const args=process.argv.slice(2);
  if (args.length!==2 || args[1]!=='--local-review') throw new Error('Local reviewer invocation required; remote databases are unsupported');
  const bundles=loadCollection(args[0]);
  const staging=await createLocalStaging();
  try {
    await staging.importBatch(bundles,{commitLocal:true});
    console.log(JSON.stringify(await probeWorkflow(staging.db)));
  } finally { await staging.close(); }
}
