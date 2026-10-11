"""Contract tests against real bank, Python, browser JS and website message parser."""
import copy
import functools
import http.server
import json
import os
import random
import subprocess
import threading
import tempfile
from consultation_server import make_handler
from consultation_gateway import Store, TOKEN, digest
from pathlib import Path
from assessment_v3 import assess, load_bank
from baca_konsultasi_v3 import parse, MARKER

HERE = Path(__file__).resolve().parent
SITE = HERE.parent / 'website'
BANK = load_bank(HERE / 'pertanyaan_v3.json')
passed = 0


def check(name, condition):
    global passed
    if not condition:
        raise AssertionError(name)
    passed += 1
    print('PASS', name)


def fixture(mode='screening'):
    return {'version': '3.0', 'mode': mode,
            'answers': {q['id']: {'value': 5, 'evidence': 'self_reported'} for q in BANK[mode]},
            'context': {'process': 'Ringkasan tiket', 'problem': 'Pencarian lama', 'process_owner': 'Lead support',
                        'baseline': {'metric': 'durasi', 'value': 12, 'unit': 'menit/tiket', 'period': '7 hari', 'source': 'simulasi'},
                        'access_permission': 'confirmed', 'impact': 'low', 'human_review': 'defined', 'fallback': 'defined'}}


# Independent implementations must agree for complete, incomplete and risky inputs.
rng = random.Random(20261004)
cases = []
for i in range(80):
    p = fixture('discovery' if i % 2 else 'screening')
    for a in p['answers'].values():
        a['value'] = rng.choice([None, 1, 2, 3, 4, 5])
        a['evidence'] = rng.choice(['self_reported', 'reviewed', 'observed'])
        a['source'] = 'simulasi: bukti uji'
    p['context']['impact'] = rng.choice(['low', 'medium', 'high', 'unknown'])
    p['context']['access_permission'] = rng.choice(['confirmed', 'denied', 'unknown'])
    cases.append(p)
cases += [fixture(), fixture('discovery')]
for p in cases[-2:]:
    for a in p['answers'].values():
        a.update(evidence='reviewed', source='simulasi: bukti uji')
reviewed = json.loads((HERE / 'input_contoh_discovery_reviewed.json').read_text())
cases.append(reviewed)
for solution in ['process','software','rule_automation']:
    p = copy.deepcopy(reviewed); p['use_case']['solution_type'] = solution; cases.append(p)
p = copy.deepcopy(reviewed)
p['answers']['D3d'].update(value=None,applicability='not_applicable',reason='simulasi tidak perlu migrasi')
cases.append(p)
p = copy.deepcopy(reviewed); p['context']['impact']='high'
p['context']['expert_review']=dict(p['answers']['D7a']['review_record'],status='approved_with_conditions',conditions=['simulasi review'],conditions_met=True)
cases.append(p)
p = copy.deepcopy(reviewed); p['answers']['D4d']['value']=1; cases.append(p)
js = "const fs=require('fs'),m=require(process.argv[1]),b=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));let x=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(x.map(p=>m.assess(p,b))))"
r = subprocess.run(['node', '-e', js, str(SITE / 'assets/konsultasi-v3.js'), str(HERE / 'pertanyaan_v3.json')],
                   input=json.dumps(cases), text=True, capture_output=True, check=True)
browser_scores = json.loads(r.stdout)
keys = ('score', 'band', 'range', 'answer_coverage_percent', 'verified_evidence_coverage_percent',
        'dimensions', 'missing', 'critical_weak', 'critical_unknown', 'critical_unverified', 'context_gaps', 'route', 'deployment_approved',
        'evidence_gaps','not_applicable','consistency_issues','use_case_gaps','pilot_blockers','bank_revision','input_version','next_questions')
for i, (p, actual) in enumerate(zip(cases, browser_scores)):
    expected = assess(p, BANK)
    check('Python/JS parity case ' + str(i), all(expected[k] == actual[k] for k in keys))

p = fixture()
for a in p['answers'].values():
    a.update(evidence='reviewed', source='pengunjung mengklaim diperiksa')
parsed = parse(MARKER + '\n' + json.dumps(p), BANK)
check('Website cannot self-certify reviewed evidence', parsed['verified_evidence_coverage_percent'] == 0)
check('Website message never claims handoff was sent', parsed['handoff']['sent_to_team'] is False)
check('Self-report goes to discovery', parsed['route'] == 'discovery_dan_verifikasi')
for name, message in [('wrong marker', 'not assessment'),
                      ('duplicate field', MARKER + '\n{"version":"3.0","version":"2.0"}'),
                      ('oversized', MARKER + '\n' + 'a' * 50000)]:
    try:
        parse(message, BANK)
    except ValueError:
        check('Parser rejects ' + name, True)
    else:
        check('Parser rejects ' + name, False)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass

test_data=tempfile.TemporaryDirectory()
store=Store(test_data.name)
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), make_handler(SITE,store))
threading.Thread(target=server.serve_forever, daemon=True).start()
out = HERE / 'test-output'
out.mkdir(exist_ok=True)
env = dict(os.environ, PW_CORE='/tmp/camofox/node_modules/playwright-core',
           CHROME_PATH='/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome',
           TEST_URL=f'http://127.0.0.1:{server.server_port}/konsultasi-v3.html', TEST_OUT=str(out))
