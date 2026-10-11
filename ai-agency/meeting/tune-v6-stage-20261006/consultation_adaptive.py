"""Application-owned discovery wording and evidence brief; no authority or score inference."""
import re

VERSION='consultation-tuning-1.2'
PROFILES={
 'stock':r'\b(stok|gudang|inventori|inventory|persediaan)\b',
 'sales':r'\b(penjualan|leads?|prospek|closing|sales)\b',
 'service':r'\b(jadwal|booking|reservasi|janji|antrian|antrean)\b',
 'reporting':r'\b(laporan|rekap|rekonsiliasi|invoice|faktur)\b',
}
PROCESS={
 'stock':'Pada kejadian selisih stok yang Anda ceritakan, bagaimana barang masuk, penjualan, dan perubahan stok dicatat, serta siapa yang memeriksanya?',
 'sales':'Untuk satu calon pelanggan yang pernah tertunda, bagaimana alurnya dari kontak masuk sampai tindak lanjut, dan siapa yang menangani tiap tahap?',
 'service':'Pada satu pesanan atau jadwal yang bermasalah, bagaimana permintaan dicatat, ketersediaan diperiksa, dan konfirmasi diberikan?',
 'reporting':'Untuk satu laporan terakhir, dari mana data dikumpulkan, siapa yang menggabungkannya, dan bagian mana yang harus dikerjakan ulang?',
 'general':'Dari contoh yang sudah Anda ceritakan, bagaimana urutan pengerjaannya dan siapa yang menangani bagian yang tersendat?',
}
METRICS={
 'stock':'frekuensi selisih stok atau pesanan tertunda',
 'sales':'jumlah kontak yang terlewat atau waktu sampai tindak lanjut',
 'service':'jumlah jadwal bermasalah atau waktu menunggu konfirmasi',
 'reporting':'waktu menyusun laporan atau jumlah koreksi',
 'general':'waktu pengerjaan, pekerjaan ulang, atau kesalahan',
}
SIMPLE={
 'process_steps':'Siapa yang mengerjakan bagian ini, lalu pekerjaan diserahkan ke siapa?',
 'impact':'Dalam kejadian terakhir, pekerjaan apa yang tertunda atau harus diulang?',
 'data_permission':'Aplikasi apa yang dipakai untuk proses ini, dan siapa yang boleh memberi izin penggunaannya? Jangan kirim data pelanggan.',
 'previous_attempts':'Pernah mencoba mengubah cara kerja ini? Kalau belum, boleh bilang belum.',
 'success_owner':'Perubahan kecil apa yang paling membantu, dan siapa yang akan memeriksa hasilnya?',
}

def profile(body):
    ctx=body.get('payload',{}).get('context',{})
    corrections=body.get('corrections',[])
    if corrections:
        text=corrections[-1].get('text','')
        text=re.sub(r'\bbukan\b.*?(?=\b(?:tapi|tetapi|melainkan)\b|[,.;]|$)',' ',text,flags=re.I)
    else:text=' '.join(str(ctx.get(k,'')) for k in ('process','problem'))+' '+body.get('input_quality',{}).get('context_clarification','')
    # Specific process wins a generic reporting mention; labels describe text, not diagnosis.
    return next((key for key,pattern in PROFILES.items() if re.search(pattern,text,re.I)),'general')

def attach_plan(body,questions):
    p=profile(body);metric=METRICS[p]
    wording={
      'process_steps':PROCESS[p],
      'impact':'Apa dampak kejadian itu bagi pelanggan atau tim? Jika ada catatan, sebut '+metric+' dan periodenya; kalau belum diukur, satu contoh juga cukup.',
      'data_permission':'Data dan aplikasi apa yang dipakai pada proses ini, siapa penanggung jawabnya, dan apakah penggunaannya diizinkan? Sebut jenisnya saja; jangan kirim data pelanggan atau rahasia.',
      'previous_attempts':'Apa yang sudah dicoba pada proses ini, apa yang terbantu, dan kendala apa yang masih tersisa?',
      'success_owner':'Perubahan apa yang ingin dicapai, ukuran pembanding apa yang bisa dicatat, dan siapa yang akan menjalankan serta meninjau hasilnya?',
    }
    body['consultation_tuning_version']=VERSION
    body['discovery_profile']=p
    body['discovery_plan']=[{'key':key,'question':wording.get(key,q)} for key,q in questions]
    return body

