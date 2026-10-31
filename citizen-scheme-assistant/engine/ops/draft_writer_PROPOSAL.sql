-- PROPOSAL ONLY. Not a migration; never executed by the importer.
-- Requires separate project-owner approval and execution against the confirmed project.
-- No passwords, LOGIN credentials, ownership changes, RLS bypass or scheme_api grants.
-- Fails if this role already exists: audit existing grants rather than silently broadening them.
BEGIN;
-- Check the real migration contract before creating any role or policy.
DO $$
DECLARE child_table text;
BEGIN
 IF to_regclass('scheme_catalog.scheme_versions') IS NULL THEN
  RAISE EXCEPTION 'Apply the existing catalogue migrations first';
 END IF;
 FOREACH child_table IN ARRAY ARRAY['scheme_jurisdictions','translations','benefits',
  'application_routes','required_documents','eligibility_rules','rule_evidence'] LOOP
  IF NOT EXISTS (
   SELECT 1 FROM pg_constraint fk JOIN pg_attribute a
    ON a.attrelid=fk.conrelid AND a.attname='scheme_version_id' AND NOT a.attisdropped
   WHERE fk.contype='f' AND fk.conrelid=to_regclass(format('scheme_catalog.%I',child_table))
    AND fk.confrelid='scheme_catalog.scheme_versions'::regclass
    AND fk.conkey=ARRAY[a.attnum]::smallint[]
    AND fk.confkey=ARRAY[(SELECT attnum FROM pg_attribute WHERE attrelid='scheme_catalog.scheme_versions'::regclass AND attname='id')]::smallint[]
  ) THEN RAISE EXCEPTION 'Missing expected scheme_version_id foreign key on %',child_table; END IF;
 END LOOP;
