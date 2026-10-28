'use strict';
let sectors=[],report,category='all';
const el=id=>document.getElementById(id);
const labels=()=>Object.fromEntries(sectors.map(s=>[s.id,s.label]));
const frequencyNames={monthly:'월간',annual:'연간',quarterly:'분기',snapshot:'확인 시점',decision:'정책 결정'};
function node(tag,text,cls){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;}
function safeURL(raw){try{const u=new URL(raw);return u.protocol==='https:'?u.href:null;}catch{return null;}}
function sourceLink(source,label){const a=node('a',label||source?.name||'원문 보기');const url=safeURL(source?.url);if(url){a.href=url;a.target='_blank';a.rel='noopener noreferrer';}return a;}
function number(value,digits){return value.toLocaleString('ko-KR',{minimumFractionDigits:digits??0,maximumFractionDigits:digits??0});}
function periodLabel(period){if(!period)return '기준 미확인';if(/^\d{4}$/.test(period))return period+'년';if(/^\d{4}-Q[1-4]$/.test(period))return `${period.slice(0,4)}년 ${period.at(-1)}분기`;return /^\d{4}-\d{2}$/.test(period)?`${period.slice(0,4)}년 ${Number(period.slice(5))}월`:period.replaceAll('-','.');}
function formatValue(m,value){if(value===null||value===undefined)return '연결 대기';let v=number(value,m.digits);if(m.unit==='%')return `${m.signed&&value>0?'+':''}${v}%`;if(m.unit==='USD/task')return `$${v}`;return v;}
function deltaInfo(m){
 if(m.current===null)return {text:'기준일과 원자료 연결 필요',direction:'neutral'};
 if(m.previous===null||m.previous===undefined||!m.comparable){
  if(typeof m.reportedChange==='number')return {text:`${m.reportedChange>0?'▲':m.reportedChange<0?'▼':'—'} ${m.reportedChangeLabel} ${number(Math.abs(m.reportedChange),1)}% · 기관 발표`,direction:m.reportedChange>0?'up':m.reportedChange<0?'down':'neutral'};
  return {text:m.frequency==='annual'?'연간 최신 발표값 · 전월 비교 제외':m.frequency==='quarterly'?'분기 최신 발표값 · 전월 비교 제외':m.id==='robo_return'?'최근 3개월 누적 · 전월 대비 수익률 아님':'비교 가능한 이전 원자료 없음',direction:'neutral'};
 }
 const diff=m.current-m.previous;
 if(m.deltaType==='pp')return {text:`${diff>0?'▲':diff<0?'▼':'—'} 변동률 ${number(Math.abs(diff),2)}%p ${diff>0?'확대':diff<0?'축소':'동일'}`,direction:diff>0?'up':diff<0?'down':'neutral'};
 if(m.previous===0)return {text:'이전값 0 · 증감률 산출 제외',direction:'neutral'};
 const d=diff/Math.abs(m.previous)*100;
 return {text:`${d>0?'▲':d<0?'▼':'—'} ${m.comparisonLabel||'전월 대비'} ${number(Math.abs(d),1)}%`,direction:d>0?'up':d<0?'down':'neutral'};
}
function metricCard(m){
 const card=node('article',undefined,'metric-card');const top=node('div',undefined,'card-top');
 const state=m.frequency==='annual'?'연간 최신값':m.frequency==='quarterly'?'분기 최신값':m.frequency==='snapshot'?'현재값 확인':m.fresh===false?'이전 발표 유지':'출처 확인';
 top.append(node('span',labels()[m.category],'category-label'),node('span','● '+state,'state'));
 card.append(top,node('h3',m.title),node('div',`${m.source.name} · ${periodLabel(m.period)}${m.scope?' · '+m.scope:''}`,'metric-meta'));
 const value=node('div',formatValue(m,m.current),'metric-value');if(m.unit!=='%')value.append(node('small',m.unit==='USD/task'?'/ 과제':m.unit));card.append(value);
 const delta=deltaInfo(m);card.append(node('div',delta.text,`delta ${delta.direction}`));
 if(m.previous!==null&&m.previous!==undefined&&m.comparable){
  const bars=node('div',undefined,'comparison');const max=Math.max(Math.abs(m.current),Math.abs(m.previous),.00001);
  for(const [label,val] of [[periodLabel(m.previousPeriod),m.previous],[periodLabel(m.period),m.current]]){const row=node('div',undefined,'bar-row');const track=node('div',undefined,'bar-track');const fill=node('div',undefined,'bar-fill');fill.style.width=`${Math.abs(val)/max*100}%`;track.append(fill);row.append(node('span',label),track,node('strong',formatValue(m,val)));bars.append(row);}card.append(bars);
  if(m.previousSource)card.append(sourceLink(m.previousSource,'이전 기간 원문 ↗'));
 }
 if(m.note)card.append(node('div',m.note,'no-comparison'));
 const meaning=node('p',undefined,'meaning');meaning.append(node('b','의미'),document.createTextNode(m.meaning));const impact=node('div',undefined,'impact');impact.append(node('b','파급'),document.createTextNode(m.impact));card.append(meaning,impact);const link=sourceLink(m.source,'원문 출처 ↗');link.className='metric-source';card.append(link);return card;
}
function newsSection(label,items,analysis=false){const box=node('div',undefined,`news-section${analysis?' news-analysis':''}`);box.append(node('strong',label));if(Array.isArray(items)){const list=node('ol');items.forEach(t=>list.append(node('li',t)));box.append(list);}else box.append(node('p',items));return box;}
function newsCard(n){const card=node('article',undefined,'news-card');const top=node('div',undefined,'card-top');top.append(node('span',n.tag,'news-tag'),node('span',n.published.replaceAll('-','.'),'news-date'),node('span',n.stage,'news-stage'));card.append(top,node('h3',n.headline),newsSection('사실',n.facts),newsSection('해석·시사점',n.analysis,true),newsSection('추적 포인트',n.track));const bottom=node('div',undefined,'news-bottom');bottom.append(sourceLink(n.source,'공식 발표 원문 ↗'),node('span',n.review==='auto'?'자동 작성 · 원문 대조 필요':'자료 검토 '+(n.reviewedAt||report.reviewedAt||report.cutoff).replaceAll('-','.')));card.append(bottom);return card;}
function render(){
 const allMetrics=report.metrics.filter(m=>category==='all'||m.category===category),metrics=allMetrics.filter(m=>m.current!==null),pending=allMetrics.filter(m=>m.current===null),news=report.news.filter(n=>category==='all'||n.category===category);
 el('metric-grid').replaceChildren(...metrics.map(metricCard));if(!metrics.length)el('metric-grid').append(node('p','이 분야의 수치 자료를 연결하고 있습니다. 아래 뉴스와 연결 현황을 확인하세요.','empty'));
 el('news-grid').replaceChildren(...news.map(newsCard));if(!news.length)el('news-grid').append(node('p','이 분야의 해당 월 검증 뉴스가 아직 없습니다.','empty'));
 el('metric-count').textContent=metrics.length;el('news-count').textContent=news.length;
 el('metric-notice').textContent='월간·분기·연간 자료를 구분합니다. 전월 대비와 전년 대비는 표시된 비교 기준을 확인하세요.';
 el('pending-list').replaceChildren();el('pending-panel').hidden=!pending.length;
 for(const m of pending){const row=node('div',undefined,'connection-row');row.append(node('strong',m.title),node('p',m.note||'원자료 연결 대기'),sourceLink(m.source,'공식 출처 ↗'));el('pending-list').append(row);}
 el('pending-count').textContent=pending.length;
 const header=node('div',undefined,'source-row header');['지표 / 출처','실적 기준','비교 기준','검증 상태'].forEach(t=>header.append(node('span',t)));el('source-table').replaceChildren(header);
 for(const m of allMetrics){const row=node('div',undefined,'source-row');const comparison=m.comparable?`${periodLabel(m.previousPeriod)} 대비`:m.reportedChangeLabel||'비교 제외';row.append(sourceLink(m.source,m.title),node('span',periodLabel(m.period)),node('span',comparison),node('span',m.current===null?'연결 대기':m.frequency==='annual'?'연간 최신값':m.frequency==='quarterly'?'분기 최신값':m.fresh===false?'이전 발표 유지':'출처 확인',m.current===null?'unknown':''));el('source-table').append(row);}
 el('data-notes').replaceChildren(...(report.dataNotes||[]).map(t=>node('li',t)));
}
async function loadReport(path){
 el('loading').hidden=false;el('error').hidden=true;
 try{const response=await fetch(path,{cache:'no-cache'});if(!response.ok)throw new Error(`HTTP ${response.status}`);report=await response.json();if(!Array.isArray(report.metrics)||!Array.isArray(report.news))throw new Error('보고서 형식 오류');
 const [y,m]=report.month.split('-');el('report-title').textContent=`${y}년 ${Number(m)}월 동향 브리핑`;el('edition').textContent=report.provisional?'잠정 보고서':'월간 보고서';el('cutoff').textContent=report.cutoff.replaceAll('-','.');el('updated-at').textContent=`${report.reviewedAt?'자료 검토 '+report.reviewedAt.replaceAll('-','.'):'자동 수집 자료'}${report.checkedAt?' · 자동 확인 '+report.checkedAt.slice(0,10).replaceAll('-','.') : ''}`;el('headline').textContent=report.headline;
 const available=new Set([...report.news,...report.metrics].map(x=>x.category));
 el('overview-counts').replaceChildren();for(const [label,val,unit] of [['수록 산업',available.size,'개'],['주요 뉴스',report.news.length,'건'],['확인된 수치',report.metrics.filter(x=>x.current!==null).length,'개'],['연결 대기',report.metrics.filter(x=>x.current===null).length,'개']]){const box=node('div',undefined,'overview-stat');const v=node('strong',String(val));v.append(node('small',unit));box.append(node('span',label),v);el('overview-counts').append(box);}
 el('filters').replaceChildren();for(const s of [{id:'all',label:'전체 보기'},...sectors]){const b=node('button',s.label);b.dataset.category=s.id;b.classList.toggle('selected',s.id===category);b.setAttribute('aria-pressed',String(s.id===category));el('filters').append(b);}render();el('report').hidden=false;
 }catch(e){el('report').hidden=true;el('error').hidden=false;el('error').textContent='보고서를 불러오지 못했습니다. 잠시 후 새로고침해 주세요.';console.error(e);}finally{el('loading').hidden=true;}
}
async function init(){try{const responses=await Promise.all([fetch('data/index.json',{cache:'no-cache'}),fetch('data/sectors.json',{cache:'no-cache'})]);if(responses.some(r=>!r.ok))throw new Error('목록 오류');const [index,config]=await Promise.all(responses.map(r=>r.json()));sectors=config;for(const entry of index.reports){const option=node('option',entry.label);option.value=entry.path;el('month-select').append(option);}el('month-select').value=index.reports[0].path;el('month-select').addEventListener('change',e=>loadReport(e.target.value));await loadReport(el('month-select').value);}catch(e){el('loading').hidden=true;el('error').hidden=false;el('error').textContent='보고서 목록을 불러올 수 없습니다.';console.error(e);}}
el('filters').addEventListener('click',e=>{const b=e.target.closest('button[data-category]');if(!b||!report)return;category=b.dataset.category;document.querySelectorAll('#filters button').forEach(x=>{const selected=x===b;x.classList.toggle('selected',selected);x.setAttribute('aria-pressed',String(selected));});render();});el('print-button').addEventListener('click',()=>window.print());init();
