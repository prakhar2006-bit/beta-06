-- Empty catalogue foundation. Apply once through migration history.
CREATE SCHEMA scheme_catalog;
REVOKE ALL ON SCHEMA scheme_catalog FROM PUBLIC;

CREATE TABLE scheme_catalog.organizations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE CHECK (btrim(code) <> ''),
    name text NOT NULL CHECK (btrim(name) <> ''),
    government_level text NOT NULL CHECK (government_level IN ('central', 'state', 'ut', 'local')),
    official_url text NOT NULL CHECK (official_url ~ '^https://[^/]+'),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE scheme_catalog.jurisdictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    code text NOT NULL UNIQUE CHECK (btrim(code) <> ''),
    name text NOT NULL,
    kind text NOT NULL CHECK (kind IN ('country', 'state', 'ut', 'district', 'local')),
    parent_id uuid REFERENCES scheme_catalog.jurisdictions(id),
    CHECK (parent_id IS DISTINCT FROM id)
);

CREATE TABLE scheme_catalog.official_sources (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES scheme_catalog.organizations(id),
    original_url text NOT NULL UNIQUE CHECK (original_url ~ '^https://[^/]+'),
    source_kind text NOT NULL CHECK (source_kind IN ('notification', 'guideline', 'webpage', 'dataset', 'api')),
    title text NOT NULL,
    external_resource_id text,
    license_url text,
    access_policy_url text,
    access_status text NOT NULL DEFAULT 'unverified'
        CHECK (access_status IN ('unverified', 'public_export', 'documented_api', 'written_permission', 'manual_only', 'restricted')),
    permission_reference text,
    policy_checked_date date,
    CHECK (access_status <> 'written_permission' OR permission_reference IS NOT NULL)
);

CREATE TABLE scheme_catalog.ingestion_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES scheme_catalog.official_sources(id),
    idempotency_key text NOT NULL CHECK (btrim(idempotency_key) <> ''),
    importer_version text NOT NULL,
    status text NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'succeeded', 'failed')),
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    records_read integer NOT NULL DEFAULT 0 CHECK (records_read >= 0),
    records_written integer NOT NULL DEFAULT 0 CHECK (records_written >= 0),
    error_code text,
    UNIQUE (source_id, idempotency_key),
    UNIQUE (id, source_id),
    CHECK ((status = 'running') = (finished_at IS NULL)),
    CHECK (finished_at IS NULL OR finished_at >= started_at)
);

CREATE TABLE scheme_catalog.source_snapshots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES scheme_catalog.official_sources(id),
    ingestion_run_id uuid,
    content_sha256 text NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
    fetched_at timestamptz NOT NULL DEFAULT now(),
    source_updated_at timestamptz,
    resolved_url text CHECK (resolved_url ~ '^https://[^/]+'),
    artifact_path text,
    media_type text NOT NULL,
    UNIQUE (source_id, content_sha256),
    FOREIGN KEY (ingestion_run_id, source_id) REFERENCES scheme_catalog.ingestion_runs(id, source_id)
);

CREATE TABLE scheme_catalog.evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id uuid NOT NULL REFERENCES scheme_catalog.source_snapshots(id),
    locator text NOT NULL CHECK (btrim(locator) <> ''),
    supporting_text text NOT NULL CHECK (btrim(supporting_text) <> ''),
    last_checked_date date NOT NULL,
    UNIQUE (snapshot_id, locator)
);

CREATE TABLE scheme_catalog.schemes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    stable_id text NOT NULL UNIQUE CHECK (stable_id ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
    organization_id uuid NOT NULL REFERENCES scheme_catalog.organizations(id),
    government_level text NOT NULL CHECK (government_level IN ('central', 'state', 'ut', 'local')),
    lifecycle_status text NOT NULL DEFAULT 'unknown' CHECK (lifecycle_status IN ('unknown', 'active', 'suspended', 'closed')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE scheme_catalog.scheme_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id uuid NOT NULL REFERENCES scheme_catalog.schemes(id),
    version_number integer NOT NULL CHECK (version_number > 0),
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'reviewed', 'published')),
    effective_from date,
    effective_to date,
    last_checked_date date,
    reviewed_at timestamptz,
    reviewer_reference text,
    published_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (scheme_id, version_number),
    CHECK (effective_to IS NULL OR effective_from IS NULL OR effective_to >= effective_from),
    CHECK (status = 'draft' OR (last_checked_date IS NOT NULL AND reviewed_at IS NOT NULL AND reviewer_reference IS NOT NULL)),
    CHECK ((status = 'published') = (published_at IS NOT NULL))
);

CREATE TABLE scheme_catalog.scheme_jurisdictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    jurisdiction_id uuid NOT NULL REFERENCES scheme_catalog.jurisdictions(id),
    UNIQUE (scheme_version_id, jurisdiction_id)
);

CREATE TABLE scheme_catalog.translations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    language_code text NOT NULL CHECK (language_code IN ('en', 'hi')),
    title text NOT NULL CHECK (btrim(title) <> ''),
    summary text NOT NULL,
    eligibility_text text,
    translation_origin text NOT NULL CHECK (translation_origin IN ('official', 'human', 'machine')),
    review_status text NOT NULL DEFAULT 'draft' CHECK (review_status IN ('draft', 'reviewed')),
    evidence_id uuid NOT NULL REFERENCES scheme_catalog.evidence(id),
    UNIQUE (scheme_version_id, language_code)
);

