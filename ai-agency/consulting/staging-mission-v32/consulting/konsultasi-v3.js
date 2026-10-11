(function(root){
'use strict';
const text=x=>typeof x==='string'&&!!x.trim(), obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const r1=n=>Math.round((n+1e-9)*10)/10;
function reviewOK(r,source){
  if(!obj(r)||!['reviewer','reviewed_at','source_ref','scope'].every(k=>text(r[k]))||r.finding!=='supports')return false;
  const d=new Date(r.reviewed_at+'T00:00:00Z');
  if(!/^\d{4}-\d{2}-\d{2}$/.test(r.reviewed_at)||isNaN(d.getTime())||d.toISOString().slice(0,10)!==r.reviewed_at)return false;
  return source===undefined||r.source_ref===source;
}
function expertOK(c){const r=c.expert_review;return obj(r)&&r.status==='approved_with_conditions'&&reviewOK(r)&&Array.isArray(r.conditions)&&r.conditions.length>0&&r.conditions.every(text)&&r.conditions_met===true;}
function useCaseGaps(u){
  if(!obj(u)||!['process','software','rule_automation','ai'].includes(u.solution_type))return ['solution_type'];
  const g=[];for(const k of ['objective','selection_reason'])if(!text(u[k]))g.push(k);
  if(!Array.isArray(u.alternatives)||u.alternatives.length<2||!u.alternatives.every(x=>obj(x)&&text(x.option)&&text(x.reason)))g.push('alternatives');
  if(!obj(u.diagnosis)||!text(u.diagnosis.selected_cause)||!text(u.diagnosis.evidence_ref))g.push('diagnosis');
  for(const k of ['value_case','feasibility'])if(!obj(u[k])||u[k].status!=='supported'||!text(u[k].source_ref))g.push(k);
  if(!obj(u.pilot_plan)||!['owner','scope','success_metric','period','stop_condition','rollback','review_owner'].every(k=>text(u.pilot_plan[k])))g.push('pilot_plan');
  return g;
}
function assess(p,bank){
  if(!obj(p)||!['3.0','3.1'].includes(p.version))throw new Error('Versi harus3.0 atau3.1');
  const mode=p.mode||'screening';if(!['screening','discovery'].includes(mode))throw new Error('Mode tidak dikenal');
  const qs=bank[mode], answers=p.answers===undefined?{}:p.answers, context=p.context===undefined?{}:p.context;
  if(!obj(answers)||!obj(context)||Object.keys(answers).some(k=>!qs.some(q=>q.id===k)))throw new Error('Jawaban/konteks tidak sah');
  if(p.consistency_resolutions!==undefined&&!obj(p.consistency_resolutions))throw new Error('Resolution harus object');
  const norm={},na=[],evidenceGaps=[];
  for(const q of qs){
    const a=answers[q.id]||{};if(!obj(a))throw new Error('Jawaban harus object');
    const v=a.value==null?null:a.value,ev=a.evidence||'self_reported',source=a.source===undefined?'':a.source;
    if(!['self_reported','reviewed','observed'].includes(ev)||typeof source!=='string')throw new Error('Bukti tidak sah');
    if(v!==null&&(!Number.isInteger(v)||v<1||v>5))throw new Error('Nilai harus1–5');
    if(v!==null&&ev!=='self_reported'&&!text(source))throw new Error('Sumber diperlukan');
    if(a.applicability==='not_applicable'){
      if(mode!=='discovery'||!q.allow_not_applicable||q.critical||v!==null||!text(a.reason)||!reviewOK(a.review_record,source))throw new Error('Tidak relevan tidak sah');
      na.push(q.id);
    }
    const documented=ev!=='self_reported'&&reviewOK(a.review_record,source);
    if(v!==null&&ev!=='self_reported'&&!documented)evidenceGaps.push(q.id);
    norm[q.id]={value:v,documented};
  }
  const sumW=bank.dimensions.reduce((s,d)=>s+d.weight,0);
  let low=0,high=0,known=0,verified=0;
  const missing=[],weak=[],unknown=[],unverified=[],dimensions=[];
  for(const d of bank.dimensions){
    const all=qs.filter(q=>q.dimension===d.id),children=all.filter(q=>!na.includes(q.id)),w=d.weight/sumW;
    if(children.length<all.length/2)throw new Error('Butir relevan terlalu sedikit');
    let dl=0,dh=0,n=0;
    for(const q of children){const a=norm[q.id],v=a.value;
      if(v===null){dl+=1;dh+=5;missing.push(q.id);if(q.critical)unknown.push(q.id);}
      else {dl+=v;dh+=v;n++;known+=w/children.length;if(a.documented)verified+=w/children.length;
        if(q.critical&&v<3)weak.push(q.id);if(q.critical&&!a.documented)unverified.push(q.id);}
    }
    dl=dl/children.length*20;dh=dh/children.length*20;low+=w*dl;high+=w*dh;
    dimensions.push({id:d.id,name:d.name,weight_percent:Math.round((w*100+1e-9)*1e6)/1e6,score:n===children.length?r1(dl):null,range:[r1(dl),r1(dh)],answered:n,total:children.length,total_bank:all.length});
  }
  const gaps=[];
  for(const k of ['process','problem','process_owner'])if(!text(context[k]))gaps.push(k);
  const b=context.baseline;
  if(!obj(b)||!['metric','unit','period','source'].every(k=>text(b[k]))||typeof b.value!=='number'||!Number.isFinite(b.value)||b.value<0)gaps.push('baseline');
  for(const [k,allowed]of Object.entries({access_permission:['confirmed','denied','unknown'],impact:['low','medium','high','unknown'],human_review:['defined','missing','unknown'],fallback:['defined','missing','unknown']}))if(!allowed.includes(context[k]===undefined?'unknown':context[k]))throw new Error('Status konteks tidak sah');
  if(context.access_permission!=='confirmed')gaps.push('access_permission');
  if(!context.impact||context.impact==='unknown')gaps.push('impact');
  if(context.human_review!=='defined')gaps.push('human_review');
  if(context.fallback!=='defined')gaps.push('fallback');
  if(context.impact==='high'&&!expertOK(context))gaps.push('expert_review_required');
  const issues=[];
  for(const rule of bank.consistency_rules||[]){if(rule.mode!==mode)continue;
    const [a,b]=rule.questions.map(k=>norm[k]?.value);
    if(a!=null&&b!=null&&a<=rule.low_max&&b>=rule.high_min&&!reviewOK((p.consistency_resolutions||{})[rule.id]))issues.push({id:rule.id,questions:rule.questions,description:rule.description});
  }
  const declared=p.consistency_issues===undefined?[]:p.consistency_issues;if(!Array.isArray(declared))throw new Error('Issue harus list');
  for(const issue of declared){if(!obj(issue)||!text(issue.description))throw new Error('Deskripsi diperlukan');
    if(issue.status!=='resolved'||!reviewOK(issue.resolution))issues.push({id:issue.id||'reported_conflict',questions:[],description:issue.description});
  }
  const u=p.use_case||{},ug=useCaseGaps(u),blocked=Object.entries((bank.pilot_minimums||{})[mode]||{}).filter(([k,m])=>norm[k].value!==null&&norm[k].value<m).map(([k])=>k);
  const criticalControlWeak=weak.some(k=>['S1b','S7a','S7b','D1d','D2c','D7a','D7b','D7c','D7d'].includes(k));
  let route;
  if(context.access_permission==='denied')route='hentikan_akses_data';
  else if(obj(context.expert_review)&&context.expert_review.status==='rejected')route='tunda_dan_review_risiko';
  else if(issues.length)route='klarifikasi_bukti';
  else if((weak.length||blocked.length)&&(u.solution_type!=='process'||criticalControlWeak||!Array.isArray(u.remediates)||![...weak,...blocked].every(k=>u.remediates.includes(k))))route='perkuat_fondasi';
  else if(gaps.length||missing.length||unverified.length)route='discovery_dan_verifikasi';
  else if(['value_case','feasibility'].some(k=>obj(u[k])&&u[k].status==='not_viable'))route='tunda_atau_pilih_alternatif';
  else if(ug.length)route='pilih_dan_uji_kelayakan_solusi';
  else route={process:'rancang_pilot_fondasi',software:'rancang_pilot_non_ai',rule_automation:'rancang_pilot_non_ai',ai:'rancang_pilot_ai'}[u.solution_type];
  const score=missing.length?null:r1(low),band=score===null?null:score>=80?'Fondasi kuat untuk ditinjau':score>=60?'Fondasi berkembang':score>=40?'Fondasi perlu diperkuat':'Fondasi awal';
  const probes={process:'Satu proses apa yang ingin dibenahi lebih dulu?',problem:'Hambatan apa yang paling terasa pada proses itu?',process_owner:'Siapa yang bertanggung jawab atas proses ini?',baseline:'Apa ukuran kondisi saat ini yang bisa kita gunakan sebagai pembanding?',access_permission:'Siapa yang berwenang mengizinkan penggunaan data untuk tujuan ini?',impact:'Apa akibatnya bila solusi pada proses ini memberikan hasil yang salah?',human_review:'Siapa yang akan meninjau hasil sebelum dipakai?',fallback:'Bagaimana proses dilanjutkan jika alat mengalami gangguan?',expert_review_required:'Siapa penanggung jawab yang dapat meninjau risiko penggunaan ini?'};
  let next=[];
  if(!['hentikan_akses_data','tunda_dan_review_risiko'].includes(route)){
    if(issues.length)next=[{id:'clarify_conflict',question:issues[0].description,probe:'Untuk proses yang sedang kita bahas, keadaan sebenarnya bagaimana?'}];
    else {
      next=gaps.filter(k=>probes[k]).map(k=>({id:k,question:probes[k],probe:probes[k]}));
      next.push(...[...new Set([...unknown,...blocked,...weak,...unverified,...missing])].map(k=>{const q=qs.find(q=>q.id===k);return{id:k,question:q.question,probe:q.probe};}));
      if(!next.length&&ug.length){const uProbes={solution_type:'Alternatif perbaikan apa yang sudah dibandingkan untuk proses ini?',objective:'Hasil apa yang ingin dicapai dari percobaan ini?',selection_reason:'Apa alasan memilih opsi ini dibanding alternatifnya?',alternatives:'Alternatif perbaikan apa yang sudah dibandingkan?',diagnosis:'Apa bukti bahwa hambatan yang kita temukan merupakan penyebab utama masalah ini?',value_case:'Apa bukti manfaat yang cukup untuk melanjutkan percobaan ini?',feasibility:'Apa bukti bahwa opsi ini dapat dijalankan dengan sumber daya yang tersedia?',pilot_plan:'Siapa penanggung jawab percobaan yang akan dijalankan?'};const q=uProbes[ug[0]];next=[{id:'use_case',question:q,probe:q}];}
    }
  }
  return {version:'3.1',input_version:p.version,bank_revision:bank.bank_revision,mode,score,band,range:[r1(low),r1(high)],answer_coverage_percent:r1(known*100),verified_evidence_coverage_percent:r1(verified*100),dimensions,missing,critical_unknown:unknown,critical_weak:weak,critical_unverified:unverified,evidence_gaps:evidenceGaps,not_applicable:na,context_gaps:gaps,consistency_issues:issues,use_case_gaps:ug,pilot_blockers:blocked,next_questions:next.slice(0,3),route,deployment_approved:false};
}
root.OmniSenseConsulting={assess};if(typeof module!=='undefined')module.exports={assess};
})(typeof window!=='undefined'?window:globalThis);
