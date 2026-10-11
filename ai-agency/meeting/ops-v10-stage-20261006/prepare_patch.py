from pathlib import Path
import hashlib
r=Path(__file__).resolve().parent
p=r/'consultation_gateway.py';s=p.read_text(encoding='utf-8')
assert 'consultation_adaptive' not in s
s=s.replace('from consultation_dialogue import FIRST_QUESTION','from consultation_adaptive import attach_plan,brief,client_summary,VERSION as TUNING_VERSION\nfrom storage_modes import protect\nfrom consultation_dialogue import FIRST_QUESTION')
s=s.replace("        if os.name=='posix':\n            self.root.chmod(0o700)","        protect(self.root,'directory')")
s=s.replace("        if os.name=='posix':\n            self.path.chmod(0o600)","        protect(self.path)")
assert "        request_hash = digest(canonical(p))" in s
s=s.replace("        request_hash = digest(canonical(p))","        attach_plan(body,QUESTIONS)\n        request_hash = digest(canonical(p))")
s=s.replace("                    tid='CASE-'+secrets.token_hex(8).upper()","                    attach_plan(body,QUESTIONS)\n                    tid='CASE-'+secrets.token_hex(8).upper()")
s=s.replace('https://omnisense.id/privacy.html','https://omnisense.my.id/privacy.html')
s=s.replace("                kind=intent(text)\n                if kind in", "                kind=intent(text)\n                if b.get('consultation_tuning_version')==TUNING_VERSION:\n                    b['clarification_streak']=min(3,b.get('clarification_streak',0)+1) if kind=='unclear' else 0\n                    c.execute('UPDATE tickets SET body=? WHERE id=?',(canonical(b),tid))\n                if kind in")
s=s.replace("                            b['corrections']=(b.get('corrections',[])+[b['followups'][-1]])[-6:]", "                            b['corrections']=(b.get('corrections',[])+[b['followups'][-1]])[-6:]\n                            if b.get('consultation_tuning_version')==TUNING_VERSION:\n                                attach_plan(b,QUESTIONS)\n                                q=current_question(b,row['cursor'],row['status'],QUESTIONS)")
s=s.replace("            cursor += 1", "            if cursor==0 and b.get('consultation_tuning_version')==TUNING_VERSION:\n                attach_plan(b,QUESTIONS)\n            cursor += 1")
s=s.replace("                return self._reply(c,principal,message_id,tid,reply,now)\n            question = QUESTIONS[cursor-1][1]", "                if b.get('consultation_tuning_version')==TUNING_VERSION:\n                    reply=client_summary(b,tid)\n                return self._reply(c,principal,message_id,tid,reply,now)\n            question = current_question(b,cursor,'discovery',QUESTIONS)")
s=s.replace("            'consent':b['consent']}}", "            'consultation_brief':brief(b),\n            'consent':b['consent']}}")
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8')
p=r/'consultation_dialogue.py';s=p.read_text(encoding='utf-8')
s=s.replace('import re','import re\nfrom consultation_adaptive import wording',1)
s=s.replace("    return questions[min(cursor-1,len(questions)-1)][1]", "    return wording(body,cursor,questions) or questions[min(cursor-1,len(questions)-1)][1]")
s=s.replace("https://omnisense.id/privacy.html","https://omnisense.my.id/privacy.html")
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8')
p=r/'web_limits.py';s=p.read_text(encoding='utf-8')
s=s.replace('import os','from storage_modes import protect\nimport os',1)
s=s.replace("        if os.name=='posix':\n            key.chmod(0o600);self.path.chmod(0o600)","        protect(key,'key');protect(self.path)")
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8')
print('Patched adaptive discovery, evidence brief, official privacy URL and shared storage handling.')
