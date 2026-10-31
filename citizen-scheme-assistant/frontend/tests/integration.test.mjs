// Explicit synthetic fixtures only. No government rules or real backend access.
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ApiClient,ApiError} from '../src/services/apiClient.js';
import {schemeApi} from '../src/services/schemeApi.js';
import {sessionApi} from '../src/services/sessionApi.js';
import {ScreeningFlow} from '../src/services/screeningFlow.js';
import {adaptResult,answerValue,speechValue} from '../src/services/adapters.js';
const state={scheme_id:'synthetic-only',answers:{},language:'en',state_version:'1.0',policy_fingerprint:'a'.repeat(64),skipped:[]};
const question=(id,type)=>({question_id:id,attribute:id,text:'Synthetic question',answer_type:type,allowed_values:type==='category'?['code_a','code_b']:type==='boolean'?[true,false]:[],rule_ids:['synthetic-rule'],content_language:'en',translation_fallback:false});
const q=(s=state,current=question('test_age','integer'),reason='QUESTIONS_REMAIN')=>({state:s,current_question:current,completed:current===null,completion_reason:reason,progress:{answered:0,unknown:0,skipped:0,remaining:current?1:0},missing_information:{},evaluation:{status:'NEEDS_VERIFICATION'}});
const raw=(status='NEEDS_VERIFICATION')=>({scheme_id:'synthetic-only',language:'en',eligibility_status:status,scheme_name:{text:'Synthetic only',content_language:'en'},explanation:{text:'Backend explanation',content_language:'en'},required_documents:{status:'unavailable',items:[]},sources:[]});
async function fetched(fn,body){const original=globalThis.fetch;globalThis.fetch=fn;try{return await body();}finally{globalThis.fetch=original;}}

