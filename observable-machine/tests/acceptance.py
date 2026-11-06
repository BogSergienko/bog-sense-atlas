import sys,json,subprocess,random,itertools,math,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'dist'))
from verify import verify,reference,preimages
base=Path(__file__).resolve().parents[1]
subprocess.run(['node',str(base/'tests/test_model.cjs')],cwd=base/'tests',check=True)
vectors=json.loads((base/'tests/test-vectors.json').read_text())
for r in vectors: verify(r)
negative=0
for r in vectors[::199]:
 for field in ['output','trace','version','q']:
  x=copy.deepcopy(r)
  if field=='output':x['output'][2]^=1
  elif field=='trace':x['trace'][0][2]^=1
  elif field=='version':x['version']='wrong'
  else:x['q']=True
  try:verify(x)
  except ValueError:negative+=1
  else:raise AssertionError('mutation survived '+field)
rng=random.Random(20261106); samples=[]
for i in range(250):
 q=rng.randrange(2,17);s=[rng.randrange(2),rng.randrange(q),rng.randrange(2)];w=''.join(rng.choice('ABJ') for _ in range(rng.randrange(41)))
 t=reference(s,q,w);samples.append({'schema':'bog-observable/1','version':'0.1.0','q':q,'input':s,'events':w,'output':t[-1],'trace':t})
 assert preimages(t[-1],q,w)==[s]
 assert len(preimages(t[-1],q,w,False))==2
(base/'tests/history-vectors.json').write_text(json.dumps(samples))
subprocess.run(['node','-e',"const fs=require('fs'),assert=require('assert'),M=require('../dist/model.js');for(const r of JSON.parse(fs.readFileSync('history-vectors.json'))){assert.deepStrictEqual(M.receipt(r.input,r.q,r.events),r);assert.deepStrictEqual(M.undo(r.output,r.q,r.events),r.input);}"],cwd=base/'tests',check=True)
assert math.lcm(6,8,12)==math.lcm(3,8)==24
assert math.lcm(5,8)==40
# Enumerate return structure examples independently.
divs=[2,3,4,6,8,12];structures=[list(x) for n in [2,3] for x in itertools.combinations(divs,n) if math.lcm(*x)==24]
assert len(structures)==12
result=json.loads((base/'tests/node-results.json').read_text())
result.update(independent_reference_vectors_passed=len(vectors),mutated_receipts_rejected=negative,random_histories_exhaustive_preimage_checks=250,history_js_python_parity=250,lcm24_structures=12,status='PASS',scope='Finite models; no physical or secret-engine equivalence claim')
(base/'release-notes/mathematical-tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
