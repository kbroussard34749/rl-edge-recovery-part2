"""Simulation-only tabular recovery experiment. No network or infrastructure API."""
from __future__ import annotations
from dataclasses import dataclass, replace, asdict
from functools import lru_cache
from pathlib import Path
import argparse, csv, hashlib, json, random, time
from collections import deque
try:
    import resource
except ImportError:
    resource=None

def peak_rss_bytes():
    if resource is None: return None
    import sys
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if sys.platform=="darwin" else value*1024

ACTIONS = ('restart','throttle_batch','migrate_N1','migrate_N2','migrate_N3','restore_N1','restore_N2','restore_N3','wait')
DEMAND = ((3,2),(4,4),(2,3)) # web, database, batch
ROOT=Path(__file__).resolve().parent

@dataclass(frozen=True)
class State:
    health: tuple
    cpu: tuple
    mem: tuple
    place: tuple
    running: tuple
    throttled: bool=False
    left: int=20

@lru_cache(maxsize=None)
def loads(s):
    cpu=list(s.cpu); mem=list(s.mem)
    for i,n in enumerate(s.place):
        if s.running[i] and s.health[n]:
            cpu[n]+=1 if i==2 and s.throttled else DEMAND[i][0]
            mem[n]+=DEMAND[i][1]
    return tuple(cpu),tuple(mem)

@lru_cache(maxsize=None)
def physical(s):
    c,m=loads(s)
    return tuple(bool(s.running[i] and s.health[n] and c[n]<=10 and m[n]<=10) for i,n in enumerate(s.place))

def available(s):
    p=physical(s)
    return (p[0] and p[1],p[1],p[2])

def success(s):
    c,m=loads(s)
    return all(available(s)) and all(not s.health[n] or (c[n]<=10 and m[n]<=10) for n in range(3))

@lru_cache(maxsize=None)
def transition(s,a):
    """Structural execution first, then separate immediate constraint check."""
    p=physical(s); target=next((i for i in (1,0,2) if not p[i]),None)
    place=list(s.place); running=list(s.running); throttle=s.throttled
    valid=False; cost=0; destination=None
    if a==8: valid=True
    elif a==1:
        valid=bool(running[2] and s.health[place[2]] and not throttle)
        if valid: throttle=True; cost=1
    elif target is not None:
        n=place[target]
        if a==0:
            valid=bool(not running[target] and s.health[n])
            if valid: running[target]=True; cost=1; destination=n
        elif 2<=a<=4:
            destination=a-2
            valid=bool(running[target] and s.health[n] and s.health[destination] and destination!=n)
            if valid: place[target]=destination; cost=3
        elif 5<=a<=7:
            destination=a-5
            valid=bool((not running[target] or not s.health[n]) and s.health[destination])
            if valid: place[target]=destination; running[target]=True; cost=3
    candidate=replace(s,place=tuple(place),running=tuple(running),throttled=throttle,left=max(0,s.left-1))
    c,m=loads(candidate)
    capacity=valid and destination is not None and (c[destination]>10 or m[destination]>10)
    before=available(s); after=available(candidate)
    loss=valid and any(before[i] and not after[i] for i in (0,1))
    return candidate,bool(valid),bool(capacity or loss),cost

@lru_cache(maxsize=None)
def step(s,a,filtered):
    if s.left<=0 or success(s): raise ValueError('Cannot step a terminal state')
    candidate,valid,prohibited,cost=transition(s,a)
    replaced=bool(filtered and prohibited)
    executed=8 if replaced else a
    nxt=replace(s,left=s.left-1) if replaced else candidate
    executed_cost=0 if replaced else cost
    avail=available(nxt); won=success(nxt); failed=nxt.left==0 and not won
    uc=int(not avail[0])+int(not avail[1]); ub=int(not avail[2]); b=int(avail[2] and nxt.throttled)
    reward=-1-10*uc-2*ub-b-executed_cost-5*int(prohibited)-20*int(failed)
    info=dict(proposed=ACTIONS[a],executed=ACTIONS[executed],replaced=int(replaced),invalid=int(not valid),prohibited=int(prohibited),violations=int(prohibited and not replaced),cost=executed_cost,critical_unavailable=uc,batch_unavailable=ub,throttled=b,success=int(won))
    return nxt,reward,bool(won or failed),info

def state_from(d):
    return State(**{k:tuple(v) if isinstance(v,list) else v for k,v in d.items()})

def manifest():
    scenarios=[]
    for fault in ('crash','cpu','memory','node'):
        for v in range(6):
            host=v%3; cpu=[0]*3; mem=[0]*3
            cpu[(host+1)%3]=v//3; mem[(host+2)%3]=v//3
            before=State((True,)*3,tuple(cpu),tuple(mem),(host,)*3,(True,)*3)
            after=before
            if fault=='crash':
                run=[True]*3; run[v%3]=False; after=replace(before,running=tuple(run))
            elif fault=='cpu':
                cpu[host]=2+v%3; after=replace(before,cpu=tuple(cpu))
            elif fault=='memory':
                mem[host]=2+v%3; after=replace(before,mem=tuple(mem))
            else:
                health=[True]*3; health[host]=False; after=replace(before,health=tuple(health))
            scenarios.append(dict(id=f'{fault}_{v}',fault=fault,split='train' if v<3 else 'validation' if v==3 else 'test',before=asdict(before),initial=asdict(after)))
    return scenarios

