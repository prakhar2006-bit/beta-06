// Proposed permissions only, exercised in ephemeral PGlite. Never Supabase SQL.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {PGlite} from '@electric-sql/pglite';
const proposal=await readFile(new URL('../ops/draft_writer_PROPOSAL.sql',import.meta.url),'utf8');
const verify=await readFile(new URL('../ops/draft_writer_VERIFY.sql',import.meta.url),'utf8');
const reviewedHook=await readFile(new URL('./fixtures/reviewed-rls-auto-enable.sql',import.meta.url),'utf8');
async function installReviewedHook(db){
 await db.exec(reviewedHook);
 await db.exec("GRANT EXECUTE ON FUNCTION public.rls_auto_enable() TO PUBLIC; CREATE EVENT TRIGGER ensure_rls ON ddl_command_end WHEN TAG IN ('CREATE TABLE','CREATE TABLE AS','SELECT INTO') EXECUTE FUNCTION public.rls_auto_enable()");
}
async function database(){
 const db=new PGlite(),dir=new URL('../supabase/migrations/',import.meta.url);
 for(const f of (await readdir(dir)).filter(f=>f.endsWith('.sql')).sort())await db.exec(await readFile(new URL(f,dir),'utf8'));
 return db;
}
async function seed(db){
 const org=(await db.query("INSERT INTO scheme_catalog.organizations(code,name,government_level,official_url) VALUES ('synthetic','Synthetic only','central','https://example.invalid') RETURNING id")).rows[0].id;
 const scheme=(await db.query("INSERT INTO scheme_catalog.schemes(stable_id,organization_id,government_level) VALUES ('synthetic-only',$1,'central') RETURNING id",[org])).rows[0].id;
 const source=(await db.query("INSERT INTO scheme_catalog.official_sources(organization_id,original_url,source_kind,title) VALUES ($1,'https://example.invalid','webpage','Synthetic') RETURNING id",[org])).rows[0].id;
 const snap=(await db.query("INSERT INTO scheme_catalog.source_snapshots(source_id,content_sha256,media_type) VALUES ($1,repeat('a',64),'text/plain') RETURNING id",[source])).rows[0].id;
 const evidence=(await db.query("INSERT INTO scheme_catalog.evidence(snapshot_id,locator,supporting_text,last_checked_date) VALUES ($1,'Synthetic','Synthetic only',current_date) RETURNING id",[snap])).rows[0].id;
 return {scheme,evidence};
}

test('proposal is NOLOGIN/NOINHERIT, non-owner and verifier is read-only valid SQL',async()=>{
 const db=await database();try{
  await db.exec(proposal);const r=(await db.query("SELECT * FROM pg_roles WHERE rolname='scheme_draft_importer'")).rows[0];
  for(const k of ['rolcanlogin','rolinherit','rolsuper','rolcreaterole','rolcreatedb','rolbypassrls','rolreplication'])assert.equal(r[k],false,k);
  await db.exec(verify);
  await db.exec('SET ROLE scheme_draft_importer');
  assert.ok((await db.query("SELECT row_security_active(c.oid) AS active FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scheme_catalog' AND c.relkind='r'")).rows.every(r=>r.active));
  await assert.rejects(()=>db.exec('ALTER TABLE scheme_catalog.schemes DISABLE ROW LEVEL SECURITY'),/owner|permission/);
 }finally{await db.close();}
});

