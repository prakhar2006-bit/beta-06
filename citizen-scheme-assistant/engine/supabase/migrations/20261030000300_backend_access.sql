-- Forward-only addition: preserve the original migration history.
-- A group role, not a credential. Provision a separate LOGIN after deployment.
CREATE ROLE scheme_catalog_reader NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA scheme_catalog TO scheme_catalog_reader;

-- These deliberately use the trusted migration owner's permissions. The reader
-- has NO base-table grants. Explicit publication filters are the security boundary.
CREATE VIEW scheme_catalog.published_versions WITH (security_barrier = true) AS
SELECT id, scheme_id, version_number, effective_from, effective_to,
       last_checked_date, published_at
FROM scheme_catalog.scheme_versions WHERE status = 'published';

CREATE VIEW scheme_catalog.published_schemes WITH (security_barrier = true) AS
SELECT s.id, s.stable_id, s.government_level, s.lifecycle_status,
       o.code AS organization_code, o.name AS organization_name, o.official_url AS organization_url
FROM scheme_catalog.schemes s JOIN scheme_catalog.organizations o ON o.id = s.organization_id
WHERE EXISTS (SELECT FROM scheme_catalog.published_versions v WHERE v.scheme_id = s.id);

CREATE VIEW scheme_catalog.published_jurisdictions WITH (security_barrier = true) AS
SELECT sj.id, sj.scheme_version_id, j.id AS jurisdiction_id, j.code, j.name, j.kind
FROM scheme_catalog.scheme_jurisdictions sj
JOIN scheme_catalog.published_versions v ON v.id = sj.scheme_version_id
JOIN scheme_catalog.jurisdictions j ON j.id = sj.jurisdiction_id;

CREATE VIEW scheme_catalog.published_translations WITH (security_barrier = true) AS
SELECT t.* FROM scheme_catalog.translations t JOIN scheme_catalog.published_versions v ON v.id = t.scheme_version_id;
CREATE VIEW scheme_catalog.published_benefits WITH (security_barrier = true) AS
SELECT b.* FROM scheme_catalog.benefits b JOIN scheme_catalog.published_versions v ON v.id = b.scheme_version_id;
CREATE VIEW scheme_catalog.published_application_routes WITH (security_barrier = true) AS
SELECT a.* FROM scheme_catalog.application_routes a JOIN scheme_catalog.published_versions v ON v.id = a.scheme_version_id;
CREATE VIEW scheme_catalog.published_required_documents WITH (security_barrier = true) AS
SELECT d.* FROM scheme_catalog.required_documents d JOIN scheme_catalog.published_versions v ON v.id = d.scheme_version_id;
CREATE VIEW scheme_catalog.published_eligibility_rules WITH (security_barrier = true) AS
SELECT r.* FROM scheme_catalog.eligibility_rules r JOIN scheme_catalog.published_versions v ON v.id = r.scheme_version_id;
CREATE VIEW scheme_catalog.published_rule_evidence WITH (security_barrier = true) AS
SELECT e.* FROM scheme_catalog.rule_evidence e JOIN scheme_catalog.published_versions v ON v.id = e.scheme_version_id;

CREATE VIEW scheme_catalog.published_evidence WITH (security_barrier = true) AS
WITH cited AS (
    SELECT evidence_id FROM scheme_catalog.published_translations
    UNION SELECT evidence_id FROM scheme_catalog.published_benefits
    UNION SELECT evidence_id FROM scheme_catalog.published_application_routes
    UNION SELECT evidence_id FROM scheme_catalog.published_required_documents
    UNION SELECT evidence_id FROM scheme_catalog.published_rule_evidence
)
SELECT e.id, e.locator, e.supporting_text, e.last_checked_date,
       ss.content_sha256, ss.fetched_at, ss.source_updated_at,
       s.original_url, s.title AS source_title, s.license_url
FROM cited c JOIN scheme_catalog.evidence e ON e.id = c.evidence_id
JOIN scheme_catalog.source_snapshots ss ON ss.id = e.snapshot_id
JOIN scheme_catalog.official_sources s ON s.id = ss.source_id;

-- The composite rule FK needs an index beginning with version_id for version
-- deletion/review joins; the previous unique (rule_id,evidence_id) doesn't cover it.
CREATE INDEX rule_evidence_version ON scheme_catalog.rule_evidence(scheme_version_id, rule_id);
CREATE INDEX versions_published ON scheme_catalog.scheme_versions(scheme_id, version_number DESC)
WHERE status = 'published';

DO $$
DECLARE relation_name text; client_role text;
BEGIN
    -- Remove any environment-specific inherited/default client grants explicitly.
    FOREACH client_role IN ARRAY ARRAY['anon', 'authenticated', 'service_role'] LOOP
        IF EXISTS (SELECT FROM pg_roles WHERE rolname = client_role) THEN
            EXECUTE format('REVOKE ALL ON SCHEMA scheme_catalog FROM %I', client_role);
            EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA scheme_catalog FROM %I', client_role);
            EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA scheme_catalog FROM %I', client_role);
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA scheme_catalog REVOKE ALL ON TABLES FROM %I', client_role);
            EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA scheme_catalog REVOKE ALL ON FUNCTIONS FROM %I', client_role);
        END IF;
    END LOOP;
    FOR relation_name IN SELECT viewname FROM pg_views
        WHERE schemaname = 'scheme_catalog' AND viewname LIKE 'published_%' LOOP
        EXECUTE format('REVOKE ALL ON scheme_catalog.%I FROM PUBLIC', relation_name);
        EXECUTE format('GRANT SELECT ON scheme_catalog.%I TO scheme_catalog_reader', relation_name);
    END LOOP;
END $$;
ALTER DEFAULT PRIVILEGES IN SCHEMA scheme_catalog REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