test('selected stable scheme starts with exact API contract and opaque state',async()=>{
 const calls=[];const flow=new ScreeningFlow({start:async(...args)=>{calls.push(args);return q();}});
 await assert.rejects(flow.start('', 'en'));
 await flow.start('synthetic-only','hi');assert.deepEqual(calls,[['synthetic-only','hi']]);assert.strictEqual(flow.current.state,state);
});
test('boolean, integer, decimal and category serialization is strict',()=>{
 assert.equal(answerValue(question('b','boolean'),false),false);
 assert.throws(()=>answerValue(question('b','boolean'),'false'));
 assert.equal(answerValue(question('n','integer'),'18'),18);
 assert.throws(()=>answerValue(question('n','integer'),'18.5'));
 assert.equal(answerValue(question('n','decimal'),'1000.00'),'1000.00');
 assert.equal(answerValue(question('c','category'),'code_b'),'code_b');
 assert.throws(()=>answerValue(question('c','category'),'other'));
 assert.equal(speechValue(question('b','boolean'),'नहीं'),false);
 assert.equal(speechValue(question('n','integer'),'१८'),18);
 assert.throws(()=>speechValue(question('n','integer'),'my income is 18 and 30'));
});
test('adaptive responses choose backend question, skip/clear omit values and completion explains',async()=>{
 const calls=[]; const next=q({...state,answers:{test_age:18}},question('test_flag','boolean'));
 const done=q({...state,skipped:['test_flag']},null,'VERIFICATION_REQUIRED');
 let index=0;
 const flow=new ScreeningFlow({start:async()=>q(),answer:async(...args)=>{calls.push(args);return [next,done,q()][index++];},explain:async s=>{assert.strictEqual(s,done.state);return raw();}});
 await flow.start('synthetic-only','en');await flow.update('test_age','answer','18');
 assert.equal(flow.current.current_question.question_id,'test_flag');assert.equal(calls[0][3],18);
 await flow.update('test_flag','skip');assert.equal(flow.current.completed,true);
 assert.equal((await flow.finish()).status,'NEEDS_VERIFICATION');
 await flow.update('test_flag','clear');assert.equal(calls[2][2],'clear');
 await fetched(async(url,options)=>{const sent=JSON.parse(options.body);assert.deepEqual(sent,{state,question_id:'test_flag',action:'skip'});return Response.json(q());},()=>sessionApi.answer(state,'test_flag','skip'));
});
test('DECISION_REACHED is shown only after explanation succeeds, failures keep state',async()=>{
 const done=q(state,null,'DECISION_REACHED');
 const flow=new ScreeningFlow({start:async()=>done,explain:async()=>{throw new ApiError('NETWORK_ERROR');}});
 await flow.start('synthetic-only','en');await assert.rejects(flow.finish());assert.equal(flow.result,null);assert.strictEqual(flow.current,done);
 flow.api.explain=async()=>raw('ELIGIBLE');assert.equal((await flow.finish()).status,'ELIGIBLE');
});
test('back restores exact prior state through backend next rather than editing answer indexes',async()=>{
 const initial=q(),next=q({...state,answers:{test_age:18}},question('flag','boolean'));let received;
 const flow=new ScreeningFlow({start:async()=>initial,answer:async()=>next,next:async s=>{received=s;return initial;}});
 await flow.start('synthetic-only','en');await flow.update('test_age','answer',18);await flow.back();
 assert.strictEqual(received,initial.state);assert.strictEqual(flow.current,initial);assert.equal(flow.history.length,0);
});
test('clear invalidates pending responses and holds no persistent profile',async()=>{
 let resolve;const flow=new ScreeningFlow({start:()=>new Promise(r=>{resolve=r;})});
 const pending=flow.start('synthetic-only','en');flow.clear();resolve(q());await assert.rejects(pending);assert.equal(flow.current,null);assert.equal(flow.result,null);
});
test('language change reuses state and backend text, never generates translations',async()=>{
 let received;const flow=new ScreeningFlow({start:async()=>q(),next:async s=>{received=s;return q(s);}});
 await flow.start('synthetic-only','en');await flow.language('hi');assert.equal(received.language,'hi');assert.strictEqual(received.answers,state.answers);
 const result=adaptResult({...raw(),language:'hi',scheme_name:{text:'English only',content_language:'en',translation_fallback:true}});
 assert.deepEqual(result.scheme_name,{en:'English only'});assert.equal(result.raw.scheme_name.translation_fallback,true);
});
test('HTTP validation, network and invalid responses fail without mock fallback',async()=>{
 await fetched(async()=>Response.json({error:{code:'INVALID_ANSWERS',fields:['body.answers']}},{status:422}),async()=>{
  await assert.rejects(new ApiClient().post('/api/v1/questionnaire/answer',{}),e=>e.code==='INVALID_ANSWERS'&&e.status===422);
 });
 await fetched(async()=>{throw new TypeError('offline');},async()=>{
  await assert.rejects(schemeApi.getSchemes(),e=>e.code==='NETWORK_ERROR');
  await assert.rejects(sessionApi.explain(state),e=>e.code==='NETWORK_ERROR');
 });
 await fetched(async()=>new Response('<html>unexpected</html>'),async()=>{await assert.rejects(new ApiClient().get('/health'),e=>e.code==='INVALID_RESPONSE');});
});
test('empty published catalog remains empty with only supported query parameters',async()=>{
 await fetched(async url=>{const query=new URL(url).searchParams;assert.equal(query.get('lang'),'hi');assert.equal(query.has('category'),false);return Response.json({items:[],total:0,has_more:false,offset:0,limit:20});},async()=>{
  const result=await schemeApi.getSchemes({language:'hi',category:'ignored'});assert.deepEqual(result.items,[]);assert.equal(result.is_mock,undefined);
 });
});
test('adapter preserves uncertainty and safely omits absent documents, sources and unsafe links',()=>{
 const result=adaptResult({...raw(),required_documents:null,sources:null,official_application_urls:{items:[{url:'javascript:alert(1)'}]}});
 assert.equal(result.status,'NEEDS_VERIFICATION');assert.deepEqual(result.required_documents,[]);assert.deepEqual(result.sources,[]);assert.deepEqual(result.application_urls,[]);
});
