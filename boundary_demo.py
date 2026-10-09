"""Development boundary fixture, explicitly outside final evaluation benchmark."""
from dataclasses import replace
import json
import recovery as r
s=r.State((True,)*3,(7,0,0),(0,0,0),(0,1,2),(True,False,True))
for filtered in (False,True):
    nxt,reward,done,info=r.step(s,5,filtered)
    print(json.dumps(dict(fixture='restore database to occupied web host; NOT held-out evaluation',filtered=filtered,before=r.asdict(s),after=r.asdict(nxt),reward=reward,**info),indent=2))
