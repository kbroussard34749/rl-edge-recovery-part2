"""Local-only live policy demonstration, backed by actual simulator steps."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,parse_qs
import json
import recovery as r
HTML=r'''<!doctype html><html lang="en"><meta charset="utf-8"><title>Simulated Edge Recovery — Live Agent Demo</title><style>body{font:20px Arial;background:#fafafa;color:#111;margin:30px;max-width:1100px}h1{font-size:32px}button,select{font-size:18px;padding:9px;margin:8px}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{text-align:left;padding:13px;border-bottom:1px solid #aaa}pre{white-space:pre-wrap;font-size:17px}#action{font-size:24px}#note{font-size:18px}</style><h1>Fault recovery in a simulated edge cluster</h1><p>Live simulator and retained policy · Simulation only · No infrastructure control</p><label>Controller <select id="controller"><option value="filtered">Filtered Q-learning</option><option value="unshielded">Unshielded Q-learning</option><option value="rule">Rule controller</option></select></label><label>Scenario <select id="scenario"></select></label><button onclick="load()">Run agent</button><button onclick="advance()">Next step</button><button onclick="play()">Play episode</button><p id="note"></p><div id="action" aria-live="polite"></div><table><thead><tr><th>Node</th><th>Health</th><th>CPU / 10</th><th>Memory / 10</th></tr></thead><tbody id="nodes"></tbody></table><p id="services"></p><p id="metrics"></p><pre id="details"></pre><script>let episode=[],index=0,timer;const el=id=>document.getElementById(id);async function init(){const data=await(await fetch('/scenarios')).json();for(const s of data){const o=document.createElement('option');o.value=s.id;o.textContent=s.id+' ('+s.split+')';el('scenario').append(o)}el('scenario').value='node_0';await load()}async function load(){clearInterval(timer);const data=await(await fetch('/run?controller='+el('controller').value+'&scenario='+el('scenario').value)).json();episode=data.trace;index=0;el('note').textContent='Final training seed 1000. Split: '+data.summary.split+'. Results are not a production-safety guarantee.';show()}function show(){const t=episode[index];if(!t)return;el('action').textContent='Step '+t.step+': proposed '+t.proposed+' → executed '+t.executed+(t.replaced?' (filtered)':'');el('nodes').innerHTML=t.next_state.health.map((h,n)=>'<tr><td>N'+(n+1)+'</td><td>'+(h?'healthy':'failed')+'</td><td>'+t.loads[0][n]+'</td><td>'+t.loads[1][n]+'</td></tr>').join('');el('services').textContent=['Web','Database','Batch'].map((s,i)=>s+': '+(t.availability[i]?'available':'unavailable')+' on N'+(t.next_state.place[i]+1)).join(' | ');el('metrics').textContent='Reward: '+t.reward+' | Steps remaining: '+t.next_state.left+' | Recovery: '+(t.success?'success':'not reached')+' | Prohibited proposal: '+t.prohibited+' | Executed violation: '+t.violations;el('details').textContent='State seen during training: '+t.seen+'\nInvalid command: '+t.invalid+'\n'+(index===episode.length-1?'Episode ended.':'')}function advance(){if(index<episode.length-1){index++;show()}else clearInterval(timer)}function play(){clearInterval(timer);timer=setInterval(advance,800)}init();</script></html>'''
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/': payload=HTML.encode(); kind='text/html; charset=utf-8'
        elif u.path=='/scenarios': payload=json.dumps(r.manifest()).encode(); kind='application/json'
        elif u.path=='/run':
            params=parse_qs(u.query); c=params.get('controller',['filtered'])[0]; sid=params.get('scenario',['node_0'])[0]
            if c not in ('filtered','unshielded','rule'): self.send_error(400); return
            scenario=next((x for x in r.manifest() if x['id']==sid),None)
            if scenario is None: self.send_error(400); return
            q={} if c=='rule' else {r.state_from(x['state']):x['values'] for x in json.loads((r.ROOT/'outputs'/'final'/c/'1000'/'policy.json').read_text())}
            rows,ts=r.evaluate(q,[scenario],c,1000,scenario['split'])
            for t in ts:
                s=r.state_from(t['next_state']); t['loads']=r.loads(s); t['availability']=r.available(s);t['seen']=c=='rule' or r.state_from(t['state']) in q
            payload=json.dumps(dict(summary=rows[0],trace=ts)).encode();kind='application/json'
        else: self.send_error(404); return
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
if __name__=='__main__':
    print('Live simulation demo: http://127.0.0.1:8765',flush=True)
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
