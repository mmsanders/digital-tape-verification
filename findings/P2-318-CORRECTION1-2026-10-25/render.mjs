// Independent logical test DOM over exact production renderer and actual CI views.
// No browser, application, Windows controls, child or device is run.
import {readFileSync} from 'node:fs';
import {mountScreen} from './renderer.mjs';
import {mountScreen as oldMount} from './old-renderer.mjs';
class E {
 constructor(doc,tag){this.ownerDocument=doc;this.tagName=tag;this.children=[];this.dataset={};this.style={};this.listeners={};this.hidden=false;this.textContent='';this.value='';}
 setAttribute(k,v){this[k]=v;} removeAttribute(k){delete this[k];}
 append(...n){this.children.push(...n);}replaceChildren(...n){this.children=n;}
 addEventListener(k,f){this.listeners[k]=f;}removeEventListener(k){delete this.listeners[k];}remove(){}
}
const doc={createElement(t){return new E(doc,t);}};
const input=JSON.parse(readFileSync(new URL('./raw/correction1.json',import.meta.url)));
const recorded=JSON.parse(readFileSync(new URL('./dom-corrected.json',import.meta.url)));
let diagnostics=0,controlMisses=0;
for(const [id,{view,details}] of Object.entries(input.details_views)){
 const need=!id.endsWith('/one64')&&!id.endsWith('/fresh-success-after-failure');
 const root=new E(doc,'main');let calls=0;
 const screen=mountScreen(root,{details:()=>{calls++;return details;}});screen.render(view);
 const el=Object.fromEntries(root.children[0].children.filter(n=>n.id).map(n=>[n.id,n]));
 if(el['show-details'].hidden===need||!el.make.disabled||el.card.textContent!==view.card_line)throw Error(id+' binding');
 if(need){el['show-details'].listeners.click();await Promise.resolve();
  if(el.details.hidden||el.details.textContent!==details||calls!==1)throw Error(id+' click/details');diagnostics++;}
 const saved=recorded.rows[id];
 if(saved.show_details_visible!==need||saved.make_disabled!==true||saved.card!==el.card.textContent||saved.details_calls!==calls)throw Error(id+' producer mismatch');
 screen.destroy();
 const old=oldMount(root,{details:()=>details});old.render(view);
 const oldShow=root.children[0].children.find(n=>n.id==='show-details');
 if(need&&oldShow.hidden)controlMisses++;
 old.destroy();
}
if(diagnostics!==8||controlMisses!==8)throw Error('control did not detect old defect');
console.log('PASS independent production-renderer test-DOM: 12 views,8 diagnostics reachable/exact current text,4 plain successes hidden; old renderer misses8/8 diagnostics. No native UI claim.');
