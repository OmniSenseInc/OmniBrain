"""Scoped, revisioned agency case ledger. No network or tool execution.

CLI identity/role must be supplied by a trusted operator, never client message text.
This is a ledger gate, not authentication of Hermes or its other tools.
"""
import argparse
import copy
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from assessment_v3 import assess, load_bank

STAGES = ['lead','intake','discovery','diagnosis','options','handoff','proposal',
          'onboarding','pilot','delivery','adoption','evaluation','closed']
RESERVED = {'tenant_id','case_id','stage','revision','scope_version','resume_stage'}


def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def nonempty(v):
    return isinstance(v,str) and bool(v.strip())


def require(data, *keys):
    missing = []
    for key in keys:
        v=data
        for part in key.split('.'):
            v=v.get(part) if isinstance(v,dict) else None
        if not nonempty(v):missing.append(key)
    if missing:raise ValueError('Belum lengkap: '+', '.join(missing))


def approval(record, kind, party, bank):
    a=record['data'].get('approvals',{}).get(kind,{}).get(party,{})
    return (isinstance(a,dict) and a.get('approved') is True and nonempty(a.get('approved_by'))
            and nonempty(a.get('source_ref')) and a.get('scope_version')==record['scope_version']
            and a.get('case_id')==record['case_id'] and a.get('tenant_id')==record['tenant_id']
            and a.get('bank_revision')==bank.get('bank_revision'))


def gate(record, target, bank):
    d=record['data']
    if target=='intake':
        require(d,'scope.process','scope.problem','coordinator')
    elif target=='discovery':
        require(d,'scope.process','scope.problem','scope.data_scope')
    elif target=='diagnosis':
        require(d,'process_map_ref','baseline.metric','baseline.unit','baseline.period','baseline.source')
        if isinstance(d['baseline'].get('value'),bool) or not isinstance(d['baseline'].get('value'),(int,float)) or d['baseline']['value']<0:
            raise ValueError('Baseline membutuhkan angka nyata dengan satuan/periode')
    elif target=='options':
        require(d,'diagnosis.selected_cause','diagnosis.evidence_ref')
        if d.get('unresolved_conflicts'):raise ValueError('Selesaikan pertentangan bukti dahulu')
    elif target=='handoff':
        require(d,'handoff.summary','handoff.decision_needed','handoff.recipient')
        payload=d.get('assessment_payload')
        if not isinstance(payload,dict):raise ValueError('Payload penilaian diperlukan')
        if payload.get('context',{}).get('process')!=d['scope']['process']:
            raise ValueError('Penilaian harus merujuk proses pada scope kasus')
        if payload.get('context',{}).get('baseline')!=d.get('baseline'):
            raise ValueError('Baseline penilaian berbeda dari kasus')
        d['assessment_result']=assess(payload,bank)
    elif target=='proposal':
        require(d,'handoff.reviewed_by','handoff.review_ref')
        if d['handoff'].get('status')!='accepted_by_team':raise ValueError('Handoff belum diterima tim')
    elif target=='onboarding':
        require(d,'commercial.scope_ref','commercial.terms_ref','commercial.owner','technical_owner','client_owner')
        if not all(approval(record,'commercial',p,bank) for p in ['team','client']):raise ValueError('Persetujuan scope/termin kedua pihak diperlukan')
    elif target=='pilot':
        result=assess(d.get('assessment_payload',{}),bank)
        if result['route'] not in ['rancang_pilot_fondasi','rancang_pilot_non_ai','rancang_pilot_ai']:
            raise ValueError('Pilot tertahan: '+result['route'])
        if not all(approval(record,'pilot',p,bank) for p in ['team','client']):raise ValueError('Persetujuan pilot kedua pihak diperlukan')
        d['assessment_result']=result
    elif target=='delivery':
        require(d,'pilot_result.metrics_ref','pilot_result.evaluator','pilot_result.measured_period')
        if d['pilot_result'].get('status')!='accepted':raise ValueError('Pilot belum diterima berdasarkan hasil')
        if not all(approval(record,'go_live',p,bank) for p in ['team','client']):raise ValueError('Persetujuan go-live kedua pihak diperlukan')
    elif target=='adoption':
        require(d,'go_live_receipt.source_ref','go_live_receipt.timestamp','adoption_owner','operating_guide_ref','support_plan_ref')
        if d['go_live_receipt'].get('status')!='confirmed':raise ValueError('Belum ada bukti go-live')
    elif target=='evaluation':
        require(d,'usage.metric','usage.period','usage.source_ref','outcome_comparison_ref')
        if isinstance(d['usage'].get('value'),bool) or not isinstance(d['usage'].get('value'),(int,float)) or d['usage']['value']<0:
            raise ValueError('Pemakaian nyata harus diukur; nol merupakan hasil sah')
    elif target=='closed':
        require(d,'evaluation.reviewer','evaluation.source_ref','evaluation.reason','handover_ref')
        if d['evaluation'].get('decision') not in ['continue','improve','stop']:
            raise ValueError('Keputusan evaluasi belum jelas')
        if d['evaluation']['decision'] in ['continue','improve']:
            require(d,'followup.owner','followup.action')


