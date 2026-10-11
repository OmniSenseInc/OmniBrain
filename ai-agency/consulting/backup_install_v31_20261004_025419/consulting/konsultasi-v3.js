(function(root){
'use strict';
function assess(p,bank){
  if(p.version!=='3.0') throw new Error('Versi harus 3.0');
  const mode=p.mode||'screening';
  if(!['screening','discovery'].includes(mode)) throw new Error('Mode tidak dikenal');
  const qs=bank[mode], answers=p.answers||{}, context=p.context||{};
  if(Object.keys(answers).some(k=>!qs.some(q=>q.id===k))) throw new Error('ID jawaban tidak dikenal');
  const sumW=bank.dimensions.reduce((s,d)=>s+d.weight,0);
  let low=0, high=0, known=0, verified=0;
  const missing=[], weak=[], unknown=[], unverified=[], dimensions=[];
  for(const d of bank.dimensions){
    const children=qs.filter(q=>q.dimension===d.id), w=d.weight/sumW;
    let dl=0,dh=0,n=0;
    for(const q of children){
      const a=answers[q.id]||{}, v=a.value==null?null:a.value, ev=a.evidence||'self_reported';
      if(!['self_reported','reviewed','observed'].includes(ev)) throw new Error('Status bukti tidak dikenal');
      if(v!==null&&(!Number.isInteger(v)||v<1||v>5)) throw new Error('Nilai harus 1-5 atau belum tahu');
      if(v!==null&&ev!=='self_reported'&&!(typeof a.source==='string'&&a.source.trim())) throw new Error('Rujukan bukti diperlukan');
      if(v===null){dl+=1;dh+=5;missing.push(q.id);if(q.critical)unknown.push(q.id);}
      else {dl+=v;dh+=v;n++;known+=w/children.length;if(ev!=='self_reported')verified+=w/children.length;
        if(q.critical&&v<3)weak.push(q.id);if(q.critical&&ev==='self_reported')unverified.push(q.id);}
    }
    dl=dl/children.length*20;dh=dh/children.length*20;low+=w*dl;high+=w*dh;
    dimensions.push({id:d.id,name:d.name,weight_percent:Math.round(w*1e8)/1e6,score:n===children.length?r1(dl):null,range:[r1(dl),r1(dh)],answered:n,total:children.length});
  }
  const gaps=[];
  for(const k of ['process','problem','process_owner'])if(typeof context[k]!=='string'||!context[k].trim())gaps.push(k);
  const b=context.baseline;
  if(!b||!['metric','unit','period','source'].every(k=>typeof b[k]==='string'&&b[k].trim())||typeof b.value!=='number'||!Number.isFinite(b.value)||b.value<0)gaps.push('baseline');
  for(const [key,allowed]of Object.entries({access_permission:['confirmed','denied','unknown'],impact:['low','medium','high','unknown'],human_review:['defined','missing','unknown'],fallback:['defined','missing','unknown']})){
    if(!allowed.includes(context[key]||'unknown'))throw new Error('Status konteks tidak dikenal');
  }
  if(context.access_permission!=='confirmed')gaps.push('access_permission');
  if(!context.impact||context.impact==='unknown')gaps.push('impact');
  if(context.human_review!=='defined')gaps.push('human_review');
  if(context.fallback!=='defined')gaps.push('fallback');
  if(context.impact==='high')gaps.push('expert_review_required');
  const route=context.access_permission==='denied'?'hentikan_akses_data':weak.length?'perkuat_fondasi':missing.length||unverified.length||gaps.length?'discovery_dan_verifikasi':'rancang_pilot_terbatas';
  const score=missing.length?null:r1(low);
  const band=score===null?null:score>=80?'Fondasi kuat untuk ditinjau':score>=60?'Fondasi berkembang':score>=40?'Fondasi perlu diperkuat':'Fondasi awal';
  return {version:'3.0',mode,score,band,range:[r1(low),r1(high)],answer_coverage_percent:r1(known*100),verified_evidence_coverage_percent:r1(verified*100),dimensions,missing,critical_unknown:unknown,critical_weak:weak,critical_unverified:unverified,context_gaps:gaps,route,deployment_approved:false};
}
function r1(n){return Math.round((n+1e-9)*10)/10;}
root.OmniSenseConsulting={assess};
if(typeof module!=='undefined')module.exports={assess};
})(typeof window!=='undefined'?window:globalThis);
