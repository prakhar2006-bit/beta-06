import {test,after} from 'node:test';
import assert from 'node:assert/strict';
import {createServer} from 'vite';
import React from 'react';
import {renderToString} from 'react-dom/server';
import {StaticRouter} from 'react-router-dom/server.js';

const server=await createServer({server:{middlewareMode:true,hmr:false},appType:'custom'});
after(async()=>{await server.close();delete globalThis.sessionStorage;});
const {LanguageProvider}=await server.ssrLoadModule('/src/i18n/LanguageContext.jsx');
const {PublishedCatalog}=await server.ssrLoadModule('/src/pages/SchemesPage.jsx');

for(const language of ['en','hi']){
 test(`informational cards in ${language} link to detail and never screening`,()=>{
  globalThis.sessionStorage={getItem:()=>language,setItem:()=>{}};
  const items=[{id:'synthetic-only',name:'Synthetic only',description:'Not government policy',level:'central',is_demo:true,language}];
  const html=renderToString(React.createElement(LanguageProvider,null,React.createElement(StaticRouter,{location:'/schemes'},React.createElement(PublishedCatalog,{data:{items},loading:false}))));
  assert.match(html,/href="\/schemes\/synthetic-only"/);
  assert.doesNotMatch(html,/href="\/screening/);
  assert.doesNotMatch(html,/DEMO|UNVERIFIED/);
  assert.match(html,language==='en'?/Scheme guide/:/योजना की जानकारी/);
 });
 test(`screenable cards in ${language} provide a real questionnaire action`,()=>{
  globalThis.sessionStorage={getItem:()=>language,setItem:()=>{}};
  const items=[{id:'synthetic-only',name:'Synthetic only',level:'central',is_demo:true,screening_available:true,benefit_highlight:'Synthetic benefit',audience:'Synthetic audience',language}];
  const html=renderToString(React.createElement(LanguageProvider,null,React.createElement(StaticRouter,{location:'/schemes'},React.createElement(PublishedCatalog,{data:{items},loading:false}))));
  assert.match(html,/href="\/screening\?scheme_id=synthetic-only"/);
  assert.match(html,/Synthetic benefit/);assert.match(html,/Synthetic audience/);
 });
}
