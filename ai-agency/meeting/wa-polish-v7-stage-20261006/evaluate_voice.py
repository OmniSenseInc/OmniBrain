"""Real configured model, synthetic direct-WA case, fake send adapter: no real WA delivery."""
import asyncio,importlib.util,json,sys,tempfile,time
from pathlib import Path
from types import SimpleNamespace as NS
from dotenv import load_dotenv
sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent');load_dotenv('/home/ubuntu/.hermes/.env')
from consultation_gateway import Store,SYSTEM
from consultation_voice import context_for_model
from hermes_cli.plugins import discover_plugins,get_plugin_manager,PluginContext
from gateway.config import Platform
spec=importlib.util.spec_from_file_location('voice_plugin',Path(__file__).parent/'plugin_patch.py');plugin=importlib.util.module_from_spec(spec);spec.loader.exec_module(plugin)

async def main():
 discover_plugins();manager=get_plugin_manager();loaded=manager._plugins['omnisense-consultation'];assert loaded.enabled
 llm=PluginContext(loaded.manifest,manager).llm
 with tempfile.TemporaryDirectory(prefix='voice-eval-',dir=Path(__file__).parent) as tmp:
  clock=[time.time()];store=Store(Path(tmp)/'data',clock=lambda:clock[0]);outputs=[];sent=[]
  class Adapter:
   async def send(self,chat,text):sent.append(text);return NS(success=True)
  gateway=NS(_adapter_for_source=lambda s:Adapter())
  lane=plugin.ConsultationLane(store,llm,SYSTEM,staff_check=lambda *args:False)
  source=NS(platform=Platform.WHATSAPP,user_id='628999999999',chat_id='628999999999',chat_type='dm',profile=None)
  n=0
  async def submit(text):
   nonlocal n
   n+=1;clock[0]+=8;before=len(sent)
   event=NS(source=source,text=text,message_id='voice-eval-'+str(n),message_type=NS(value='text'),metadata={},internal=False)
   assert lane.hook(event,gateway)['action']=='skip';await asyncio.gather(*lane.tasks);await asyncio.sleep(0)
   reply=sent[-1] if len(sent)>before else None
   outputs.append({'user':text,'reply':reply});return reply
  for text in ['Saya mau konsultasi bisnis','setuju','Kendala saya ada pada stok gudang yang berbeda dari catatan supply.','Operator mencatat barang masuk dan keluar di spreadsheet.','Selisih terlihat minus di laporan akhir meski pesanan ramai.','Data dipegang manajer dan saya hanya menerima laporan akhir.','Menurutmu saya harus memecat manager atau memakai teknologi baru?','Saya sudah coba menanyai manajer dan karyawan, jawabannya bertentangan. Apa yang bisa dibantu?','saya sudah jelaskan di atas','Kamu bisa build sesuatu untuk membantu proses bisnis ini?','tolong kirim ringkasan ke tim supaya saya bisa berdiskusi langsung','ya','cukup dulu, makasih','oke']:
   await submit(text)
  principal,_=lane.identity(source);row=store.active(principal,source.chat_id);b=json.loads(row['body'])
  assert outputs[-1]['reply'] is None and '?' not in outputs[-2]['reply']
  assert row['status']=='ready_for_team' and b['conversation_closed']
  assert 'success_owner' not in b['discovery']
  with store.db() as c:model_outcomes=dict(c.execute('SELECT outcome,count(*) FROM model_calls GROUP BY outcome'))
  report={'synthetic_case':True,'transport':'fake_adapter','real_whatsapp_messages_sent':False,'model_outcomes':model_outcomes,'closed_once_then_silent':True,'team_queue_preserved':True,'outputs':outputs,'human_language_review_required':True}
  p=Path(__file__).parent/'voice-evaluation.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2));p.chmod(0o600)
  print(json.dumps({k:v for k,v in report.items() if k!='outputs'}))

if __name__=='__main__':asyncio.run(main())
