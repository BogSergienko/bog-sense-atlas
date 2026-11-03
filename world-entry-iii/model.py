"""BOG OPEN DEMO 001. Original public-safe 2-cycle reversible witness; not R5.
Authorial equation is a research hypothesis, not derived physics.
"""
import json

def c(a,b): return a ^ (b % 2)

def forward(x, p=2, q=3):
    a, b, h = x
    aa, bb = (a+1)%p, (b+1)%q
    return (aa, bb, h ^ c(aa,bb))

def reverse(x, p=2, q=3):
    a, b, h = x
    return ((a-1)%p, (b-1)%q, h ^ c(a,b))

def table(p=2,q=3):
    x=(0,0,0); rows=[]
    for t in range(2*p*q+1):
        a,b,h=x; rows.append({'step':t,'a':a,'b':b,'joint':c(a,b),'memory':h})
        x=forward(x,p,q)
    return rows

def test():
    checks={}
    for p,q in [(2,3),(2,4),(2,5),(2,6)]:
        states=[(a,b,h) for a in range(p) for b in range(q) for h in (0,1)]
        assert all(reverse(forward(x,p,q),p,q)==x for x in states)
        assert all(forward(reverse(x,p,q),p,q)==x for x in states)
        assert len({forward(x,p,q) for x in states})==len(states)
        checks[f'bijective_{p}_{q}']=len(states)
    vals=[c(t%2,t%3) for t in range(6)]
    assert vals==[0,0,0,1,1,1]
    checks['joint_2_3']=vals
    x=(0,0,0)
    for _ in range(6):x=forward(x)
    assert x==(0,0,1);checks['after_6']=list(x)
    for _ in range(6):x=forward(x)
    assert x==(0,0,0);checks['after_12']=list(x)
    assert all(c(t%2,t%4)==0 for t in range(4))
    checks['control_2_4']='joint observable always zero'
    rows=table()
    assert tuple(rows[0][k] for k in ("a","b","joint","memory"))==tuple(rows[-1][k] for k in ("a","b","joint","memory"))
    checks['table_return']='ok'
    return {'passed':len(checks),'checks':checks,'table':rows}

if __name__=='__main__':print(json.dumps(test(),ensure_ascii=False,indent=2))