import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createLocalStaging } from './staging-import.mjs';
import { probeWorkflow } from './reviewer-preview.mjs';

const id=n=>`00000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
async function fixture(db,reviewed=false) {
  await db.exec(`INSERT INTO scheme_catalog.organizations(id,code,name,government_level,official_url)
    VALUES ('${id(1)}','synthetic','Synthetic only','central','https://example.invalid');
    INSERT INTO scheme_catalog.official_sources(id,organization_id,original_url,source_kind,title)
    VALUES ('${id(2)}','${id(1)}','https://example.invalid/policy','webpage','Synthetic');
    INSERT INTO scheme_catalog.source_snapshots(id,source_id,content_sha256,media_type)
    VALUES ('${id(3)}','${id(2)}','${'a'.repeat(64)}','text/plain');
    INSERT INTO scheme_catalog.evidence(id,snapshot_id,locator,supporting_text,last_checked_date)
    VALUES ('${id(4)}','${id(3)}','Synthetic clause','Synthetic assertion','2026-10-31');
    INSERT INTO scheme_catalog.schemes(id,stable_id,organization_id,government_level)
    VALUES ('${id(5)}','synthetic-only','${id(1)}','central');
    INSERT INTO scheme_catalog.scheme_versions(id,scheme_id,version_number)
    VALUES ('${id(6)}','${id(5)}',1)`);
  if (reviewed) {
    await db.exec(`INSERT INTO scheme_catalog.jurisdictions(id,code,name,kind) VALUES ('${id(7)}','TEST','Synthetic','country');
      INSERT INTO scheme_catalog.scheme_jurisdictions(scheme_version_id,jurisdiction_id) VALUES ('${id(6)}','${id(7)}');
      INSERT INTO scheme_catalog.translations(scheme_version_id,language_code,title,summary,translation_origin,review_status,evidence_id)
      VALUES ('${id(6)}','en','Synthetic','Test only','human','reviewed','${id(4)}'),
      ('${id(6)}','hi','Synthetic','Test only','human','reviewed','${id(4)}');
      INSERT INTO scheme_catalog.eligibility_rules(id,scheme_version_id,rule_key,node_type,attribute,operator,expected_value,confidence)
      VALUES ('${id(8)}','${id(6)}','test','predicate','synthetic','eq','true','VERIFIED');
      INSERT INTO scheme_catalog.rule_evidence(scheme_version_id,rule_id,evidence_id) VALUES ('${id(6)}','${id(8)}','${id(4)}');
      UPDATE scheme_catalog.scheme_versions SET status='reviewed',reviewer_reference='synthetic-review',reviewed_at=now(),last_checked_date='2026-10-31'
      WHERE id='${id(6)}'`);
  }
}
async function isolated(fn) { const s=await createLocalStaging();try { await fn(s.db); } finally { await s.close(); } }

test('actual migration guard rejects incomplete draft without changing it',()=>isolated(async db=>{
  await fixture(db);
  const result=await probeWorkflow(db);
  assert.equal(result.versions[0].guard_passed,false);
  assert.match(result.versions[0].blocker,/translations/);
  assert.equal((await db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows[0].status,'draft');
}));
test('fully reviewed synthetic copy passes publication guard but original stays reviewed',()=>isolated(async db=>{
  await fixture(db,true);
  const result=await probeWorkflow(db);
  assert.equal(result.versions[0].guard_passed,true);
  assert.equal(result.original_versions_unchanged,true);
  assert.equal((await db.query('SELECT status FROM scheme_catalog.scheme_versions')).rows[0].status,'reviewed');
  assert.equal((await db.query('SELECT * FROM scheme_catalog.published_versions')).rows.length,0);
}));
test('restricted reader cannot inspect draft records through probe',()=>isolated(async db=>{
  await fixture(db);
  await db.exec('SET ROLE scheme_catalog_reader');
  try { await assert.rejects(probeWorkflow(db),/permission denied/); }
  finally { await db.exec('RESET ROLE'); }
}));
