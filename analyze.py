"""Recompute descriptive summaries from retained evaluation CSV."""
from pathlib import Path
import csv,json,statistics,hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'outputs/evaluation.csv').open()))
fields=['success','steps','return_value','critical_unavailable','batch_unavailable','throttled','cost','prohibited','violations','replaced','invalid','unseen']
for row in rows:
    for f in fields: row[f]=float(row[f])
aggregates=[]
for key in sorted(set((r['controller'],r['seed'],r['split']) for r in rows)):
    group=[r for r in rows if (r['controller'],r['seed'],r['split'])==key]
    good=[r for r in group if r['success']]
    a=dict(controller=key[0],seed=key[1],split=key[2],episodes=len(group),success_count=len(good),success_rate=len(good)/len(group),successful_steps=statistics.mean(r['steps'] for r in good) if good else None)
    for f in fields[1:]: a[f+'_mean']=statistics.mean(r[f] for r in group)
    a['unseen_fraction']=sum(r['unseen'] for r in group)/sum(r['steps'] for r in group)
    a['filter_intervention_rate']=sum(r['replaced'] for r in group)/sum(r['steps'] for r in group)
    aggregates.append(a)
summary=[]
for c,sp in sorted(set((r['controller'],r['split']) for r in rows)):
    g=[r for r in aggregates if r['controller']==c and r['split']==sp]
    a=dict(controller=c,split=sp,seeds=len(g),configurations_per_seed=g[0]['episodes'])
    for f in ('success_rate','steps_mean','return_value_mean','critical_unavailable_mean','violations_mean','prohibited_mean','unseen_fraction','filter_intervention_rate'):
        v=[r[f] for r in g]; a[f]=dict(mean=statistics.mean(v),sd=statistics.stdev(v) if len(v)>1 else None,min=min(v),max=max(v))
    summary.append(a)
(ROOT/'outputs/seed_aggregates.json').write_text(json.dumps(aggregates,indent=2))
(ROOT/'outputs/summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
# Every retained evaluation trace is replayed against the implementation.
import recovery as model
traces=[json.loads(line) for line in (ROOT/'outputs/traces.jsonl').read_text().splitlines()]
for t in traces:
    s=model.state_from(t['state']); a=model.ACTIONS.index(t['proposed'])
    nxt,reward,done,info=model.step(s,a,t['controller']=='filtered')
    assert nxt==model.state_from(t['next_state']) and reward==t['reward']
    assert all(t[k]==v for k,v in info.items())
    if t['controller']=='rule': assert a==model.rule(s)
# Aggregate trace totals crosscheck evaluation records, independently of summarize code.
for row in rows:
    g=[t for t in traces if t['controller']==row['controller'] and str(t['seed'] or '')==row['seed'] and t['scenario']==row['scenario'] and t['split']==row['split']]
    assert len(g)==row['steps'] and sum(t['reward'] for t in g)==row['return_value']
    assert g[-1]['success']==row['success']
    for k in ('critical_unavailable','violations','prohibited','replaced','cost','invalid','batch_unavailable','throttled'):
        assert sum(t[k] for t in g)==row[k]
verification=dict(evaluation_rows=len(rows),trace_rows=len(traces),replay_and_metric_checks_passed=True)
(ROOT/'outputs/evidence_checks.json').write_text(json.dumps(verification,indent=2))
print('VERIFIED',verification)