def feasible(initial):
    """Development-only BFS; never supplies training labels or a policy."""
    queue=deque([(initial,0)]); seen={replace(initial,left=20)}; edges=0
    shortest=None
    while queue:
        s,depth=queue.popleft()
        if success(s):
            if shortest is None: shortest=depth
            continue
        if depth>=20: continue
        for a in range(9):
            nxt,r,done,info=step(s,a,True); edges+=1
            if info['violations']: raise AssertionError('Filtered action violation')
            key=replace(nxt,left=20)
            if key not in seen:
                seen.add(key); queue.append((nxt,depth+1))
    return dict(feasible=shortest is not None,shortest_steps=shortest,reachable_physical_states=len(seen),checked_edges=edges)

def greedy(values): return max(range(9),key=lambda a:values[a])

def rule(s):
    candidates=[]
    for a in range(9):
        nxt,valid,bad,cost=transition(s,a)
        if not valid or bad: continue
        av=available(nxt); c,m=loads(nxt)
        overload=sum(s.health[n] and (c[n]>10 or m[n]>10) for n in range(3))
        candidates.append(((int(not av[0])+int(not av[1]),overload,int(not av[2]),cost,a),a))
    return min(candidates)[1]

def update(q,s,a,reward,nxt,done,alpha,gamma=.95):
    values=q.setdefault(s,[0.]*9)
    target=reward+(0 if done else gamma*max(q.get(nxt,[0.]*9)))
    values[a]+=alpha*(target-values[a])