def wording(body,cursor,questions):
    plan=body.get('discovery_plan')
    if body.get('consultation_tuning_version')!=VERSION or not isinstance(plan,list) or len(plan)!=len(questions):return None
    index=min(cursor-1,len(questions)-1)
    item=plan[index]
    if not isinstance(item,dict) or item.get('key')!=questions[index][0] or not isinstance(item.get('question'),str) or len(item['question'])>600:return None
    if body.get('clarification_streak',0)>=2:return SIMPLE.get(item['key'],item['question'])
    return item['question']

def brief(body):
    ctx=body.get('payload',{}).get('context',{})
    discovery=body.get('discovery',{})
    corrections=[{'statement':x.get('text','')[:700],'source':'client_self_report','verified':False} for x in body.get('corrections',[])][-6:]
    statements=[{'topic':k,'statement':str(ctx.get(k,''))[:700],'source':'client_self_report','verified':False} for k in ('process','problem') if ctx.get(k)]
    clarified=body.get('input_quality',{}).get('context_clarification')
    if clarified:statements=[{'topic':'clarified_context','statement':clarified[:700],'source':'client_self_report','verified':False}]
    statements += [{'topic':k,'statement':v.get('answer','')[:700],'source':'client_self_report','verified':False} for k,v in discovery.items() if isinstance(v,dict) and not v.get('unknown')]
    unknown=[{'topic':k,'reason':'client_does_not_know' if discovery.get(k,{}).get('unknown') else 'not_yet_collected'} for k in SIMPLE if k not in discovery or discovery[k].get('unknown')]
    return {'version':VERSION,'reported_statements':statements,'corrections':corrections,'original_context_requires_reconciliation':bool(corrections),'unknowns':unknown,'verified_diagnosis':None,'hypotheses':[],
      'alternatives_to_compare':['perbaikan proses','software siap pakai','otomasi aturan','AI jika bukti mendukung'],
      'evidence_tasks':['Cocokkan alur dan satu contoh kejadian dengan penanggung jawab.','Catat kondisi awal dan ukuran keberhasilan tanpa menebak angka.','Tinjau izin data serta koreksi klien sebelum menentukan scope.'],
      'next_gate':'permission_review' if body.get('risk_hold') else 'human_review','commercial_scope_approved':False,'score_validation':'screening_self_report_not_calibrated'}

def client_summary(body,case_id):
    b=brief(body);ctx=body.get('payload',{}).get('context',{})
    clarification=body.get('input_quality',{}).get('context_clarification')
    title='Konteks awal yang perlu dicocokkan dengan koreksi' if b['corrections'] else 'Yang Anda ceritakan'
    text='Ringkasan awal kasus '+case_id+':\n\n'+title+':\n'+('Penjelasan konteks setelah klarifikasi: '+clarification[:500] if clarification else 'Proses: '+str(ctx.get('process',''))[:160]+'\nHambatan: '+str(ctx.get('problem',''))[:500])
    labels={'problem_example':'Contoh kejadian','process_steps':'Alur proses','impact':'Dampak','data_permission':'Data dan izin','previous_attempts':'Upaya sebelumnya','success_owner':'Tujuan dan penanggung jawab'}
    details=[labels.get(k,k.replace('_',' '))+': '+v.get('answer','')[:180] for k,v in body.get('discovery',{}).items() if isinstance(v,dict) and not v.get('unknown')]
    if details:text+='\n\nPenjelasan pendalaman:\n'+'\n'.join(details)
    if b['corrections']:text+='\n\nKoreksi Anda:\n'+'\n'.join(x['statement'][:220] for x in b['corrections'][-2:])
    if b['unknowns']:text+='\n\nYang masih perlu dipastikan: '+', '.join(x['topic'].replace('_',' ') for x in b['unknowns'])+'.'
    text+='\n\nPenyebab belum terverifikasi. Tim perlu memeriksa contoh proses, ukuran kondisi awal, dan izin data sebelum memilih pendekatan.\n\nBoleh ringkasan ini masuk antrean review tim? Balas “ya”, atau /stop.'
    return text
