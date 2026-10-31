// JSX rendering checks through the installed Vite transformer; no new dependencies.
import {test,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'vite';
import React from 'react';
import {renderToString} from 'react-dom/server';
import {StaticRouter} from 'react-router-dom/server.js';
const server=await createServer({server:{middlewareMode:true},appType:'custom'});
after(async()=>{await server.close();delete globalThis.sessionStorage;});
const {LanguageProvider}=await server.ssrLoadModule('/src/i18n/LanguageContext.jsx');
const {ResultCard}=await server.ssrLoadModule('/src/components/results/ResultCard.jsx');
const {DocumentChecklist}=await server.ssrLoadModule('/src/components/results/DocumentChecklist.jsx');
const {PublishedCatalog}=await server.ssrLoadModule('/src/pages/SchemesPage.jsx');
const {adaptResult}=await server.ssrLoadModule('/src/services/adapters.js');
function render(element,language='en'){
 globalThis.sessionStorage={getItem:()=>language,setItem:()=>{},removeItem:()=>{}};
 return renderToString(React.createElement(LanguageProvider,null,React.createElement(StaticRouter,{location:'/'},element)));
}
test('result and checklist render safely without documents or source objects',()=>{
 const result=adaptResult({scheme_id:'synthetic-only',eligibility_status:'NEEDS_VERIFICATION'});
 const html=render(React.createElement(ResultCard,{result}));assert.match(html,/Needs Verification/);assert.doesNotMatch(html,/javascript:/);
 assert.equal(render(React.createElement(DocumentChecklist,{results:[result]})), '');
});
test('Hindi UI preserves English fallback and backend assessment notice',()=>{
 const result=adaptResult({scheme_id:'synthetic-only',eligibility_status:'ELIGIBLE',scheme_name:{text:'Synthetic only',content_language:'en',translation_fallback:true},assessment_notice:{text:'Backend assessment notice',content_language:'en',translation_fallback:true}});
 const html=render(React.createElement(ResultCard,{result}),'hi');assert.match(html,/अंग्रेज़ी/);assert.match(html,/Backend assessment notice/);assert.match(html,/Synthetic only/);
});
test('empty catalog and backend failure are distinct visible states',()=>{
 const empty=render(React.createElement(PublishedCatalog,{data:{items:[]},loading:false}));assert.match(empty,/No published schemes/);
 const offline=render(React.createElement(PublishedCatalog,{error:'Backend unavailable',loading:false}));assert.match(offline,/role="alert"/);assert.doesNotMatch(offline,/No published schemes/);
});
