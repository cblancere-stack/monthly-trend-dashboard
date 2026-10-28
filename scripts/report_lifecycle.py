"""Validate independently researched summaries; preserve other months on publication."""
import copy,json,re
from datetime import date,timedelta
from pathlib import Path
from urllib.parse import urlparse

def _source(item):
 source=item.get('source',{})
 u=urlparse(source.get('url',''))
 return bool(source.get('name') and u.scheme=='https' and u.hostname and not u.username and not u.password)

def _month_end_close(item,asof):
 """Only designated index closes may become available on the following KST day."""
 m=item.get('marketClose',{})
 series={
  'provided-m-7-25':('IAIQP','www.indxx.com'),
  'provided-m-7-24':('ROBO','www.vettafi.com'),
 }
 expected=series.get(item.get('id'))
 if not expected or m.get('cutoffPolicy')!='local_month_end_close':return False
 try:
  observed=date.fromisoformat(m['date']);published=date.fromisoformat(item['published'])
  last=(observed.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
  return (m.get('seriesCode')==expected[0] and urlparse(item.get('source',{}).get('url','')).hostname==expected[1]
   and m.get('currency')=='USD' and m.get('returnType')=='price'
   and observed.isoformat()==item.get('period') and observed<=asof and last==asof
   and 0<=(last-observed).days<=7 and published==observed+timedelta(days=1))
 except (KeyError,ValueError,TypeError):return False

def validate_summary(report,template):
 if report.get('kind')!='summary' or report.get('origin')!='independent':raise ValueError('Independent summary required')
 if not re.fullmatch(r'\d{4}-\d{2}',report.get('month','')):raise ValueError('Report month required')
 date.fromisoformat(report['month']+'-01')
 asof=date.fromisoformat(report['asOf'])
 if report['month']>asof.strftime('%Y-%m'):raise ValueError('Future report')
 if not report.get('headline'):raise ValueError('Headline required')
 covered=set()
 for m in report['metrics']:
  covered.add(m.get('replaces',m.get('id')))
  for key in ['id','category','title','valueText','basis','meaning','impact','deltaText','frequency']:
   if not m.get(key):raise ValueError('Empty metric field: '+key)
  if m.get('dataStatus') in ('not_released','unavailable'):
   if not m.get('missingReason') or not m.get('checkedSources'):raise ValueError('Unexplained missing value')
  elif not _source(m) or not m.get('period') or not m.get('published'):raise ValueError('Metric source and dates required')
  elif date.fromisoformat(m['published'])>asof and not _month_end_close(m,asof):raise ValueError('Metric source after cutoff')
 required={m['id'] for m in template['requiredMetricSlots']}
 if not required.issubset(covered):raise ValueError('Missing tracked indicator slots')
 cats={s['id'] for s in template['sectors']}
 if not cats.issubset(set(report.get('sectorCoverage',{}))):raise ValueError('All sectors require coverage notes')
 for key,fields in [('news',['headline','facts','analysis','track']),('policies',['headline','content','analysis'])]:
  for item in report[key]:
   if item.get('category') not in cats or not _source(item):raise ValueError('Invalid issue category or source')
   if not all(item.get(field) for field in fields):raise ValueError('Empty issue summary')
   published=date.fromisoformat(item['published'])
   if published>asof:raise ValueError('Source after report cutoff')
 for key in ['supplements','calendar','sectorSummaries']:
  if not isinstance(report.get(key),list):raise ValueError('Missing section: '+key)
 if len(report['sectorSummaries'])!=5:raise ValueError('Five overview groups required')
 if any(not _source(item) for item in report['calendar']):raise ValueError('Calendar source required')
 # Nested citations and event announcements must respect the same cutoff.
 def check_dates(value):
  if isinstance(value,dict):
   if value.get('published') and date.fromisoformat(value['published'])>asof and not _month_end_close(value,asof):raise ValueError('Nested source after report cutoff')
   for child in value.values():check_dates(child)
  elif isinstance(value,list):
   for child in value:check_dates(child)
 for section in ['metrics','news','policies','supplements','calendar','references']:check_dates(report.get(section,[]))
 return report

def save_summary(root,report,today=None,*,historical=False):
 root=Path(root);today=today or date.today()
 template=json.loads((root/'data/report-template.json').read_text())
 draft=copy.deepcopy(report)
 previous_month=(today.replace(day=1)-timedelta(days=1)).strftime('%Y-%m')
 if draft.get('month')!=previous_month and not historical:raise ValueError('Only previous month may be published')
 if historical and draft.get('month','')>=today.strftime('%Y-%m'):raise ValueError('Historical publication requires a past month')
 if date.fromisoformat(draft['asOf'])>today:raise ValueError('Report cutoff cannot be in the future')
 if historical and not draft.get('revisionNote'):raise ValueError('Historical publication reason required')
 validate_summary(draft,template)
 target=root/f"data/summaries/{draft['month']}.json"
 old=json.loads(target.read_text()) if target.exists() else None
 draft['phase']='initial' if historical else ('enriched' if today.day>=10 else 'initial')
 if historical:draft['publicationMode']='historical'
 draft['firstPublishedAt']=(old or {}).get('firstPublishedAt',today.isoformat())
 draft['updatedAt']=today.isoformat()
 draft['revisions']=(old or {}).get('revisions',[])+[{'date':today.isoformat(),'phase':draft['phase'],'note':draft.get('revisionNote','공식자료 반영')}]
 index_path=root/'data/index.json';index=json.loads(index_path.read_text())
 month=draft['month'];year,number=map(int,month.split('-'))
 edition='기준일 재현' if historical else ('보강판' if draft['phase']=='enriched' else '1차')
 entry={'id':'summary-'+month,'month':month,'label':f"{year}년 {number}월 · {edition}",'path':f'data/summaries/{month}.json'}
 def entry_month(e):
  if e.get('month'):return e['month']
  match=re.search(r'\d{4}-\d{2}',e.get('id',''))
  return match[0] if match else ''
 index['summaryReports']=sorted([entry]+[e for e in index.get('summaryReports',[]) if entry_month(e)!=month],key=entry_month,reverse=True)
 target.parent.mkdir(parents=True,exist_ok=True)
 for path,data in [(target,draft),(index_path,index)]:
  temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
 return target