def train(scenarios,alpha,seed,filtered,episodes,folder):
    rng=random.Random(seed); q={}; start=time.perf_counter(); curves=[]; rows=[]
    initial=[state_from(x['initial']) for x in scenarios if x['split']=='train']
    for episode in range(episodes):
        s=rng.choice(initial); total=0; violations=0
        epsilon=1-.9*min(episode/(.8*episodes),1)
        for t in range(20):
            values=q.setdefault(s,[0.]*9)
            a=rng.randrange(9) if rng.random()<epsilon else greedy(values)
            nxt,r,done,info=step(s,a,filtered)
            update(q,s,a,r,nxt,done,alpha)
            total+=r; violations+=info['violations']; s=nxt
            if done: break
        rows.append((episode+1,total,info['success'],t+1,violations))
        if (episode+1)%200==0 or episode+1==episodes:
            recent=rows[-200:]
            curves.append(dict(episode=episode+1,return_mean=sum(x[1] for x in recent)/len(recent),success_mean=sum(x[2] for x in recent)/len(recent),epsilon=epsilon))
    folder.mkdir(parents=True,exist_ok=True)
    with (folder/'episodes.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['episode','return','success','steps','executed_violations']); w.writerows(rows)
    (folder/'curve.json').write_text(json.dumps(curves,indent=2))
    (folder/'policy.json').write_text(json.dumps([dict(state=asdict(s),values=values) for s,values in q.items()]))
    meta=dict(seed=seed,alpha=alpha,filtered=filtered,episodes=episodes,seconds=time.perf_counter()-start,q_states=len(q),nonzero_pairs=sum(v!=0 for values in q.values() for v in values),process_peak_rss_bytes=peak_rss_bytes())
    # macOS reports bytes; Linux reports KiB. Record platform in provenance.
    (folder/'training.json').write_text(json.dumps(meta,indent=2)); return q,meta

def evaluate(q,scenarios,controller,seed,split,trace=True):
    results=[]; traces=[]
    for scenario in scenarios:
        if scenario['split']!=split: continue
        s=state_from(scenario['initial']); total=0; metrics=dict(cost=0,critical_unavailable=0,batch_unavailable=0,throttled=0,prohibited=0,violations=0,replaced=0,invalid=0); unseen=0
        for t in range(20):
            if controller=='rule': a=rule(s)
            else:
                unseen+=int(s not in q); a=greedy(q.get(s,[0.]*9))
            nxt,r,done,info=step(s,a,controller=='filtered')
            total+=r
            for key in metrics: metrics[key]+=info[key]
            if trace: traces.append(dict(controller=controller,seed=seed,scenario=scenario['id'],split=split,step=t+1,state=asdict(s),next_state=asdict(nxt),reward=r,**info))
            s=nxt
            if done: break
        results.append(dict(controller=controller,seed=seed,scenario=scenario['id'],fault=scenario['fault'],split=split,success=info['success'],steps=t+1,return_value=total,unseen=unseen,**metrics))
    return results,traces

def score(rows):
    return (sum(x['success'] for x in rows)/len(rows),-sum(x['critical_unavailable'] for x in rows)/len(rows),sum(x['return_value'] for x in rows)/len(rows))

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def run(episodes=20000):
    import platform
    out=ROOT/'outputs'; out.mkdir(exist_ok=True); scenarios=manifest()
    (ROOT/'scenarios.json').write_text(json.dumps(scenarios,indent=2))
    audit=[dict(id=x['id'],**feasible(state_from(x['initial']))) for x in scenarios]
    if not all(x['feasible'] and success(state_from(scenarios[i]['before'])) for i,x in enumerate(audit)): raise AssertionError('Invalid manifest')
    (out/'scenario_validation.json').write_text(json.dumps(audit,indent=2))
    config=dict(episodes=episodes,gamma=.95,alphas=[.1,.3],tuning_seeds=list(range(100,105)),final_seeds=list(range(1000,1010)),epsilon_initial=1.,epsilon_final=.1,decay_fraction=.8,budget=20,capacity=10,tie_break=list(ACTIONS),rng='Python random.Random',state='exact tuple including remaining budget',heldout_tuning=False)
    (ROOT/'config.json').write_text(json.dumps(config,indent=2))
    start=time.perf_counter(); pilot=[]
    for controller in ('unshielded','filtered'):
        _,meta=train(scenarios,.1,7,controller=='filtered',1000,out/'pilot'/controller); pilot.append(dict(controller=controller,**meta))
    (out/'pilot.json').write_text(json.dumps(pilot,indent=2))
    print('PILOT',json.dumps(pilot),flush=True)
    tuning=[]; selection={}
    for controller in ('unshielded','filtered'):
        scores=[]
        for alpha in (.1,.3):
            pooled=[]
            for seed in range(100,105):
                q,meta=train(scenarios,alpha,seed,controller=='filtered',episodes,out/'tuning'/controller/str(alpha)/str(seed))
                rows,_=evaluate(q,scenarios,controller,seed,'validation',False); pooled+=rows
                tuning+=rows
                print('TUNED',controller,alpha,seed,round(meta['seconds'],2),flush=True)
            scores.append((score(pooled),alpha))
        selection[controller]=max(scores,key=lambda x:x[0])[1]
    write_csv(out/'validation.csv',tuning)
    frozen=dict(config=config,selection=selection,scenario_sha256=hashlib.sha256((ROOT/'scenarios.json').read_bytes()).hexdigest(),selection_rule='mean success, then lower critical outage, then return; alpha .1 wins exact tie',frozen_before_test=True)
    (out/'frozen_protocol.json').write_text(json.dumps(frozen,indent=2))
    results=[]; traces=[]
    for controller in ('unshielded','filtered'):
        for seed in range(1000,1010):
            q,meta=train(scenarios,selection[controller],seed,controller=='filtered',episodes,out/'final'/controller/str(seed))
            for split in ('test','train'):
                rows,ts=evaluate(q,scenarios,controller,seed,split); results+=rows; traces+=ts
            print('FINAL',controller,seed,round(meta['seconds'],2),flush=True)
    for split in ('test','train'):
        rows,ts=evaluate({},scenarios,'rule',None,split); results+=rows; traces+=ts
    write_csv(out/'evaluation.csv',results)
    with (out/'traces.jsonl').open('w') as f:
        for row in traces: f.write(json.dumps(row)+'\n')
    provenance=dict(python=platform.python_version(),platform=platform.platform(),total_seconds=time.perf_counter()-start,total_planned_training_episodes=40*episodes,pilot_episodes=2000,process_peak_rss=peak_rss_bytes(),peak_memory_scope='whole experiment process including transition caches; not isolated per learner',submission_performed=False,publication_performed=False)
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2))
    print('COMPLETE',json.dumps(provenance),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['run','demo','validate']); parser.add_argument('--episodes',type=int,default=20000); parser.add_argument('--scenario',default='cpu_4'); parser.add_argument('--controller',choices=['filtered','unshielded','rule'],default='filtered'); parser.add_argument('--seed',type=int,default=1000)
    args=parser.parse_args()
    if args.command=='run': run(args.episodes)
    elif args.command=='validate':
        print(json.dumps([dict(id=x['id'],**feasible(state_from(x['initial']))) for x in manifest()],indent=2))
    else:
        scenarios=json.loads((ROOT/'scenarios.json').read_text()); scenario=next(x for x in scenarios if x['id']==args.scenario)
        if args.controller=='rule': q={}
        else:
            q={state_from(x['state']):x['values'] for x in json.loads((ROOT/'outputs'/'final'/args.controller/str(args.seed)/'policy.json').read_text())}
        rows,traces=evaluate(q,[scenario],args.controller,args.seed,scenario['split'])
        for row in traces:
            print(json.dumps(row,indent=2))
        print('SUMMARY',json.dumps(rows[0],indent=2))
