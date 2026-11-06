const M=require('../dist/model.js'),fs=require('fs'),assert=require('assert');
let cases=[],roundtrips=0,periods=0,controls=0;
for(let q=2;q<=64;q++)for(let a=0;a<2;a++)for(let b=0;b<q;b++)for(let h=0;h<2;h++){
 const s=[a,b,h];for(const e of 'ABJ'){
  assert.deepStrictEqual(M.step(M.step(s,q,e),q,e,true),s);
  assert.deepStrictEqual(M.step(M.step(s,q,e,true),q,e),s);roundtrips+=2;
  cases.push(M.receipt(s,q,e));
 }
 const period=q%2?4*q:q,trace=M.run(s,q,'J'.repeat(period));
 assert.deepStrictEqual(trace.at(-1),s);
 assert(!trace.slice(1,-1).some(x=>JSON.stringify(x)===JSON.stringify(s)));periods++;
}
for(const bad of [()=>M.state([0,0,0],NaN),()=>M.state([0,3,0],3),()=>M.state([false,0,0],3),()=>M.state([0,0,2],3),()=>M.labels('AX'),()=>M.labels('J'.repeat(513)),()=>M.periods([]),()=>M.periods([1]),()=>M.periods([2.5]),()=>M.periods([Infinity]),()=>M.step([0,0,0],3,'X')]){assert.throws(bad);controls++;}
fs.writeFileSync('test-vectors.json',JSON.stringify(cases));
fs.writeFileSync('node-results.json',JSON.stringify({roundtrip_identities:roundtrips,full_period_minimality_states:periods,invalid_input_controls:controls,reference_vectors:cases.length},null,2));
console.log({roundtrips,periods,controls,vectors:cases.length});
