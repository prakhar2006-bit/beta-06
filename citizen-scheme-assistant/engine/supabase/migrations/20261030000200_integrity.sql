-- Reviewed/published versions and their children are frozen. Corrections create a new version.
CREATE FUNCTION scheme_catalog.guard_version() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, scheme_catalog AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.status <> 'draft' THEN RAISE EXCEPTION 'Reviewed versions are immutable'; END IF;
        RETURN OLD;
    END IF;
    IF TG_OP = 'INSERT' THEN
        IF NEW.status <> 'draft' THEN RAISE EXCEPTION 'Versions must start as draft'; END IF;
        RETURN NEW;
    END IF;
    IF NEW.scheme_id <> OLD.scheme_id OR NEW.version_number <> OLD.version_number OR NEW.id <> OLD.id THEN
        RAISE EXCEPTION 'Version identity is immutable';
    END IF;
    IF OLD.status = 'published' OR (OLD.status = 'reviewed' AND NEW.status <> 'published') THEN
        RAISE EXCEPTION 'Reviewed versions are immutable';
    END IF;
    IF OLD.status = 'draft' AND NEW.status = 'published' THEN
        RAISE EXCEPTION 'Review before publishing';
    END IF;
    IF OLD.status = 'reviewed' AND
       (to_jsonb(NEW) - 'status' - 'published_at') IS DISTINCT FROM
       (to_jsonb(OLD) - 'status' - 'published_at') THEN
        RAISE EXCEPTION 'Only publication metadata may change after review';
    END IF;
    IF NEW.status IN ('reviewed', 'published') THEN
        IF (SELECT count(*) FROM scheme_catalog.translations
            WHERE scheme_version_id = NEW.id AND review_status = 'reviewed') <> 2 THEN
            RAISE EXCEPTION 'Reviewed English and Hindi translations required';
        END IF;
        IF NOT EXISTS (SELECT FROM scheme_catalog.scheme_jurisdictions WHERE scheme_version_id = NEW.id) THEN
            RAISE EXCEPTION 'At least one jurisdiction required';
        END IF;
        IF NOT EXISTS (SELECT FROM scheme_catalog.eligibility_rules WHERE scheme_version_id = NEW.id AND parent_id IS NULL) THEN
            RAISE EXCEPTION 'A rule tree is required';
        END IF;
        IF EXISTS (SELECT FROM scheme_catalog.eligibility_rules r
            WHERE r.scheme_version_id = NEW.id AND r.node_type = 'predicate'
              AND NOT EXISTS (SELECT FROM scheme_catalog.rule_evidence e WHERE e.rule_id = r.id)) THEN
            RAISE EXCEPTION 'Every predicate requires evidence';
        END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_version BEFORE INSERT OR UPDATE OR DELETE ON scheme_catalog.scheme_versions
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.guard_version();

CREATE FUNCTION scheme_catalog.guard_version_child() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, scheme_catalog AS $$
DECLARE version_id uuid;
BEGIN
    IF TG_OP = 'UPDATE' AND (NEW.scheme_version_id <> OLD.scheme_version_id OR NEW.id <> OLD.id) THEN
        RAISE EXCEPTION 'Child identity and version are immutable';
    END IF;
    IF TG_OP = 'DELETE' THEN version_id := OLD.scheme_version_id;
    ELSE version_id := NEW.scheme_version_id; END IF;
    -- Serialize child edits with review/publication to avoid concurrent review races.
    PERFORM 1 FROM scheme_catalog.scheme_versions WHERE id = version_id AND status = 'draft' FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'Only draft version content may change'; END IF;
    IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
    RETURN NEW;
END $$;

DO $$
DECLARE table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY['scheme_jurisdictions', 'translations', 'benefits',
        'application_routes', 'required_documents', 'eligibility_rules', 'rule_evidence'] LOOP
        EXECUTE format('CREATE TRIGGER guard_content BEFORE INSERT OR UPDATE OR DELETE ON scheme_catalog.%I FOR EACH ROW EXECUTE FUNCTION scheme_catalog.guard_version_child()', table_name);
    END LOOP;
