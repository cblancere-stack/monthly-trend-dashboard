'use strict';
let sectors=[],report,category='home';
const el=id=>document.getElementById(id);
const labels=()=>Object.fromEntries(sectors.map(s=>[s.id,s.label]));

async function fetchJSON(path){
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),15000);
 try{const response=await fetch(path,{cache:'no-store',signal:controller.signal});if(!response.ok)throw new Error(`HTTP ${response.status}`);return await response.json();}finally{clearTimeout(timer);}
}
function showLoadError(message){const box=el('error');box.hidden=false;box.replaceChildren(node('p',message));const link=node('a','최신 화면 다시 열기');const url=new URL(location.href);url.searchParams.set('v','20261028-r12');link.href=url.href;link.className='quiet-button';box.append(link);}

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
const overviewGroups=[{title:'경제·사회·규제·정치',categories:['macro']},{title:'부동산',categories:['realestate']},{title:'자동차·항공·우주·방산',categories:['mobility','defense']},{title:'AI·휴머노이드·로보틱스',categories:['ai','robotics']},{title:'2차전지·에너지·ESG',categories:['battery','energy']}];
function selectCategory(id){category=id;document.querySelectorAll('#filters button').forEach(b=>{b.classList.toggle('selected',b.dataset.category===id);b.setAttribute('aria-pressed',String(b.dataset.category===id));});render();el('filters').scrollIntoView({block:'start'});}
function renderSectorHome(){const provided=report.kind==='summary';const groups=provided?report.sectorSummaries:overviewGroups.map(g=>{const ms=report.metrics.filter(m=>g.categories.includes(m.category)&&m.current!==null);const news=report.news.filter(n=>g.categories.includes(n.category));return {...g,message:news[0]?.headline||'수록 자료와 공식 출처 확인',stats:ms.slice(0,6).map(m=>[`${m.title} · ${periodLabel(m.period)}`,formatValue(m,m.current)+(m.unit==='%'||m.unit==='USD/task'?'':' '+m.unit)]),issues:news.map(n=>n.headline),opportunity:ms[0]?.impact||'해당 월 공식 발표 확인',risk:'자료별 실적 기준월·범위·발표 단계가 다르므로 원문을 함께 확인하세요.'};});
 el('sector-home-grid').replaceChildren();for(const g of groups){const card=node('article',undefined,'sector-summary-card');if(g.categories.length>1)card.classList.add('wide-summary');const top=node('div',undefined,'summary-card-heading');top.append(node('h2',g.title),node('span','월간 요약','summary-origin'));card.append(top,node('p',g.message,'sector-takeaway'));const stats=node('div',undefined,'sector-summary-stats');for(const [label,value] of g.stats){const box=node('div');box.append(node('span',label),node('strong',value));stats.append(box);}card.append(stats,node('h3','이달의 핵심 이슈'));const list=node('ul');g.issues.forEach(t=>list.append(node('li',t)));card.append(list);for(const [label,text] of [['기회',g.opportunity],['리스크',g.risk]]){const p=node('p',undefined,'overview-implication');p.append(node('b',label),document.createTextNode(text));card.append(p);}
 const nav=node('div',undefined,'summary-detail-links');for(const cat of g.categories){const count=report.metrics.filter(m=>m.category===cat).length,newsCount=report.news.filter(n=>n.category===cat).length;const b=node('button',`${labels()[cat]} 항목별 요약 · 지표 ${count} / 현안 ${newsCount}`);b.addEventListener('click',()=>selectCategory(cat));nav.append(b);}card.append(nav);
 el('sector-home-grid').append(card);}
 el('sector-home-note').textContent=provided?'분야별 핵심 흐름과 주요 지표를 한눈에 확인하고, 각 분야에서 상세 요약을 살펴보세요.':'해당 월 공식자료 조사 결과의 요약입니다. 분야별 지표·뉴스와 출처를 확인하세요.';
}

function summaryMetric(m){const card=node('article',undefined,'metric-card');const top=node('div',undefined,'card-top');top.append(node('span',labels()[m.category],'category-label'),node('span',m.frequency?({monthly:'월간 지표',quarterly:'분기 지표',annual:'연간 지표',snapshot:'시점 지표',forecast:'전망'}[m.frequency]||'주요 지표'):'월간 지표','state'));card.append(top,node('h3',m.title),node('div',m.basis,'metric-meta'),node('div',m.valueText,'metric-value provided-value'));
 if(m.deltaText)card.append(node('div',m.deltaText,'provided-delta'));
 if(m.displayNote){const details=node('details',undefined,'metric-definition-note');details.append(node('summary','지표 산출 기준'),node('p',m.displayNote));card.append(details);}
 for(const [label,text] of [['의미',m.meaning],['파급',m.impact]])if(text){const block=node('p',undefined,'meaning');block.append(node('b',label),document.createTextNode(text));card.append(block);}
 if(m.source){const link=sourceLink(m.source,`${m.source.name} · 원문 ↗`);link.className='metric-source';card.append(link);}return card;}