CREATE TABLE scheme_catalog.benefits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    item_key text NOT NULL,
    benefit_type text NOT NULL,
    description text NOT NULL,
    amount_min numeric(18,2),
    amount_max numeric(18,2),
    currency text CHECK (currency ~ '^[A-Z]{3}$'),
    frequency text,
    evidence_id uuid NOT NULL REFERENCES scheme_catalog.evidence(id),
    UNIQUE (scheme_version_id, item_key),
    CHECK (amount_min IS NULL OR amount_min >= 0),
    CHECK (amount_max IS NULL OR amount_max >= 0),
    CHECK (amount_min IS NULL OR amount_max IS NULL OR amount_max >= amount_min),
    CHECK ((amount_min IS NULL AND amount_max IS NULL) OR currency IS NOT NULL)
);

CREATE TABLE scheme_catalog.application_routes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    item_key text NOT NULL,
    mode text NOT NULL CHECK (mode IN ('online', 'offline', 'both')),
    original_url text CHECK (original_url ~ '^https://[^/]+'),
    instructions text NOT NULL,
    last_checked_date date NOT NULL,
    evidence_id uuid NOT NULL REFERENCES scheme_catalog.evidence(id),
    UNIQUE (scheme_version_id, item_key),
    CHECK (mode = 'offline' OR original_url IS NOT NULL)
);

CREATE TABLE scheme_catalog.required_documents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    item_key text NOT NULL,
    document_type text NOT NULL,
    requirement text NOT NULL CHECK (requirement IN ('required', 'conditional', 'optional', 'unknown')),
    condition_text text,
    evidence_id uuid NOT NULL REFERENCES scheme_catalog.evidence(id),
    UNIQUE (scheme_version_id, item_key),
    CHECK (requirement <> 'conditional' OR condition_text IS NOT NULL)
);

-- Rules are normalized trees. Predicate values are JSON scalars/arrays, never citizen answers.
CREATE TABLE scheme_catalog.eligibility_rules (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    rule_key text NOT NULL,
    parent_id uuid,
    node_type text NOT NULL CHECK (node_type IN ('and', 'or', 'not', 'predicate')),
    attribute text,
    operator text CHECK (operator IN ('eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'exists')),
    expected_value jsonb,
    unit text,
    time_basis text,
    confidence text NOT NULL DEFAULT 'UNCERTAIN' CHECK (confidence IN ('VERIFIED', 'UNCERTAIN')),
    uncertainty_reason text,
    UNIQUE (scheme_version_id, rule_key),
    UNIQUE (id, scheme_version_id),
    FOREIGN KEY (parent_id, scheme_version_id) REFERENCES scheme_catalog.eligibility_rules(id, scheme_version_id) DEFERRABLE INITIALLY DEFERRED,
    CHECK (parent_id IS DISTINCT FROM id),
    CHECK (confidence <> 'UNCERTAIN' OR nullif(btrim(uncertainty_reason), '') IS NOT NULL),
    CHECK ((node_type = 'predicate' AND attribute IS NOT NULL AND operator IS NOT NULL AND expected_value IS NOT NULL)
        OR (node_type <> 'predicate' AND attribute IS NULL AND operator IS NULL AND expected_value IS NULL)),
    CHECK (operator NOT IN ('in', 'not_in') OR jsonb_typeof(expected_value) = 'array'),
    CHECK (operator NOT IN ('gt', 'gte', 'lt', 'lte') OR jsonb_typeof(expected_value) = 'number'),
    CHECK (operator <> 'exists' OR jsonb_typeof(expected_value) = 'boolean')
);
CREATE UNIQUE INDEX rules_one_root ON scheme_catalog.eligibility_rules(scheme_version_id) WHERE parent_id IS NULL;

CREATE TABLE scheme_catalog.rule_evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_version_id uuid NOT NULL REFERENCES scheme_catalog.scheme_versions(id),
    rule_id uuid NOT NULL,
    evidence_id uuid NOT NULL REFERENCES scheme_catalog.evidence(id),
    FOREIGN KEY (rule_id, scheme_version_id) REFERENCES scheme_catalog.eligibility_rules(id, scheme_version_id),
    UNIQUE (rule_id, evidence_id)
);

CREATE INDEX organizations_level ON scheme_catalog.organizations(government_level);
CREATE INDEX jurisdictions_parent ON scheme_catalog.jurisdictions(parent_id);
CREATE INDEX sources_organization ON scheme_catalog.official_sources(organization_id);
CREATE INDEX ingestion_status ON scheme_catalog.ingestion_runs(status, started_at);
CREATE INDEX snapshots_run ON scheme_catalog.source_snapshots(ingestion_run_id, source_id);
CREATE INDEX evidence_snapshot ON scheme_catalog.evidence(snapshot_id);
CREATE INDEX schemes_owner ON scheme_catalog.schemes(organization_id);
CREATE INDEX schemes_level_status ON scheme_catalog.schemes(government_level, lifecycle_status);
CREATE INDEX versions_discovery ON scheme_catalog.scheme_versions(status, last_checked_date);
CREATE INDEX jurisdiction_discovery ON scheme_catalog.scheme_jurisdictions(jurisdiction_id, scheme_version_id);
CREATE INDEX translations_search ON scheme_catalog.translations USING gin (to_tsvector('simple', title || ' ' || summary));
CREATE INDEX translations_evidence ON scheme_catalog.translations(evidence_id);
CREATE INDEX benefits_evidence ON scheme_catalog.benefits(evidence_id);
CREATE INDEX routes_evidence ON scheme_catalog.application_routes(evidence_id);
CREATE INDEX documents_evidence ON scheme_catalog.required_documents(evidence_id);
CREATE INDEX rules_parent ON scheme_catalog.eligibility_rules(parent_id, scheme_version_id);
CREATE INDEX rules_attribute ON scheme_catalog.eligibility_rules(attribute) WHERE node_type = 'predicate';
CREATE INDEX rule_evidence_source ON scheme_catalog.rule_evidence(evidence_id);
