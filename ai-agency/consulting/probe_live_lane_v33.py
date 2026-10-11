import sys,asyncio,json,tempfile,importlib.util
from pathlib import Path
from types import SimpleNamespace

root=Path(sys.argv[1])
sys.path[:0]=['/home/ubuntu/.hermes/hermes-agent',str(root/'consulting')]
from dotenv import load_dotenv
load_dotenv('/home/ubuntu/.hermes/.env')
from agent.plugin_llm import PluginLlm
from consultation_gateway import Store,SYSTEM,digest
from test_consultation_gateway import fixture
from gateway.session import SessionSource
from gateway.config import Platform
from gateway.platforms.base import MessageEvent,SendResult
spec=importlib.util.spec_from_file_location('omni_live_probe',root/'hermes-plugin/__init__.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class Live:
    async def acomplete(self,**kw):
        assert 'tools' not in kw
        assert 'HASIL PERHITUNGAN SERVER' in kw['messages'][0]['content']
        assert kw['messages'][1]['role']=='user'
        assert 'server_result' not in json.loads(kw['messages'][1]['content'].split('\n')[1])
        self.result=await PluginLlm(plugin_id='omnisense-consultation').acomplete(**kw)
        return self.result

async def main():
    sent=[]
    class Transport:
        async def send(self,chat,text):
            sent.append(text);return SendResult(success=True,message_id='synthetic-output')
    with tempfile.TemporaryDirectory() as tmp:
        store=Store(Path(tmp)/'data');llm=Live();lane=mod.ConsultationLane(store,llm,SYSTEM)
        src=SessionSource(platform=Platform('whatsapp'),chat_id='synthetic-client',user_id='synthetic-client',chat_type='dm')
        run=SimpleNamespace(_adapter_for_source=lambda s:Transport())
        p=fixture(store.bank)
        p['context']={'process':'Laporan operasional mingguan','problem':'Laporan disusun manual dari spreadsheet dan pencarian dokumen lambat. Durasi serta tingkat kesalahan belum diukur.','process_owner':'Operator'}
        ticket=store.create(p,True,'browser','f'*32)
        await lane.handle(MessageEvent(text=ticket['claim_code'],source=src,message_id='s0'),run,digest('synthetic-client'),'synthetic-client')
        await lane.handle(MessageEvent(text='Tim mengumpulkan spreadsheet dari beberapa bagian, lalu menyalin dan mencocokkan datanya secara manual.',source=src,message_id='s1'),run,digest('synthetic-client'),'synthetic-client')
        raw=llm.result.text.strip()
        result={'model_success':bool(raw),'personalized_reply_used':sent[-1].startswith(raw+'\n\n'),'application_question_appended':'Bagaimana urutan' in sent[-1],'reply_quality_guard':mod.usable_reply(raw),'transport':'simulated; no WhatsApp sent','database':'temporary; removed','reply':sent[-1]}
        assert all(result[k] for k in ['model_success','personalized_reply_used','application_question_appended','reply_quality_guard'])
        Path('/home/ubuntu/ai-agency/consulting/live-lane-after-topup-v33.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False))
asyncio.run(main())