function summaryNews(n,policy=false){const card=node('article',undefined,'news-card');const top=node('div',undefined,'card-top');top.append(node('span',policy?'정부정책':n.tag||labels()[n.category],'news-tag'),node('span',n.dateLabel||'정책 요약','news-date'),node('span',report.origin==='independent'?(n.stage||'월간 조사'):'월간 브리핑','news-stage'));card.append(top,node('h3',n.headline));
 if(policy)card.append(newsSection('내용',n.content),newsSection('해석',n.analysis,true));
 else card.append(newsSection('사실',n.facts),newsSection('해석·시사점',n.analysis,true),newsSection('추적 포인트',n.track));
 const bottom=node('div',undefined,'news-bottom');if(n.source)bottom.append(sourceLink(n.source,`${n.source.name} · 원문 ↗`));if(n.source){if((n.sources||[]).length>1){const details=node('details',undefined,'related-sources');details.append(node('summary',`관련 원문 ${n.sources.length-1}건`));for(const source of n.sources.slice(1)){const p=node('p');p.append(sourceLink(source,`${source.name} · ${source.title||'원문 보기'}`));details.append(p);}bottom.append(details);}card.append(bottom);}return card;}
function renderSummary(){const metrics=report.metrics.filter(m=>m.category===category),news=report.news.filter(n=>n.category===category),policies=report.policies.filter(n=>n.category===category),supplements=report.supplements.filter(s=>s.categories.includes(category));
 el('metric-grid').dataset.count=String(metrics.length);el('metric-grid').replaceChildren(...metrics.map(summaryMetric));el('news-grid').replaceChildren(...news.map(n=>summaryNews(n)));el('metric-count').textContent=metrics.length;el('news-count').textContent=news.length;
 el('metric-notice').textContent='지표별 수치와 비교 기준, 의미와 영향을 함께 확인하세요.';el('pending-panel').hidden=true;
 if(!metrics.length)el('metric-grid').append(node('p','이 분야의 별도 대표 지표는 이번 보고서에 없습니다.','empty'));
 if(!news.length)el('news-grid').append(node('p','이 분야의 해당 월 수록 이슈가 없습니다.','empty'));
 el('provided-extra').hidden=false;el('policy-count').textContent=policies.length;el('policy-grid').replaceChildren(...policies.map(n=>summaryNews(n,true)));el('provided-policy').hidden=!policies.length;
 el('supplement-section').hidden=!supplements.length;el('supplement-list').replaceChildren();for(const s of supplements){const card=node('article',undefined,'news-card');card.append(node('h3',s.title));const list=node('ul');for(const text of s.points)list.append(node('li',text));card.append(list);el('supplement-list').append(card);}
 el('calendar-table').replaceChildren();const table=node('table');const head=node('tr');['일자','분야','일정','관전 포인트'].forEach(t=>head.append(node('th',t)));const thead=node('thead');thead.append(head);table.append(thead);const tbody=node('tbody');const calendar=report.calendar.filter(item=>item.categories.includes(category));for(const item of calendar){const row=node('tr');[item.date,item.sector,item.event,item.watch].forEach(t=>row.append(node('td',t)));tbody.append(row);}table.append(tbody);el('calendar-section').hidden=!calendar.length;el('calendar-table').append(table);
 const sourcePanel=el('source-table');sourcePanel.replaceChildren();const references=(report.references||[]).filter(s=>s.categories.includes(category));
 if(references.length){const header=node('div',undefined,'source-row header');['자료 제목 / 원문','기관·매체','발표일','자료 유형'].forEach(t=>header.append(node('span',t)));sourcePanel.append(header);for(const source of references){const row=node('div',undefined,'source-row bibliography-row');row.append(sourceLink(source,source.title||source.name),node('span',source.name),node('span',source.published?source.published.replaceAll('-','.'):source.kind==='통계 시계열'?'시계열 자료':'원문 기준일 참조'),node('span',source.kind||'참고자료'));sourcePanel.append(row);}}
 else {for(const item of [...metrics,...news,...policies]){if(!item.source)continue;const row=node('div',undefined,'source-row');row.append(sourceLink(item.source,item.source.title||item.title||item.headline),node('span',item.source.name),node('span',item.source.published||item.published||''),node('span',item.source.kind||'발표자료'));sourcePanel.append(row);}if(!sourcePanel.childElementCount)sourcePanel.append(node('p','이 분야의 개별 원문 연결을 보완하고 있습니다.','source-empty'));}
 el('data-notes').replaceChildren(...(report.origin==='independent'?(report.dataNotes||['통계의 실적 기준월과 발표일을 구분합니다.']):['통계의 실적 기준월·발표일과 지표의 비교 범위를 구분합니다.','AI·로봇 지표의 상세 기준과 공식 출처는 각 카드에서 확인할 수 있습니다.']).map(t=>node('li',t)));
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
 const home=category==='home';el('sector-home').hidden=!home;
 for(const id of ['indicators','briefing','sources'])el(id).hidden=home;
 const [year,month]=report.month.split('-');el('report-title').textContent=`${year}년 ${Number(month)}월 ${home?'동향보고서 요약':labels()[category]||'동향 브리핑'}`;
 if(home){el('provided-extra').hidden=true;renderSectorHome();return;}
 if(report.kind==='summary'){renderSummary();return;}
 el('provided-extra').hidden=true;
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
 try{const priorKind=report?.kind;report=await fetchJSON(path);if(!Array.isArray(report.metrics)||!Array.isArray(report.news))throw new Error('보고서 형식 오류');
 const provided=report.kind==='summary';document.querySelector('.hero-description').textContent=provided?'모든 지표와 이슈를 항목별로 짧게 정리합니다.':'경제와 주요 산업의 변화, 수치와 공식 발표로 확인합니다.';if(priorKind!==report.kind||!report)category='home';
 const [y,m]=report.month.split('-');el('report-title').textContent=`${y}년 ${Number(m)}월 ${provided?'월간 요약보고서':'동향 브리핑'}`;el('edition').textContent=provided?(report.origin==='independent'?(report.publicationMode==='historical'?'월말 기준 보고서':report.phase==='enriched'?'보강판':'1차 보고서'):'월간 동향보고서'):report.provisional?'월간 요약 · 잠정':'월간 요약 · 자동 갱신';el('cutoff-label').textContent=provided&&report.origin!=='independent'?'작성 기준일':'작성 기준일';el('cutoff').textContent=report.cutoff.replaceAll('-','.');el('updated-at').textContent=provided?(report.origin==='independent'?(report.publicationMode==='historical'?'작성 '+report.updatedAt.replaceAll('-','.')+' · 월말 기준 재현':report.phase==='enriched'?'10일 보강판':'5일 1차 보고서'):report.revisedAt?'수정 '+report.revisedAt.replaceAll('-','.'):'기준월·발표일 구분'):`${report.reviewedAt?'자료 검토 '+report.reviewedAt.replaceAll('-','.'):'자동 수집 자료'}${report.checkedAt?' · 자동 확인 '+report.checkedAt.slice(0,10).replaceAll('-','.') : ''}`;el('headline').textContent=report.headline;
 const available=new Set([...report.news,...report.metrics].map(x=>x.category));
 const stats=provided?[['대표 지표',report.metrics.length,'개'],['뉴스·현안',report.news.length,'개'],['정부정책',report.policies.length,'개'],['수록 분야',available.size,'개']]:[['수록 산업',available.size,'개'],['주요 뉴스',report.news.length,'건'],['확인된 수치',report.metrics.filter(x=>x.current!==null).length,'개'],['연결 대기',report.metrics.filter(x=>x.current===null).length,'개']];
 el('overview-counts').replaceChildren();for(const [label,val,unit] of stats){const box=node('div',undefined,'overview-stat');const v=node('strong',String(val));v.append(node('small',unit));box.append(node('span',label),v);el('overview-counts').append(box);}
 el('filters').replaceChildren();for(const sector of [{id:'home',label:'동향보고서 요약'},...sectors]){const b=node('button',sector.label);b.dataset.category=sector.id;b.classList.toggle('selected',sector.id===category);b.setAttribute('aria-pressed',String(sector.id===category));el('filters').append(b);}render();el('report').hidden=false;
 }catch(e){el('report').hidden=true;showLoadError(e.name==='AbortError'?'자료 응답이 지연되고 있습니다. 최신 화면 다시 열기를 눌러 주세요.':'보고서를 불러오지 못했습니다. 최신 화면 다시 열기를 눌러 주세요.');console.error(e);}finally{el('loading').hidden=true;}
}
async function init(){try{const [index,config]=await Promise.all([fetchJSON('data/index.json'),fetchJSON('data/sectors.json')]);sectors=config;
 for(const [label,entries] of [['월간 동향보고서',index.summaryReports||[]]]){const group=node('optgroup');group.label=label;for(const entry of entries){const option=node('option',entry.label);option.value=entry.path;group.append(option);}el('month-select').append(group);}
 el('month-select').value=index.summaryReports?.[0]?.path;el('month-select').addEventListener('change',e=>loadReport(e.target.value));await loadReport(el('month-select').value);
 }catch(e){el('loading').hidden=true;showLoadError('보고서 목록을 불러올 수 없습니다. 최신 화면 다시 열기를 눌러 주세요.');console.error(e);}}
el('filters').addEventListener('click',e=>{const b=e.target.closest('button[data-category]');if(!b||!report)return;category=b.dataset.category;document.querySelectorAll('#filters button').forEach(x=>{const selected=x===b;x.classList.toggle('selected',selected);x.setAttribute('aria-pressed',String(selected));});render();});el('print-button').addEventListener('click',()=>window.print());init();

document.querySelectorAll('nav a').forEach(a=>a.addEventListener('click',()=>{if(a.hash==='#overview')selectCategory('home');else if(category==='home')selectCategory('macro');}));