END $$;

-- Deferred validation permits a complete tree to be assembled in one transaction.
CREATE FUNCTION scheme_catalog.validate_rule_tree() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, scheme_catalog AS $$
DECLARE version_id uuid;
BEGIN
    IF TG_OP = 'DELETE' THEN version_id := OLD.scheme_version_id;
    ELSE version_id := NEW.scheme_version_id; END IF;
    IF EXISTS (
        WITH RECURSIVE ancestors AS (
            SELECT id, parent_id, ARRAY[id] AS path, false AS cycle
            FROM scheme_catalog.eligibility_rules WHERE scheme_version_id = version_id
            UNION ALL
            SELECT a.id, r.parent_id, a.path || r.id, r.id = ANY(a.path)
            FROM ancestors a JOIN scheme_catalog.eligibility_rules r ON r.id = a.parent_id
            WHERE NOT a.cycle
        ) SELECT FROM ancestors WHERE cycle
    ) THEN RAISE EXCEPTION 'Rule tree contains a cycle'; END IF;
    IF EXISTS (
        SELECT FROM scheme_catalog.eligibility_rules r
        LEFT JOIN scheme_catalog.eligibility_rules c ON c.parent_id = r.id
        WHERE r.scheme_version_id = version_id
        GROUP BY r.id, r.node_type
        HAVING (r.node_type = 'predicate' AND count(c.id) <> 0)
            OR (r.node_type = 'not' AND count(c.id) <> 1)
            OR (r.node_type IN ('and', 'or') AND count(c.id) = 0)
    ) THEN RAISE EXCEPTION 'Invalid rule node arity'; END IF;
    RETURN NULL;
END $$;
CREATE CONSTRAINT TRIGGER validate_rule_tree AFTER INSERT OR UPDATE OR DELETE
ON scheme_catalog.eligibility_rules DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.validate_rule_tree();

CREATE FUNCTION scheme_catalog.guard_scheme_identity() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    IF NEW.id <> OLD.id OR NEW.stable_id <> OLD.stable_id THEN
        RAISE EXCEPTION 'Scheme identity is immutable';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_identity BEFORE UPDATE ON scheme_catalog.schemes
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.guard_scheme_identity();

CREATE FUNCTION scheme_catalog.guard_source_identity() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    IF NEW.id <> OLD.id OR NEW.original_url <> OLD.original_url
       OR NEW.organization_id <> OLD.organization_id THEN
        RAISE EXCEPTION 'Original source identity is immutable';
    END IF;
    RETURN NEW;
END $$;
CREATE TRIGGER guard_source_identity BEFORE UPDATE ON scheme_catalog.official_sources
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.guard_source_identity();

-- Evidence and snapshots are append-only so citations cannot silently change.
CREATE FUNCTION scheme_catalog.reject_mutation() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog AS $$
BEGIN
    RAISE EXCEPTION 'Provenance is append-only; insert a new record';
END $$;
CREATE TRIGGER immutable_evidence BEFORE UPDATE OR DELETE ON scheme_catalog.evidence
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.reject_mutation();
CREATE TRIGGER immutable_snapshot BEFORE UPDATE OR DELETE ON scheme_catalog.source_snapshots
FOR EACH ROW EXECUTE FUNCTION scheme_catalog.reject_mutation();

-- Backend-only schema: no public/client grants or policies. Owner/migration role
-- operates through a server connection. Explicit grants for a dedicated backend
-- role should be a separate reviewed migration when that role is provisioned.
DO $$
DECLARE table_name text;
BEGIN
    FOR table_name IN SELECT tablename FROM pg_tables WHERE schemaname = 'scheme_catalog' LOOP
        EXECUTE format('ALTER TABLE scheme_catalog.%I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('REVOKE ALL ON scheme_catalog.%I FROM PUBLIC', table_name);
    END LOOP;
END $$;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA scheme_catalog FROM PUBLIC;