END $$;
CREATE ROLE scheme_draft_importer NOLOGIN NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
ALTER ROLE scheme_draft_importer SET search_path = pg_catalog, scheme_catalog;
ALTER ROLE scheme_draft_importer SET statement_timeout = '15s';
ALTER ROLE scheme_draft_importer SET lock_timeout = '5s';
ALTER ROLE scheme_draft_importer SET idle_in_transaction_session_timeout = '30s';
GRANT USAGE ON SCHEMA scheme_catalog TO scheme_draft_importer;
DO $$
DECLARE t text;
BEGIN
 FOREACH t IN ARRAY ARRAY['organizations','jurisdictions','official_sources','source_snapshots',
  'evidence','schemes','scheme_versions','scheme_jurisdictions','translations','benefits',
  'application_routes','required_documents','eligibility_rules','rule_evidence','ingestion_runs'] LOOP
  EXECUTE format('GRANT SELECT,INSERT ON scheme_catalog.%I TO scheme_draft_importer',t);
  EXECUTE format('CREATE POLICY draft_import_read ON scheme_catalog.%I FOR SELECT TO scheme_draft_importer USING (true)',t);
  EXECUTE format('CREATE POLICY draft_import_insert ON scheme_catalog.%I FOR INSERT TO scheme_draft_importer WITH CHECK (true)',t);
  IF t = 'scheme_versions' THEN
   EXECUTE 'CREATE POLICY draft_import_insert_fence ON scheme_catalog.scheme_versions AS RESTRICTIVE FOR INSERT TO scheme_draft_importer
    WITH CHECK (status=''draft'' AND reviewed_at IS NULL AND reviewer_reference IS NULL AND published_at IS NULL)';
  ELSIF t = ANY(ARRAY['scheme_jurisdictions','translations','benefits','application_routes','required_documents','eligibility_rules','rule_evidence']) THEN
   EXECUTE format('CREATE POLICY draft_import_insert_fence ON scheme_catalog.%I AS RESTRICTIVE FOR INSERT TO scheme_draft_importer
    WITH CHECK (EXISTS (SELECT 1 FROM scheme_catalog.scheme_versions AS v WHERE v.id=scheme_version_id AND v.status=''draft''
     AND v.reviewed_at IS NULL AND v.reviewer_reference IS NULL AND v.published_at IS NULL))',t);
   -- scheme_version_id is the outer policy target column; v has no such column.
   -- No invented child alias or dynamically qualified RTE is required.
  END IF;
 END LOOP;
END $$;
CREATE POLICY draft_import_translation_fence ON scheme_catalog.translations AS RESTRICTIVE FOR INSERT TO scheme_draft_importer
 WITH CHECK (review_status='draft');
CREATE POLICY draft_import_rule_fence ON scheme_catalog.eligibility_rules AS RESTRICTIVE FOR INSERT TO scheme_draft_importer
 WITH CHECK (confidence='UNCERTAIN');
-- Existing guard_version_child SELECT ... FOR UPDATE requires column UPDATE privilege.
-- Identity remains immutable; no status/review/content columns can be updated.
GRANT UPDATE(id) ON scheme_catalog.scheme_versions TO scheme_draft_importer;
CREATE POLICY draft_import_lock ON scheme_catalog.scheme_versions FOR UPDATE TO scheme_draft_importer
 USING (status='draft') WITH CHECK (status='draft');
CREATE POLICY draft_import_lock_fence ON scheme_catalog.scheme_versions AS RESTRICTIVE FOR UPDATE TO scheme_draft_importer
 USING (status='draft' AND reviewed_at IS NULL AND reviewer_reference IS NULL AND published_at IS NULL)
 WITH CHECK (status='draft' AND reviewed_at IS NULL AND reviewer_reference IS NULL AND published_at IS NULL);
GRANT SELECT ON scheme_catalog.published_versions TO scheme_draft_importer;
-- PUBLIC privileges cannot be denied by REVOKE ... FROM this role alone.
-- Fail closed on inherited/shared exposure; do NOT revoke shared grants here.
DO $$
DECLARE unexpected text;
BEGIN
 IF EXISTS (SELECT 1 FROM pg_auth_members WHERE member=(SELECT oid FROM pg_roles WHERE rolname='scheme_draft_importer')) THEN
  RAISE EXCEPTION 'Writer must have no memberships in other roles';
 END IF;
 IF has_database_privilege('scheme_draft_importer',current_database(),'CREATE') THEN
  RAISE EXCEPTION 'Writer inherits database CREATE; review shared grants separately';
 END IF;
 SELECT nspname INTO unexpected FROM pg_namespace
 WHERE nspname NOT IN ('pg_catalog','information_schema') AND nspname !~ '^pg_(toast_)?temp_'
 AND has_schema_privilege('scheme_draft_importer',oid,'CREATE') LIMIT 1;
 IF FOUND THEN RAISE EXCEPTION 'Writer inherits schema CREATE on %. Provisioning rolled back; review PUBLIC grants separately',unexpected; END IF;
 SELECT n.nspname||'.'||c.relname INTO unexpected FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname NOT IN ('pg_catalog','information_schema','scheme_catalog') AND n.nspname !~ '^pg_(toast_)?temp_'
 AND c.relkind IN ('r','p','v','m','f','S') AND has_schema_privilege('scheme_draft_importer',n.oid,'USAGE')
 AND CASE WHEN c.relkind='S' THEN has_sequence_privilege('scheme_draft_importer',c.oid,'USAGE,SELECT,UPDATE')
 ELSE has_table_privilege('scheme_draft_importer',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
   OR has_any_column_privilege('scheme_draft_importer',c.oid,'SELECT,INSERT,UPDATE,REFERENCES') END LIMIT 1;
 IF FOUND THEN RAISE EXCEPTION 'Writer can access unrelated relation %. Provisioning rolled back; audit PUBLIC grants',unexpected; END IF;
 SELECT n.nspname||'.'||p.proname INTO unexpected FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
 WHERE n.nspname NOT IN ('pg_catalog','information_schema','scheme_catalog') AND n.nspname !~ '^pg_(toast_)?temp_'
 AND has_schema_privilege('scheme_draft_importer',n.oid,'USAGE') AND has_function_privilege('scheme_draft_importer',p.oid,'EXECUTE')
 -- Reviewed infrastructure exception, not a function-name allowlist. PUBLIC
 -- EXECUTE on an event_trigger does not make it callable as a SQL/RPC function.
 -- Pin the reviewed body AND owner/language/search_path/bindings: arbitrary
 -- event-trigger or row-trigger SECURITY DEFINER functions are NOT exempt.
 AND NOT coalesce((
  p.prokind='f' AND p.prorettype='pg_catalog.event_trigger'::regtype AND p.pronargs=0 AND NOT p.proretset
  AND p.prosecdef AND p.prolang=(SELECT oid FROM pg_language WHERE lanname='plpgsql')
  AND pg_get_userbyid(p.proowner)='postgres' AND p.proconfig=ARRAY['search_path=pg_catalog']::text[]
  AND encode(sha256(convert_to(p.prosrc,'UTF8')),'hex')='325ae266d9b166715ef5230ceaf7ff9d523e483cf5610dfb9779ab3f183f4af9'
  AND EXISTS (SELECT 1 FROM pg_event_trigger b WHERE b.evtfoid=p.oid)
  AND NOT EXISTS (SELECT 1 FROM pg_event_trigger b WHERE b.evtfoid=p.oid AND NOT coalesce(
   b.evtowner=p.proowner AND b.evtevent='ddl_command_end' AND b.evtenabled IN ('O','D')
   AND b.evttags IS NOT NULL AND cardinality(b.evttags)>0
   AND b.evttags <@ ARRAY['CREATE TABLE','CREATE TABLE AS','SELECT INTO']::text[],false))
 ),false) LIMIT 1;
 IF FOUND THEN RAISE EXCEPTION 'Writer can execute unrelated routine %. Provisioning rolled back; review its shared EXECUTE grant',unexpected; END IF;
 IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scheme_catalog'
   AND c.relkind IN ('r','p') AND (NOT c.relrowsecurity OR pg_has_role('scheme_draft_importer',c.relowner,'USAGE')
    OR has_table_privilege('scheme_draft_importer',c.oid,'UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER'))) THEN
  RAISE EXCEPTION 'Catalogue RLS/owner/mutation privilege check failed';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='scheme_catalog'
  AND p.prosecdef AND has_function_privilege('scheme_draft_importer',p.oid,'EXECUTE')) THEN
  RAISE EXCEPTION 'Unexpected executable SECURITY DEFINER in catalogue';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  JOIN pg_attribute a ON a.attrelid=c.oid WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p','v','m','f')
  AND a.attnum>0 AND NOT a.attisdropped AND has_column_privilege('scheme_draft_importer',c.oid,a.attnum,'UPDATE')
  AND NOT (c.relname='scheme_versions' AND a.attname='id')) THEN
  RAISE EXCEPTION 'Unexpected column UPDATE privilege';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='scheme_catalog'
  AND c.relkind IN ('v','m','f') AND (has_table_privilege('scheme_draft_importer',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
   OR has_any_column_privilege('scheme_draft_importer',c.oid,'INSERT,UPDATE,REFERENCES'))) THEN
  RAISE EXCEPTION 'Unexpected mutable catalogue view/foreign relation';
 END IF;
 IF EXISTS (SELECT 1 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p','v','m','f')
  AND (has_any_column_privilege('scheme_draft_importer',c.oid,'REFERENCES')
   OR has_table_privilege('scheme_draft_importer',c.oid,'SELECT WITH GRANT OPTION,INSERT WITH GRANT OPTION,UPDATE WITH GRANT OPTION')
   OR has_any_column_privilege('scheme_draft_importer',c.oid,'SELECT WITH GRANT OPTION,INSERT WITH GRANT OPTION,UPDATE WITH GRANT OPTION'))) THEN
  RAISE EXCEPTION 'Unexpected REFERENCES or grant-option privilege';
 END IF;
END $$;
COMMIT;
-- An authorized administrator must provision this role's LOGIN/password securely
-- outside source control, then revoke LOGIN/access after the approved import window.
