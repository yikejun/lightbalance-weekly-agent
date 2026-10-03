import copy,datetime,json,tempfile,unittest,uuid
from pathlib import Path
from weekly_service import Store,validate_report,validate_snapshot,configuration,now,PROMPT

def snapshot():
 return {'id':str(uuid.uuid4()),'snapshotAt':now().isoformat(),'plansHash':'a'*64,'plans':[], 'profile':{},'records':[], 'health':{},'windowDays':28}
def report():
 return {'summary':'记录不足','observations':[], 'dataGaps':['训练记录缺失'], 'question':'请补充实际训练，是否先保持？', 'recommendation':'insufficient_data','rationale':'未提供负重与恢复资料','sourceIDs':['acsm-personalize'],'proposedPlans':[]}
class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name)/'db.sqlite')
 def tearDown(self):self.temp.cleanup()
 def test_consent_and_no_call_without_data(self):
  with self.assertRaises(ValueError):self.store.upload(snapshot())
  self.assertEqual(self.store.run(call=lambda _:self.fail('not consented')),'disabled')
  self.store.consent(True);self.assertEqual(self.store.run(call=lambda _:self.fail('no data')),'missing_snapshot')
 def test_full_context_preserved_and_dedup(self):
  self.store.consent(True);s=snapshot();s['health']={'days':[{'values':{'sleep':{'value':7.5,'sources':['Watch']}}}]};self.store.upload(s)
  calls=[]
  def call(data):calls.append(data);return report()
  self.assertEqual(self.store.run(call=call),'awaiting_choice');self.assertEqual(calls[0]['health'],s['health'])
  self.assertEqual(self.store.run(call=lambda _:self.fail('duplicate')),'already_attempted')
  self.store.decide(self.store.inbox()['reports'][0]['week'],'keep')
  self.assertEqual(self.store.inbox()['reports'][0]['state'],'kept')
 def test_failed_attempt_no_automatic_retry(self):
  self.store.consent(True);self.store.upload(snapshot())
  self.assertEqual(self.store.run(call=lambda _:{}),'failed')
  self.assertEqual(self.store.run(call=lambda _:self.fail('retry')),'already_attempted')
 def test_no_fixed_adjustment_and_source_validation(self):
  self.assertIn('是否调整和调整方案由你',PROMPT)
  r=report();r['sourceIDs']=['invented'];self.assertRaises(ValueError,validate_report,r)
  r=report();r['recommendation']='adjust';self.assertRaises(ValueError,validate_report,r)
 def test_stale_and_disable(self):
  self.store.consent(True);s=snapshot();s['snapshotAt']=(now()-datetime.timedelta(days=8)).isoformat()
  self.assertRaises(ValueError,validate_snapshot,s)
  self.store.upload(snapshot());self.store.consent(False)
  self.assertIsNone(self.store.inbox()['snapshotAt'])
 def test_concurrent_disable_does_not_publish(self):
  self.store.consent(True);self.store.upload(snapshot())
  def call(_):self.store.consent(False);return report()
  self.assertEqual(self.store.run(call=call),'cancelled');self.assertIsNone(self.store.inbox()['reports'][0]['payload'])
 def test_photos_rejected(self):
  s=snapshot();s['records']=[{'meals':[]}];self.assertRaises(ValueError,validate_snapshot,s)
 def test_plan_conflict(self):
  from weekly_service import CATALOG
  r=report();r['recommendation']='adjust';r['proposedPlans']=[{'id':str(uuid.uuid4()),'name':'测试计划','exercises':[{'id':str(uuid.uuid4()),'name':CATALOG[0]['name'],'sets':3,'reps':10}]}]
  self.store.consent(True);self.store.upload(snapshot());self.store.run(call=lambda _:r)
  row=self.store.inbox()['reports'][0];self.store.decide(row['week'],'accept');self.store.decide(row['week'],'accept')
  s=snapshot();s['plansHash']='b'*64;self.store.upload(s)
  self.assertRaises(ValueError,self.store.decide,row['week'],'accept')
if __name__=='__main__':unittest.main()
