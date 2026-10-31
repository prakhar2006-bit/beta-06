import {test} from 'node:test';
import assert from 'node:assert/strict';
import {adaptResult,uniqueSources,speechValue} from '../src/services/adapters.js';
test('likely outcomes require an explicit preliminary scope, never an approved result substitution',()=>{
 const raw={eligibility_status:'ELIGIBLE_LIKELY',screening_scope:'preliminary_only',evaluation:{scope:'preliminary_only',policy_review:{execution_enabled:false}},scheme_id:'synthetic-only'};
 assert.equal(adaptResult(raw).status,'ELIGIBLE_LIKELY');
 assert.throws(()=>adaptResult({...raw,screening_scope:'published'}));
 assert.throws(()=>adaptResult({...raw,evaluation:{...raw.evaluation,policy_review:{execution_enabled:true}}}));
 assert.equal(adaptResult({...raw,eligibility_status:'NOT_ELIGIBLE_LIKELY'}).status,'NOT_ELIGIBLE_LIKELY');
});
test('canonical citations retain aliases and discard unsafe links',()=>{
 const sources=uniqueSources([
  {reference_id:'one',original_url:'https://example.gov.in/info?b=2&a=1#top'},
  {reference_id:'two',original_url:'https://example.gov.in/info?a=1&b=2&utm_source=x'},
  {reference_id:'unsafe',original_url:'javascript:alert(1)'}]);
 assert.equal(sources.length,1);assert.deepEqual(sources[0].reference_ids,['one','two']);
});
test('Hindi speech values remain typed input for explicit citizen confirmation',()=>{
 assert.equal(speechValue({answer_type:'integer'},'३०'),30);
 assert.equal(speechValue({answer_type:'boolean'},'हाँ'),true);
 assert.equal(speechValue({answer_type:'boolean'},'नहीं'),false);
 assert.throws(()=>speechValue({answer_type:'integer'},'not a number'));
});
