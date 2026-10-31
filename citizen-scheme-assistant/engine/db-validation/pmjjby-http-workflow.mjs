// Real frontend service/controller -> isolated HTTP FastAPI fixture. No browser or government approval.
import assert from 'node:assert/strict';
import { ApiClient } from '../../frontend/src/services/apiClient.js';
import { ScreeningFlow } from '../../frontend/src/services/screeningFlow.js';
import { speechValue } from '../../frontend/src/services/adapters.js';
const client=new ApiClient('http://127.0.0.1:8011');
assert.equal((await client.get('/health')).scope,'SIMULATED FIXTURE ONLY');
const api={start:(scheme_id,language)=>client.post('/api/v1/questionnaire/start',{scheme_id,language}),
 next:state=>client.post('/api/v1/questionnaire/next',{state}),
 answer:(state,question_id,action,value)=>client.post('/api/v1/questionnaire/answer',
    {state,question_id,action,...(action==='answer'?{value}:{})}),
 explain:state=>client.post('/api/v1/results/explain',{state}),clearSession:()=>{}};
const catalog=await client.get('/api/v1/schemes?lang=en');
assert.equal(catalog.items.length,1);assert.match(catalog.items[0].name,/SIMULATED/);
const id=catalog.items[0].id;assert.equal(id,'pmjjby-workflow-fixture');
assert.match((await client.get('/api/v1/schemes/'+id)).description,/SIMULATED/);
const outcomes=[];
for(const language of ['en','hi'])for(const scenario of ['eligible','ineligible','uncertain']){
 const flow=new ScreeningFlow(api);await flow.start(id,language);const asked=[];
 while(!flow.current.completed){
  const q=flow.current.current_question;assert.equal(q.content_language,language);asked.push(q.question_id);
  const before=JSON.stringify(flow.current.state);
  const recognized=speechValue(q,language==='hi'?'हाँ':'yes');
  assert.equal(JSON.stringify(flow.current.state),before); // recognition alone never submits
  await flow.update(q.question_id,'answer',scenario==='uncertain'?null:scenario==='ineligible'?false:recognized);
 }
 const result=await flow.finish();
 assert.equal(result.status,{eligible:'ELIGIBLE',ineligible:'INELIGIBLE',uncertain:'NEEDS_VERIFICATION'}[scenario]);
 assert.equal(new Set(asked).size,asked.length);assert.equal(asked.length,scenario==='ineligible'?1:3);
 assert.ok(result.raw.sources.length);assert.ok(result.raw.required_documents.items.length);
 assert.ok(result.raw.application_guidance.items.length);assert.equal(result.application_urls.length,0);
 outcomes.push({language,scenario,status:result.status,questions:asked.length});flow.clear();assert.equal(flow.current,null);
}
console.log(JSON.stringify({scope:'synthetic_local_HTTP_frontend_services_not_browser_or_real_policy',outcomes,
 voice_recognition_simulated:true,voice_confirmation_service_semantics_passed:true,real_government_decision:false},null,2));
