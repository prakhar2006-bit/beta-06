// TEST ONLY: JSON-line SQL adapter into ephemeral PGlite, no remote connection.
import { PGlite } from '@electric-sql/pglite';
import { readFile, readdir } from 'node:fs/promises';
import { createInterface } from 'node:readline';
const db = new PGlite();
const dir = new URL('../supabase/migrations/', import.meta.url);
for (const file of (await readdir(dir)).filter(f=>f.endsWith('.sql')).sort()) await db.exec(await readFile(new URL(file,dir),'utf8'));
if(process.argv.includes('--reviewed-supabase-hook')){
 await db.exec(await readFile(new URL('./fixtures/reviewed-rls-auto-enable.sql',import.meta.url),'utf8'));
 await db.exec("GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO PUBLIC; CREATE EVENT TRIGGER ensure_rls ON ddl_command_end WHEN TAG IN ('CREATE TABLE','CREATE TABLE AS','SELECT INTO') EXECUTE FUNCTION public.rls_auto_enable()");
}
// Rehearse the exact proposed permissions, only in this ephemeral database.
await db.exec(await readFile(new URL('../ops/draft_writer_PROPOSAL.sql',import.meta.url),'utf8'));
await db.exec('SET ROLE scheme_draft_importer');
process.stdout.write('{"ready":true}\n');
for await (const line of createInterface({input:process.stdin,crlfDelay:Infinity})) {
 try {
  const {sql,parameters=[]}=JSON.parse(line);let n=0;
  const statement=sql.replace(/%s/g,()=>`$${++n}`);
  const result=await db.query(statement,parameters);
  process.stdout.write(JSON.stringify({rows:result.rows})+'\n');
 } catch(error) {process.stdout.write(JSON.stringify({error:error.message})+'\n');}
}
await db.close();
