import unittest
from dataclasses import replace
import recovery as r
class ModelTests(unittest.TestCase):
    def setUp(self): self.s=r.State((True,)*3,(0,0,0),(0,0,0),(0,0,0),(True,)*3)
    def test_capacity_boundary_and_throttle_reward(self):
        self.assertTrue(r.success(replace(self.s,cpu=(1,0,0))))
        s=replace(self.s,cpu=(2,0,0)); self.assertFalse(r.success(s))
        nxt,reward,done,info=r.step(s,1,True)
        self.assertEqual(r.loads(nxt)[0][0],10); self.assertEqual(reward,-3); self.assertTrue(done)
    def test_web_dependency_and_wait_reward(self):
        s=replace(self.s,place=(0,1,2),running=(True,False,True))
        self.assertEqual(r.available(s),(False,False,True)); self.assertEqual(r.step(s,8,True)[1],-21)
    def test_blocked_restore_updates_proposal(self):
        s=replace(self.s,place=(0,1,2),running=(True,False,True),cpu=(7,0,0))
        nxt,reward,done,info=r.step(s,5,True)
        self.assertEqual(info['executed'],'wait'); self.assertEqual(info['replaced'],1)
        self.assertEqual(nxt.place,s.place); self.assertEqual(info['violations'],0)
        q={}; r.update(q,s,5,reward,nxt,done,.1)
        self.assertEqual(q[s][5],.1*reward); self.assertEqual(q[s][8],0)
        u,_,_,ui=r.step(s,5,False); self.assertEqual(ui['violations'],1); self.assertTrue(u.running[1])
    def test_restore_failed_node_and_invalid_migration(self):
        s=replace(self.s,health=(False,True,True)); nxt,_,_,info=r.step(s,6,True)
        self.assertEqual(nxt.place[1],1); self.assertFalse(nxt.health[0]); self.assertEqual(info['cost'],3)
        self.assertEqual(r.step(s,3,True)[3]['invalid'],1)
    def test_memory_migration(self):
        nxt,_,done,_=r.step(replace(self.s,mem=(2,0,0)),3,True)
        self.assertTrue(done); self.assertTrue(r.success(nxt)); self.assertEqual(nxt.place[1],1)
    def test_final_step_success_and_failure(self):
        s=replace(self.s,running=(False,True,True),left=1)
        nxt,reward,done,info=r.step(s,0,True); self.assertTrue(done); self.assertTrue(info['success']); self.assertEqual(reward,-2)
        nxt,reward,done,info=r.step(s,8,True); self.assertTrue(done); self.assertFalse(info['success']); self.assertEqual(reward,-31)
        with self.assertRaises(ValueError): r.step(nxt,8,True)
    def test_terminal_no_bootstrap(self):
        s=replace(self.s,running=(False,True,True),left=1); nxt,reward,done,_=r.step(s,0,True)
        q={nxt:[100]*9}; r.update(q,s,0,reward,nxt,done,1); self.assertEqual(q[s][0],reward)
    def test_manifest(self):
        scenarios=r.manifest(); self.assertEqual(len(scenarios),24)
        for fault in ('crash','cpu','memory','node'):
            self.assertEqual([sum(x['fault']==fault and x['split']==sp for x in scenarios) for sp in ('train','validation','test')],[3,1,2])
        starts=[r.state_from(x['initial']) for x in scenarios]; self.assertEqual(len(set(starts)),24)
        for x,s in zip(scenarios,starts):
            self.assertTrue(r.success(r.state_from(x['before']))); self.assertFalse(r.success(s)); self.assertTrue(r.feasible(s)['feasible'])
    def test_critical_loss_filter(self):
        s=replace(self.s,place=(0,1,2),cpu=(7,0,0),mem=(0,0,8))
        nxt,_,_,i=r.step(s,2,True); self.assertEqual(i['replaced'],1); self.assertTrue(r.available(nxt)[0])
if __name__=='__main__': unittest.main()