def transition(record,event,actor,bank):
    if actor.get('role') not in ['operator','team'] or not nonempty(actor.get('id')):
        raise ValueError('Identitas operator tepercaya diperlukan; klien tidak dapat mengubah ledger')
    if isinstance(event.get('expected_revision'),bool) or event.get('expected_revision')!=record['revision']:
        raise ValueError('Revisi usang; baca kasus terbaru')
    r=copy.deepcopy(record);patch=event.get('data',{})
    if not isinstance(patch,dict) or RESERVED.intersection(patch):raise ValueError('Field identitas/tahap tidak boleh ditimpa')
    # Approval records can only be recorded by the team role from actual decision evidence.
    if 'approvals' in patch and actor['role']!='team':raise ValueError('Pencatatan persetujuan adalah fungsi tim')
    material={'scope','baseline','diagnosis','assessment_payload','commercial'}
    scope_changed=any(k in patch and canonical(patch[k])!=canonical(r['data'].get(k)) for k in material)
    r['data'].update(copy.deepcopy(patch))
    if scope_changed:
        r['scope_version']+=1
        for k in ['approvals','assessment_result','assessment_payload','pilot_result','go_live_receipt','usage','evaluation']:
            if k=='approvals' or k not in patch:r['data'].pop(k,None)
        if r['stage']=='deferred':
            if r.get('resume_stage') not in ['lead','intake','discovery']:r['resume_stage']='discovery'
        elif r['stage'] not in ['lead','intake','discovery']:r['stage']='discovery'
    action=event.get('action')
    if scope_changed and action!='update':raise ValueError('Ubah scope melalui update terpisah; bukti/persetujuan lama dibatalkan')
    if action=='advance':
        if r['stage'] not in STAGES[:-1]:raise ValueError('Kasus tidak dapat maju dari tahap ini')
        target=STAGES[STAGES.index(r['stage'])+1];gate(r,target,bank);r['stage']=target
    elif action=='defer':
        if r['stage'] in ['deferred','closed']:raise ValueError('Kasus sudah ditunda atau ditutup')
        require(r['data'],'defer_reason');r['resume_stage']=r['stage'];r['stage']='deferred'
    elif action=='resume':
        if r['stage']!='deferred':raise ValueError('Kasus tidak sedang ditunda')
        r['stage']=r.pop('resume_stage')
    elif action!='update':raise ValueError('Action tidak dikenal')
    r['revision']+=1
    return r


def apply_event(db_path,tenant,case,event,actor,bank,commit=False):
    if actor.get('role') not in ['operator','team'] or not nonempty(actor.get('id')):
        raise ValueError('Identitas operator tepercaya diperlukan')
    if not all(nonempty(v) for v in [tenant,case,event.get('id')]):raise ValueError('Tenant,case,eventID diperlukan')
    request_hash=hashlib.sha256(canonical({'event':event,'actor':actor}).encode()).hexdigest()
    path=Path(db_path)
    if not commit:
        if not path.exists():record=None
        else:
            with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)) as c:
                row=c.execute('select body from cases where tenant=? and case_id=?',(tenant,case)).fetchone();record=json.loads(row[0]) if row else None
        record=record or dict(tenant_id=tenant,case_id=case,stage='lead',revision=0,scope_version=0,data={})
        return {'committed':False,'case':transition(record,event,actor,bank)}
    path.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(path,timeout=15)) as c, c:
        c.execute('create table if not exists cases(tenant text,case_id text,body text,primary key(tenant,case_id))')
        c.execute('create table if not exists events(tenant text,case_id text,event_id text,request_hash text,body text,primary key(tenant,case_id,event_id))')
        c.execute('BEGIN IMMEDIATE')
        prev=c.execute('select request_hash,body from events where tenant=? and case_id=? and event_id=?',(tenant,case,event['id'])).fetchone()
        if prev:
            if prev[0]!=request_hash:raise ValueError('EventID sudah digunakan untuk isi berbeda')
            return {'committed':True,'idempotent':True,'case':json.loads(prev[1])}
        row=c.execute('select body from cases where tenant=? and case_id=?',(tenant,case)).fetchone()
        record=json.loads(row[0]) if row else dict(tenant_id=tenant,case_id=case,stage='lead',revision=0,scope_version=0,data={})
        new=transition(record,event,actor,bank)
        body=canonical(new)
        c.execute('insert or replace into cases values(?,?,?)',(tenant,case,body))
        c.execute('insert into events values(?,?,?,?,?)',(tenant,case,event['id'],request_hash,body))
        return {'committed':True,'idempotent':False,'case':new}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default=str(Path(__file__).with_name('data')/'pipeline.sqlite3'))
    p.add_argument('--tenant',required=True);p.add_argument('--case',required=True);p.add_argument('--event-file',required=True)
    p.add_argument('--actor',required=True);p.add_argument('--role',choices=['operator','team'],required=True)
    p.add_argument('--commit',action='store_true',help='Tanpa opsi ini hanya dry-run, tidak menulis')
    a=p.parse_args()
    try:
        r=apply_event(a.db,a.tenant,a.case,json.loads(Path(a.event_file).read_text()),
                      {'id':a.actor,'role':a.role},load_bank(Path(__file__).with_name('pertanyaan_v3.json')),a.commit)
        print(json.dumps(r,ensure_ascii=False,indent=2))
    except (ValueError,KeyError,TypeError,sqlite3.Error,OSError) as e:p.exit(2,'Ditolak: '+str(e)+'\n')
