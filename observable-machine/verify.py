#!/usr/bin/env python3
"""Independent receipt verifier. Python 3.9+, standard library only.
Uses cumulative event counts and integer parity sums, not model.js.
Usage: python verify.py [receipt.json ...]; no arguments runs published witnesses.
"""
import json
import sys
from pathlib import Path

def require(condition, message):
    if not condition:
        raise ValueError(message)

def valid_state(s, q):
    return (isinstance(s, list) and len(s) == 3 and
            all(type(v) is int for v in s) and
            0 <= s[0] < 2 and 0 <= s[1] < q and 0 <= s[2] < 2)

def reference(initial, q, events):
    require(type(q) is int and 2 <= q <= 64, 'invalid q')
    require(valid_state(initial, q), 'invalid initial state')
    require(isinstance(events, str) and len(events) <= 512 and
            all(c in 'ABJ' for c in events), 'invalid event record')
    a0, b0, h0 = initial
    na = nb = total = 0
    trace = [initial[:]]
    for event in events:
        na += event != 'B'
        nb += event != 'A'
        a, b = (a0 + na) % 2, (b0 + nb) % q
        total += (a + b % 2) % 2
        trace.append([a, b, (h0 + total) % 2])
    return trace

def verify(receipt):
    require(isinstance(receipt, dict), 'receipt must be an object')
    require(set(receipt) == {'schema','version','q','input','events','output','trace'}, 'unexpected or missing fields')
    require(receipt['schema'] == 'bog-observable/1' and receipt['version'] == '0.1.0', 'unknown schema/version')
    trace = reference(receipt['input'], receipt['q'], receipt['events'])
    require(valid_state(receipt['output'], receipt['q']), 'invalid output')
    require(isinstance(receipt['trace'], list) and all(valid_state(s,receipt['q']) for s in receipt['trace']), 'invalid trace')
    require(receipt['output'] == trace[-1], 'output mismatch')
    require(receipt['trace'] == trace, 'trace mismatch')
    return True

def preimages(output, q, events, keep_h=True):
    """Independent exhaustive reconstruction: no inverse formula used."""
    return [[a,b,h] for a in range(2) for b in range(q) for h in range(2)
            if reference([a,b,h], q, events)[-1][:3 if keep_h else 2] == output[:3 if keep_h else 2]]

def selftest():
    require(reference([0,0,0],3,'J'*6)[-1] == [0,0,1], 'q=3 phase return')
    require(reference([0,0,0],3,'J'*12)[-1] == [0,0,0], 'q=3 full return')
    require(reference([0,0,0],4,'J'*4)[-1] == [0,0,0], 'q=4 control')
    for q in [3,4]:
        s=[0,q-1,0]
        ab, ba = reference(s,q,'AB')[-1], reference(s,q,'BA')[-1]
        require(ab[:2] == ba[:2], 'phase agreement')
        require((ab == ba) == (q == 4), 'order control')
    print('PASS: 7 published witness/control assertions')

if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            selftest()
        for filename in sys.argv[1:]:
            p = Path(filename)
            require(p.stat().st_size <= 2_000_000, 'receipt too large')
            verify(json.loads(p.read_text(encoding='utf-8')))
            print('PASS:', p.name)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('FAIL:', exc, file=sys.stderr)
        sys.exit(1)