test('restrictive fences survive broad permissive policies and reject approvals',async()=>{
 const db=await database();try{
  await db.exec(proposal);const {scheme,evidence}=await seed(db);
  await db.exec("CREATE POLICY synthetic_broad ON scheme_catalog.scheme_versions FOR INSERT TO PUBLIC WITH CHECK (true)");
  await db.exec('SET ROLE scheme_draft_importer');
  await assert.rejects(()=>db.query("INSERT INTO scheme_catalog.scheme_versions(scheme_id,version_number,status,reviewer_reference) VALUES ($1,1,'draft','fake approval')",[scheme]),/row-level security/);
  const version=(await db.query("INSERT INTO scheme_catalog.scheme_versions(scheme_id,version_number,status) VALUES ($1,1,'draft') RETURNING id",[scheme])).rows[0].id;
  await assert.rejects(()=>db.query("INSERT INTO scheme_catalog.translations(scheme_version_id,language_code,title,summary,translation_origin,review_status,evidence_id) VALUES ($1,'en','Synthetic','Synthetic','human','reviewed',$2)",[version,evidence]),/row-level security/);
  await assert.rejects(()=>db.query("INSERT INTO scheme_catalog.eligibility_rules(scheme_version_id,rule_key,node_type,attribute,operator,expected_value,confidence) VALUES ($1,'synthetic','predicate','synthetic','eq','true','VERIFIED')",[version]),/row-level security/);
  await assert.rejects(()=>db.exec("UPDATE scheme_catalog.scheme_versions SET status='published'"),/permission/);
  await db.exec('SET row_security=off');
  await assert.rejects(()=>db.query('SELECT * FROM scheme_catalog.scheme_versions'),/row-level security/);
 }finally{await db.close();}
});

test('reviewed/published content cannot be extended or mutated by writer',async()=>{
 const db=await database();try{
  await db.exec(proposal);const {scheme,evidence}=await seed(db);
  const version=(await db.query("INSERT INTO scheme_catalog.scheme_versions(scheme_id,version_number,status,last_checked_date) VALUES ($1,1,'draft',current_date) RETURNING id",[scheme])).rows[0].id;
  const jurisdiction=(await db.query("INSERT INTO scheme_catalog.jurisdictions(code,name,kind) VALUES ('TEST','Synthetic','country') RETURNING id")).rows[0].id;
  await db.query('INSERT INTO scheme_catalog.scheme_jurisdictions(scheme_version_id,jurisdiction_id) VALUES ($1,$2)',[version,jurisdiction]);
  for(const lang of ['en','hi'])await db.query("INSERT INTO scheme_catalog.translations(scheme_version_id,language_code,title,summary,translation_origin,review_status,evidence_id) VALUES ($1,$2,'Synthetic','Synthetic','human','reviewed',$3)",[version,lang,evidence]);
  const rule=(await db.query("INSERT INTO scheme_catalog.eligibility_rules(scheme_version_id,rule_key,node_type,attribute,operator,expected_value,confidence) VALUES ($1,'synthetic','predicate','synthetic','eq','true','VERIFIED') RETURNING id",[version])).rows[0].id;
  await db.query('INSERT INTO scheme_catalog.rule_evidence(scheme_version_id,rule_id,evidence_id) VALUES ($1,$2,$3)',[version,rule,evidence]);
  await db.query("UPDATE scheme_catalog.scheme_versions SET status='reviewed',reviewed_at=now(),reviewer_reference='synthetic-test-only' WHERE id=$1",[version]);
  await db.query("UPDATE scheme_catalog.scheme_versions SET status='published',published_at=now() WHERE id=$1",[version]);
  await db.exec('SET ROLE scheme_draft_importer');
  await assert.rejects(()=>db.query("INSERT INTO scheme_catalog.benefits(scheme_version_id,item_key,benefit_type,description,evidence_id) VALUES ($1,'bad','synthetic','Bad extension',$2)",[version,evidence]),/draft|row-level security/);
  assert.equal((await db.query('UPDATE scheme_catalog.scheme_versions SET id=id WHERE id=$1 RETURNING id',[version])).rows.length,0);
  await assert.rejects(()=>db.exec("UPDATE scheme_catalog.evidence SET supporting_text='tampered'"),/permission/);
  await assert.rejects(()=>db.exec('DELETE FROM scheme_catalog.scheme_versions'),/permission/);
 }finally{await db.close();}
});

