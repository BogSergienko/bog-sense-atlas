/* Observable Machine 0.1.0 — public finite mathematics only. */
(function(root){
'use strict';
const VERSION='0.1.0';
function integer(x,min,max,name){if(!Number.isSafeInteger(x)||x<min||x>max)throw Error(name+' must be an integer from '+min+' to '+max);return x;}
function state(s,q){integer(q,2,64,'q');if(!Array.isArray(s)||s.length!==3)throw Error('State must have three coordinates');integer(s[0],0,1,'a');integer(s[1],0,q-1,'b');integer(s[2],0,1,'h');return s.slice();}
function labels(w){if(typeof w!=='string'||w.length>512||!/^[ABJ]*$/.test(w))throw Error('Use at most 512 event labels A, B or J');return w;}
function step(s,q,e='J',inverse=false){state(s,q);if(!['A','B','J'].includes(e))throw Error('Unknown event');let [a,b,h]=s;const da=e==='B'?0:1,db=e==='A'?0:1;if(inverse){h^=a^(b%2);a=(a-da+2)%2;b=(b-db+q)%q;}else{a=(a+da)%2;b=(b+db)%q;h^=a^(b%2);}return [a,b,h];}
function run(s,q,w){state(s,q);labels(w);let trace=[s.slice()];for(const e of w)trace.push(step(trace.at(-1),q,e));return trace;}
function undo(s,q,w){labels(w);let x=state(s,q);for(const e of [...w].reverse())x=step(x,q,e,true);return x;}
function gcd(a,b){while(b){[a,b]=[b,a%b];}return a;}
function periods(xs){if(!Array.isArray(xs)||xs.length<1||xs.length>6)throw Error('Use 1–6 periods');xs.forEach(x=>integer(x,2,64,'period'));return xs.reduce((a,b)=>a/gcd(a,b)*b,1);}
function candidates(y,q,w,reveal){state(y,q);return (reveal?[y]:[[y[0],y[1],0],[y[0],y[1],1]]).map(s=>undo(s,q,w));}
function receipt(s,q,w){const trace=run(s,q,w);return {schema:'bog-observable/1',version:VERSION,q,input:s.slice(),events:w,output:trace.at(-1),trace};}
const api={VERSION,state,labels,step,run,undo,periods,candidates,receipt};
if(typeof module!=='undefined')module.exports=api;else root.BOG=api;
})(typeof globalThis!=='undefined'?globalThis:this);
