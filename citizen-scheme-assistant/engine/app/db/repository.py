"""Parameterized queries grounded in migrations 001 and 003; no base-table reads."""
from datetime import datetime, timedelta, timezone
from app.db.connection import open_connection
from app.schemas.schemes import Language, Level, SchemeDetail, SchemeList, SchemeSummary

LOCAL_TIMEZONE = timezone(timedelta(hours=5, minutes=30))

# Pick a version BEFORE localization/search, so an older matching title never
# causes an obsolete version to replace the current published version.
CATALOG = """
WITH current_versions AS (
    SELECT DISTINCT ON (scheme_id) * FROM scheme_catalog.published_versions
    WHERE (effective_from IS NULL OR effective_from <= %(as_of)s)
      AND (effective_to IS NULL OR effective_to >= %(as_of)s)
    ORDER BY scheme_id, version_number DESC, id
), localized AS (
    SELECT s.stable_id AS id, s.id AS database_id, v.id AS version_id,
           v.version_number, v.last_checked_date, v.effective_from, v.effective_to,
           v.published_at, s.government_level AS level, s.lifecycle_status,
           s.organization_code, s.organization_name, s.organization_url,
           t.language_code AS language, t.title AS name, t.summary AS description,
           t.eligibility_text, t.evidence_id AS translation_evidence_id,
           %(lang)s::text AS requested_language,
           (t.language_code IS DISTINCT FROM %(lang)s::text) AS translation_fallback
    FROM scheme_catalog.published_schemes s JOIN current_versions v ON v.scheme_id = s.id
    LEFT JOIN LATERAL (
        SELECT language_code, title, summary, eligibility_text, evidence_id
        FROM scheme_catalog.published_translations
        WHERE scheme_version_id = v.id AND language_code IN ('en', 'hi')
        ORDER BY (language_code = %(lang)s) DESC, language_code LIMIT 1
    ) t ON true
)
"""
FILTER = """ WHERE (%(level)s::text IS NULL OR level = %(level)s)
AND (%(search)s::text IS NULL OR COALESCE(name, '') ILIKE %(search)s ESCAPE '!'
     OR COALESCE(description, '') ILIKE %(search)s ESCAPE '!') """


class SchemeRepository:
    def list_schemes(self, lang: Language, search: str | None, level: Level | None,
                     limit: int, offset: int) -> SchemeList:
        pattern = None
        if search and search.strip():
            pattern = '%' + search.strip().replace('!', '!!').replace('%', '!%').replace('_', '!_') + '%'
        params = {"as_of": datetime.now(LOCAL_TIMEZONE).date(), "lang": lang,
                  "level": level, "search": pattern, "limit": limit, "offset": offset}
        with open_connection() as conn, conn.cursor() as cursor:
            cursor.execute(CATALOG + 'SELECT count(*) AS total FROM localized' + FILTER, params)
            total = cursor.fetchone()["total"]
            cursor.execute(CATALOG + 'SELECT * FROM localized' + FILTER +
                           ' ORDER BY id, database_id LIMIT %(limit)s OFFSET %(offset)s', params)
            items = [SchemeSummary.model_validate(row) for row in cursor.fetchall()]
        return SchemeList(items=items, total=total, limit=limit, offset=offset,
                          has_more=offset + len(items) < total)

    def get_scheme(self, scheme_id: str, lang: Language) -> SchemeDetail | None:
        params = {"as_of": datetime.now(LOCAL_TIMEZONE).date(), "lang": lang, "id": scheme_id}
        with open_connection() as conn, conn.cursor() as cursor:
            cursor.execute(CATALOG + 'SELECT * FROM localized WHERE id = %(id)s', params)
            row = cursor.fetchone()
            if row is None:
                return None
            version = {"version_id": row["version_id"]}
            # Fixed allowlisted queries, never identifiers supplied by a client.
            queries = {
                "benefits": 'SELECT * FROM scheme_catalog.published_benefits WHERE scheme_version_id = %(version_id)s ORDER BY item_key, id',
                "application_routes": 'SELECT * FROM scheme_catalog.published_application_routes WHERE scheme_version_id = %(version_id)s ORDER BY item_key, id',
                "required_documents": 'SELECT * FROM scheme_catalog.published_required_documents WHERE scheme_version_id = %(version_id)s ORDER BY item_key, id',
                "eligibility_rules": 'SELECT * FROM scheme_catalog.published_eligibility_rules WHERE scheme_version_id = %(version_id)s ORDER BY rule_key, id',
                "rule_evidence": 'SELECT rule_id, evidence_id FROM scheme_catalog.published_rule_evidence WHERE scheme_version_id = %(version_id)s ORDER BY rule_id, evidence_id',
                "jurisdictions": 'SELECT jurisdiction_id, code, name, kind FROM scheme_catalog.published_jurisdictions WHERE scheme_version_id = %(version_id)s ORDER BY code, jurisdiction_id',
                "sources": """SELECT e.* FROM scheme_catalog.published_evidence e WHERE e.id IN (
                    SELECT evidence_id FROM scheme_catalog.published_translations WHERE scheme_version_id = %(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_benefits WHERE scheme_version_id = %(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_application_routes WHERE scheme_version_id = %(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_required_documents WHERE scheme_version_id = %(version_id)s
                    UNION SELECT evidence_id FROM scheme_catalog.published_rule_evidence WHERE scheme_version_id = %(version_id)s
                ) ORDER BY original_url, id""",
            }
            for name, query in queries.items():
                cursor.execute(query, version)
                row[name] = cursor.fetchall()
            return SchemeDetail.model_validate(row)

    def health(self) -> None:
        with open_connection() as conn, conn.cursor() as cursor:
            cursor.execute('SELECT id FROM scheme_catalog.published_versions LIMIT 1')
            cursor.fetchone()


def get_repository() -> SchemeRepository:
    return SchemeRepository()