test('unrelated PUBLIC schema/table/routine privileges abort and roll back provisioning',async()=>{
 for(const [grant,pattern] of [
  ['GRANT CREATE ON SCHEMA leaky TO PUBLIC',/schema CREATE/],
  ['CREATE TABLE leaky.private_data(id integer); GRANT SELECT ON leaky.private_data TO PUBLIC',/unrelated relation/],
  ["CREATE FUNCTION leaky.rpc() RETURNS integer LANGUAGE sql SECURITY DEFINER AS 'SELECT 1'",/unrelated routine/]
 ]){
  const db=await database();try{
   await db.exec('CREATE SCHEMA leaky; GRANT USAGE ON SCHEMA leaky TO PUBLIC');await db.exec(grant);
   await assert.rejects(()=>db.exec(proposal),pattern);await db.exec('ROLLBACK');
   assert.equal((await db.query("SELECT rolname FROM pg_roles WHERE rolname='scheme_draft_importer'")).rows.length,0);
  }finally{await db.close();}
 }
});

test('schema FK mismatch fails before role provisioning',async()=>{
 const db=await database();try{
  const fk=(await db.query("SELECT conname FROM pg_constraint WHERE conrelid='scheme_catalog.benefits'::regclass AND contype='f' AND confrelid='scheme_catalog.scheme_versions'::regclass")).rows[0].conname;
  await db.exec(`ALTER TABLE scheme_catalog.benefits DROP CONSTRAINT "${fk}"`);
  await assert.rejects(()=>db.exec(proposal),/Missing expected scheme_version_id foreign key/);
  await db.exec('ROLLBACK');
  assert.equal((await db.query("SELECT rolname FROM pg_roles WHERE rolname='scheme_draft_importer'")).rows.length,0);
 }finally{await db.close();}
});

test('correlated child policies require the actual outer parent and preserve composite FK checks',async()=>{
 const db=await database();try{
  await db.exec(proposal);const {scheme,evidence}=await seed(db);await db.exec('SET ROLE scheme_draft_importer');
  const v1=(await db.query("INSERT INTO scheme_catalog.scheme_versions(scheme_id,version_number,status) VALUES ($1,1,'draft') RETURNING id",[scheme])).rows[0].id;
  const v2=(await db.query("INSERT INTO scheme_catalog.scheme_versions(scheme_id,version_number,status) VALUES ($1,2,'draft') RETURNING id",[scheme])).rows[0].id;
  await assert.rejects(()=>db.query("INSERT INTO scheme_catalog.benefits(scheme_version_id,item_key,benefit_type,description,evidence_id) VALUES (gen_random_uuid(),'absent','synthetic','Synthetic',$1)",[evidence]),/row-level security|draft/);
  await db.query("INSERT INTO scheme_catalog.benefits(scheme_version_id,item_key,benefit_type,description,evidence_id) VALUES ($1,'valid','synthetic','Synthetic',$2)",[v1,evidence]);
  const rule=(await db.query("INSERT INTO scheme_catalog.eligibility_rules(scheme_version_id,rule_key,node_type,attribute,operator,expected_value,confidence,uncertainty_reason) VALUES ($1,'synthetic','predicate','synthetic','eq','true','UNCERTAIN','Synthetic draft') RETURNING id",[v1])).rows[0].id;
  await assert.rejects(()=>db.query('INSERT INTO scheme_catalog.rule_evidence(scheme_version_id,rule_id,evidence_id) VALUES ($1,$2,$3)',[v2,rule,evidence]),/foreign key/);
  const privileges=(await db.query("SELECT has_table_privilege('scheme_catalog.scheme_versions','UPDATE') AS table_update,has_column_privilege('scheme_catalog.scheme_versions','id','UPDATE') AS id_update,has_column_privilege('scheme_catalog.scheme_versions','status','UPDATE') AS status_update")).rows[0];
  assert.deepEqual(privileges,{table_update:false,id_update:true,status_update:false});
 }finally{await db.close();}
});

