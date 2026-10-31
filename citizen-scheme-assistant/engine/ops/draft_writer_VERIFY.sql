-- REVIEW ONLY. Run manually AFTER separately approved provisioning; no credentials or writes.
-- Execute as project administrator in the confirmed project's SQL Editor.
BEGIN READ ONLY;

-- Exactly one row. Before credential activation every boolean below must be false.
-- After approved activation only rolcanlogin should become true.
SELECT rolname,rolcanlogin,rolinherit,rolsuper,rolcreatedb,rolcreaterole,rolreplication,rolbypassrls,
       rolconnlimit,rolvaliduntil,rolconfig
FROM pg_roles WHERE rolname='scheme_draft_importer';

-- Must return zero rows: writer cannot inherit/SET ROLE to another role.
SELECT parent.rolname AS member_of,m.admin_option
FROM pg_auth_members m JOIN pg_roles parent ON parent.oid=m.roleid
JOIN pg_roles child ON child.oid=m.member WHERE child.rolname='scheme_draft_importer';

-- 15 base tables: RLS true, SELECT/INSERT true; table UPDATE/mutation false.
-- can_update_any_column is true ONLY for scheme_versions (the id lock grant).
SELECT c.relname,c.relrowsecurity,
 pg_has_role('scheme_draft_importer',c.relowner,'USAGE') AS owner_access,
 has_table_privilege('scheme_draft_importer',c.oid,'SELECT') AS can_select,
 has_table_privilege('scheme_draft_importer',c.oid,'INSERT') AS can_insert,
 has_table_privilege('scheme_draft_importer',c.oid,'UPDATE') AS can_update_table,
 has_any_column_privilege('scheme_draft_importer',c.oid,'UPDATE') AS can_update_any_column,
 has_any_column_privilege('scheme_draft_importer',c.oid,'REFERENCES') AS unsafe_column_references,
 has_any_column_privilege('scheme_draft_importer',c.oid,'SELECT WITH GRANT OPTION,INSERT WITH GRANT OPTION,UPDATE WITH GRANT OPTION') AS unsafe_column_grant_option,
 has_table_privilege('scheme_draft_importer',c.oid,'UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER') AS unsafe_mutation
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p') ORDER BY c.relname;

-- Exactly one row: scheme_versions.id. It permits the existing FOR UPDATE row lock,
-- not publication/review/content edits. Table-level UPDATE above must remain false.
SELECT c.relname,a.attname AS updatable_column
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid
WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p') AND a.attnum>0 AND NOT a.attisdropped
AND has_column_privilege('scheme_draft_importer',c.oid,a.attnum,'UPDATE');

-- Must return zero rows: column UPDATE is not equivalent to table UPDATE.
SELECT c.relname,a.attname AS unsafe_updatable_column
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_attribute a ON a.attrelid=c.oid
WHERE n.nspname='scheme_catalog' AND c.relkind IN ('r','p','v','m','f') AND a.attnum>0 AND NOT a.attisdropped
AND has_column_privilege('scheme_draft_importer',c.oid,a.attnum,'UPDATE')
AND NOT (c.relname='scheme_versions' AND a.attname='id');

-- Must return zero rows, including column-only INSERT/UPDATE grants on views.
SELECT c.relname AS unsafe_mutable_view FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname='scheme_catalog' AND c.relkind IN ('v','m','f')
AND (has_table_privilege('scheme_draft_importer',c.oid,'INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
 OR has_any_column_privilege('scheme_draft_importer',c.oid,'INSERT,UPDATE,REFERENCES'));

-- Inspect policies: restrictive insert fences must exist for versions and children,
-- translation review_status, rule confidence, and draft-only version row locks.
SELECT tablename,policyname,permissive,roles,cmd,qual,with_check
FROM pg_policies WHERE schemaname='scheme_catalog'
AND 'scheme_draft_importer'=ANY(roles) ORDER BY tablename,policyname;

-- Must be false. Standard CONNECT/TEMP and system-catalog access are not denied.
SELECT has_database_privilege('scheme_draft_importer',current_database(),'CREATE') AS unsafe_database_create;

-- Must return zero rows. PUBLIC privileges count; REVOKE FROM writer alone cannot deny them.
SELECT 'schema_create' AS exposure,n.nspname AS object_name FROM pg_namespace n
WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname !~ '^pg_(toast_)?temp_'
AND has_schema_privilege('scheme_draft_importer',n.oid,'CREATE')
UNION ALL
SELECT 'unrelated_relation',n.nspname||'.'||c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
WHERE n.nspname NOT IN ('pg_catalog','information_schema','scheme_catalog') AND n.nspname !~ '^pg_(toast_)?temp_'
AND c.relkind IN ('r','p','v','m','f','S') AND has_schema_privilege('scheme_draft_importer',n.oid,'USAGE')
AND CASE WHEN c.relkind='S' THEN has_sequence_privilege('scheme_draft_importer',c.oid,'USAGE,SELECT,UPDATE')
 ELSE has_table_privilege('scheme_draft_importer',c.oid,'SELECT,INSERT,UPDATE,DELETE,TRUNCATE,REFERENCES,TRIGGER')
 OR has_any_column_privilege('scheme_draft_importer',c.oid,'SELECT,INSERT,UPDATE,REFERENCES') END
UNION ALL
SELECT 'unrelated_routine',n.nspname||'.'||p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog','information_schema','scheme_catalog') AND n.nspname !~ '^pg_(toast_)?temp_'
AND has_schema_privilege('scheme_draft_importer',n.oid,'USAGE') AND has_function_privilege('scheme_draft_importer',p.oid,'EXECUTE')
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
),false)
UNION ALL
SELECT 'catalogue_security_definer',n.nspname||'.'||p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
WHERE n.nspname='scheme_catalog' AND p.prosecdef AND has_function_privilege('scheme_draft_importer',p.oid,'EXECUTE');

-- Informational ACL provenance and hook metadata, NOT a failed security check.
-- NULL proacl means built-in default ACL; otherwise this is a stored explicit ACL.
-- The source hash above is independently enforced by the provisioning audit.
SELECT p.oid::regprocedure::text AS routine,p.prorettype::regtype::text AS returns,
 p.prosecdef,p.proacl IS NULL AS uses_default_acl,
 encode(sha256(convert_to(p.prosrc,'UTF8')),'hex') AS source_sha256,
 CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
 a.privilege_type,a.is_grantable,b.evtname,b.evtevent,b.evttags
FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
CROSS JOIN LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
LEFT JOIN pg_event_trigger b ON b.evtfoid=p.oid
WHERE n.nspname='public' AND p.proname='rls_auto_enable' ORDER BY routine,grantee;

-- Independent administrator version preflight: 15 rows, all statuses considered.
-- A zero maximum is verified absence of a version, not absence of a scheme identity.
WITH requested AS (
 SELECT 'in-cen-'||lpad(i::text,6,'0') AS stable_id FROM generate_series(1,15) AS g(i)
)
SELECT r.stable_id,s.id AS existing_scheme_id,coalesce(max(v.version_number),0) AS current_max_version,
 count(v.id) FILTER (WHERE v.status='draft') AS drafts,
 count(v.id) FILTER (WHERE v.status='reviewed') AS reviewed,
 count(v.id) FILTER (WHERE v.status='published') AS published
FROM requested r LEFT JOIN scheme_catalog.schemes s ON s.stable_id=r.stable_id
LEFT JOIN scheme_catalog.scheme_versions v ON v.scheme_id=s.id
GROUP BY r.stable_id,s.id ORDER BY r.stable_id;
ROLLBACK;
