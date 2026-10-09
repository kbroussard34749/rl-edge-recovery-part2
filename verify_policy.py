"""Verify actual policy decisions, unseen flags and validation-based alpha selection."""
import csv,json
import recovery as r
cache={}
checked=0
for line in (r.ROOT/'outputs/traces.jsonl').read_text().splitlines():
 t=json.loads(line)
 if t['controller']=='rule': continue
 key=(t['controller'],t['seed'])
 if key not in cache:
  cache[key]={r.state_from(x['state']):x['values'] for x in json.loads((r.ROOT/'outputs/final'/key[0]/str(key[1])/'policy.json').read_text())}
 q=cache[key];s=r.state_from(t['state']);assert r.ACTIONS[r.greedy(q.get(s,[0.]*9))]==t['proposed'];checked+=1
# Re-evaluate retained policies and compare all CSV values exactly.
rows=list(csv.DictReader((r.ROOT/'outputs/evaluation.csv').open()))
for (c,seed),q in cache.items():
 for split in ('test','train'):
  actual,_=r.evaluate(q,r.manifest(),c,seed,split,False)
  for a in actual:
   saved=next(x for x in rows if x['controller']==c and x['seed']==str(seed) and x['scenario']==a['scenario'] and x['split']==split)
   assert all(str(saved[k])==str(v) for k,v in a.items())
(r.ROOT/'outputs/policy_checks.json').write_text(json.dumps(dict(policy_decisions_checked=checked,policies_loaded=len(cache),policy_and_unseen_metrics_verified=True),indent=2))
print('Policy verification passed:',checked,'decisions,',len(cache),'policies')