test('real Supabase hook with PUBLIC EXECUTE provisions without changing its ACL/body/binding',async()=>{
 const db=await database();try{
  await installReviewedHook(db);
  const before=(await db.query("SELECT p.prosrc,p.proacl::text,p.proconfig,p.prosecdef FROM pg_proc p WHERE p.oid='public.rls_auto_enable()'::regprocedure")).rows[0];
  assert.equal((await db.query("SELECT encode(sha256(convert_to(prosrc,'UTF8')),'hex') AS hash FROM pg_proc WHERE oid='public.rls_auto_enable()'::regprocedure")).rows[0].hash,'325ae266d9b166715ef5230ceaf7ff9d523e483cf5610dfb9779ab3f183f4af9');
  await db.exec(proposal);await db.exec(verify);
  assert.deepEqual((await db.query("SELECT p.prosrc,p.proacl::text,p.proconfig,p.prosecdef FROM pg_proc p WHERE p.oid='public.rls_auto_enable()'::regprocedure")).rows[0],before);
  await db.exec('SET ROLE scheme_draft_importer');
  // This true ACL was the old audit's false-positive condition; direct call still fails.
  assert.equal((await db.query("SELECT has_function_privilege('public.rls_auto_enable()','EXECUTE') AS acl_execute")).rows[0].acl_execute,true);
  await assert.rejects(()=>db.query('SELECT public.rls_auto_enable()'),/trigger functions can only be called as/);
  await assert.rejects(()=>db.exec("CREATE EVENT TRIGGER writer_hook ON ddl_command_end EXECUTE FUNCTION public.rls_auto_enable()"),/superuser|permission/);
  await assert.rejects(()=>db.exec("ALTER FUNCTION public.rls_auto_enable() SET search_path=public"),/owner|permission/);
  await db.exec('CREATE TEMP TABLE synthetic_writer_temp(id integer)');
  assert.equal((await db.query("SELECT relrowsecurity FROM pg_class WHERE oid='synthetic_writer_temp'::regclass")).rows[0].relrowsecurity,false);
  await assert.rejects(()=>db.exec('CREATE TABLE public.writer_escape(id integer)'),/permission/);
 }finally{await db.close();}
});

test('same-name RPC, unsafe event body and row-trigger SECURITY DEFINER are never name-allowlisted',async()=>{
 for(const setup of [
  "CREATE FUNCTION public.rls_auto_enable() RETURNS integer LANGUAGE sql SECURITY DEFINER AS 'SELECT 1'",
  "CREATE FUNCTION public.rls_auto_enable() RETURNS event_trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path=pg_catalog AS 'BEGIN RAISE EXCEPTION ''unsafe''; END'; CREATE EVENT TRIGGER ensure_rls ON ddl_command_end WHEN TAG IN ('CREATE TABLE') EXECUTE FUNCTION public.rls_auto_enable()",
  "CREATE FUNCTION public.unsafe_row_hook() RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS 'BEGIN RETURN NEW; END'"
 ]){
  const db=await database();try{
   await db.exec(setup);await assert.rejects(()=>db.exec(proposal),/unrelated routine/);await db.exec('ROLLBACK');
   assert.equal((await db.query("SELECT rolname FROM pg_roles WHERE rolname='scheme_draft_importer'")).rows.length,0);
  }finally{await db.close();}
 }
});

test('reviewed hook with widened binding or unsafe search_path still fails closed',async()=>{
 for(const mutate of [
  "DROP EVENT TRIGGER ensure_rls; CREATE EVENT TRIGGER ensure_rls ON ddl_command_end EXECUTE FUNCTION public.rls_auto_enable()",
  'ALTER FUNCTION public.rls_auto_enable() SET search_path=public'
 ]){
  const db=await database();try{
   await installReviewedHook(db);await db.exec(mutate);
   await assert.rejects(()=>db.exec(proposal),/unrelated routine/);await db.exec('ROLLBACK');
  }finally{await db.close();}
 }
});