browser_js = r"""
const {chromium}=require(process.env.PW_CORE),fs=require('fs');
(async()=>{
let b=await chromium.launch({executablePath:process.env.CHROME_PATH});let count=0, payloads=[];
function check(name,x){if(!x)throw new Error(name);count++;console.log('PASS UI '+name)}
for(const [label,width,height]of [['desktop',1280,900],['mobile',390,844]]){
let p=await b.newPage({viewport:{width,height}}),errors=[];
p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
await p.goto(process.env.TEST_URL,{waitUntil:'networkidle'});
check(label+' 16 questions',await p.locator('fieldset').count()===16);
check(label+' unfilled submit disabled',await p.locator('#calculate').isDisabled());
const ids=await p.evaluate(()=>window.OMNISENSE_CONSULTING_V3.screening.map(q=>q.id));
for(const id of ids)await p.locator('input[name="'+id+'"][value="unknown"]').check();
await p.locator('#calculate').click();
check(label+' process context required',(await p.locator('#error').innerText()).includes('Isi proses'));
await p.locator('#process').fill('Rekap laporan <script>alert("x")</script>');
await p.locator('#problem').fill('Waktu pencarian laporan lama; data contoh simulasi');
await p.locator('#calculate').click();
check(label+' unknown yields range',(await p.locator('#score').innerText()).includes('20–100'));
check(label+' no WhatsApp link before consent',await p.locator('#send').getAttribute('href')===null);
await p.locator('#consent').check();
check(label+' consent alone does not send',!(await p.locator('#send').getAttribute('href')).startsWith('https://wa.me/'));
await p.locator('#send').click();await p.waitForFunction(()=>document.getElementById('send').href.startsWith('https://wa.me/'));
let href=await p.locator('#send').getAttribute('href');
check(label+' link points to correct WA',href.startsWith('https://wa.me/6288809640700?text='));
payloads.push(new URL(href).searchParams.get('text'));
check(label+' marker present',payloads.at(-1).includes('[OMNISENSE-KONSULTASI] OS-')&&!payloads.at(-1).includes('script'));
await p.locator('#results details summary').click();
check(label+' text treated literally',(await p.locator('#preview').innerText()).includes('<script>'));
await p.locator('#problem').fill('Konteks berubah');
check(label+' edits invalidate result',await p.locator('#results').isHidden());
check(label+' edits revoke consent',!await p.locator('#consent').isChecked());
check(label+' edits remove WA link',await p.locator('#send').getAttribute('href')===null);
for(const id of ids)await p.locator('input[name="'+id+'"][value="5"]').check();
await p.locator('#calculate').click();
check(label+' all high gets index100',(await p.locator('#score').innerText()).startsWith('100 /'));
check(label+' self report still requires verification',(await p.locator('#route').innerText()).includes('verifikasi'));
await p.locator('#consent').check();await p.locator('#send').click();await p.waitForFunction(()=>document.getElementById('send').href.startsWith('https://wa.me/'));payloads.push(new URL(await p.locator('#send').getAttribute('href')).searchParams.get('text'));
await p.locator('input[name="S2a"][value="1"]').check();await p.locator('#calculate').click();
check(label+' conflicting answers change guidance',(await p.locator('#route').innerText()).includes('klarifikasi'));
await p.locator('#results').screenshot({path:process.env.TEST_OUT+'/'+label+'-results.png'});
await p.locator('#reset').click();
check(label+' reset clears context',await p.locator('#process').inputValue()==='');
check(label+' reset clears all selections',await p.locator('input[type=radio]:checked').count()===0);
check(label+' reset hides results',await p.locator('#results').isHidden());
check(label+' no local storage',await p.evaluate(()=>localStorage.length)===0);
check(label+' no horizontal overflow',await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
check(label+' no JS/console errors',errors.length===0);
await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:process.env.TEST_OUT+'/'+label+'-top.png'});await p.close();
}
fs.writeFileSync(process.env.TEST_OUT+'/browser-payloads.json',JSON.stringify(payloads));
fs.writeFileSync(process.env.TEST_OUT+'/browser-summary.json',JSON.stringify({count}));await b.close();
})().catch(e=>{console.error(e);process.exit(1)})
"""
try:
    r = subprocess.run(['node', '-e', browser_js], env=env, text=True, capture_output=True, timeout=120)
    print(r.stdout)
    if r.returncode:
        raise RuntimeError(r.stderr)
    messages = json.loads((out / 'browser-payloads.json').read_text())
    for i, text in enumerate(messages):
        token=TOKEN.search(text).group(1)
        with store.db() as c:
            body=json.loads(c.execute('SELECT body FROM tickets WHERE token_hash=?',(digest(token),)).fetchone()[0])
        response=body['result']
        check('Real browser message parse ' + str(i), response['version'] == '3.1')
        if i % 2 == 0:
            check('Browser unknown preserved as null ' + str(i), response['score'] is None)
        else:
            check('Browser high self-report not verified ' + str(i), response['score'] == 100 and response['route'] == 'discovery_dan_verifikasi')
    ui = json.loads((out / 'browser-summary.json').read_text())['count']
    summary = {'contract_checks': passed, 'browser_checks': ui, 'parity_cases': len(cases), 'real_browser_messages': len(messages)}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2))
    print('RESULT', json.dumps(summary))
finally:
    server.shutdown()
    server.server_close()
    test_data.cleanup()

