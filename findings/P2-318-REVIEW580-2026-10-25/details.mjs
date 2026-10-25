// Diagnostic of the exact production renderer over retained component views.
// A test DOM is not native Windows observation or input.
import {readFileSync,writeFileSync} from 'node:fs';
import {mountScreen} from './source/host/app/frontend/screen.mjs';
class Element {
  constructor(doc,tag){this.ownerDocument=doc;this.tagName=tag;this.children=[];this.dataset={};this.style={};this.listeners={};this.hidden=false;this.textContent='';this.value='';}
  setAttribute(k,v){this[k]=v;}
  removeAttribute(k){delete this[k];}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=nodes;}
  addEventListener(k,f){this.listeners[k]=f;}
  removeEventListener(k){delete this.listeners[k];}
  remove(){}
}
const doc={createElement(tag){return new Element(doc,tag);}};
const root=new Element(doc,'main');
const raw=JSON.parse(readFileSync(new URL('./evidence/discovery.raw.json',import.meta.url)));
let details='';const screen=mountScreen(root,{details:()=>details});
const nodes=()=>Object.fromEntries(root.children[0].children.filter(x=>x.id).map(x=>[x.id,x]));
const results=[];
for(const id of ['zero-unprobed','enum-unavailable']){
  const row=raw.rows.find(x=>x.id===id);details=row.details;
  screen.render(row.view);
  let n=nodes();
  if(!n['show-details'].hidden)throw Error('expected exact-head failure changed');
  results.push({id,actualView:row.view.view,detailsAvailable:row.view.details_available,detailsTextPresent:!!details,showHidden:n['show-details'].hidden});
  // Diagnostic counterfactual isolates the second gate: setting only availability
  // cannot fix this, because discovery leaves Empty/Ready rather than Problem.
  screen.render({...row.view,details_available:true});n=nodes();
  if(!n['show-details'].hidden)throw Error('expected independent state gate changed');
  results.push({id,diagnosticOnly:'availability true; same actual view',showHidden:n['show-details'].hidden});
}
// A reachable Problem illustrates the new poll's effect on an already open panel.
const row=raw.rows.find(x=>x.id==='enum-unavailable');
const problem={...row.view,view:'problem',message:'Something went wrong.',details_available:true};
screen.render(problem);let n=nodes();n['show-details'].listeners.click();await Promise.resolve();
if(n.details.hidden)throw Error('click failed in test DOM');
screen.render(problem);n=nodes();
if(!n.details.hidden)throw Error('expected next-poll collapse changed');
results.push({diagnosticOnly:'Problem panel opened; next identical state emission',detailsHidden:n.details.hidden});
screen.destroy();
writeFileSync(new URL('./DOM-RESULT.json',import.meta.url),JSON.stringify({candidate:'18f424f66bbd0ad9c9f74c930d524627a3a6cf82',class:'production renderer/test DOM only',results},null,2)+'\n');
console.log(JSON.stringify(results,null,2));
