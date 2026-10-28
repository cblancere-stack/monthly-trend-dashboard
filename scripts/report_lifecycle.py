"""Validate independently researched summaries; preserve other months on publication."""
import copy,json,re
from datetime import date,timedelta
from pathlib import Path
from urllib.parse import urlparse

def _source(item):
 source=item.get('source',{})
 u=urlparse(source.get('url',''))
 return bool(source.get('name') and u.scheme=='https' and u.hostname and not u.username and not u.password)

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
  elif date.fromisoformat(m['published'])>asof:raise ValueError('Metric source after cutoff')
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
 return report

def save_summary(root,report,today=None):
 root=Path(root);today=today or date.today()
 template=json.loads((root/'data/report-template.json').read_text())
 draft=copy.deepcopy(report)
 previous_month=(today.replace(day=1)-timedelta(days=1)).strftime('%Y-%m')
 if draft.get('month')!=previous_month:raise ValueError('Only previous month may be published')
 validate_summary(draft,template)
 target=root/f"data/summaries/{draft['month']}.json"
 old=json.loads(target.read_text()) if target.exists() else None
 draft['phase']='enriched' if today.day>=10 else 'initial'
 draft['firstPublishedAt']=(old or {}).get('firstPublishedAt',today.isoformat())
 draft['updatedAt']=today.isoformat()
 draft['revisions']=(old or {}).get('revisions',[])+[{'date':today.isoformat(),'phase':draft['phase'],'note':draft.get('revisionNote','공식자료 반영')}]
 index_path=root/'data/index.json';index=json.loads(index_path.read_text())
 month=draft['month'];year,number=map(int,month.split('-'))
 entry={'id':'summary-'+month,'month':month,'label':f"{year}년 {number}월 · {'보강판' if draft['phase']=='enriched' else '1차'}",'path':f'data/summaries/{month}.json'}
 def entry_month(e):
  if e.get('month'):return e['month']
  match=re.search(r'\d{4}-\d{2}',e.get('id',''))
  return match[0] if match else ''
 index['summaryReports']=sorted([entry]+[e for e in index.get('summaryReports',[]) if entry_month(e)!=month],key=entry_month,reverse=True)
 target.parent.mkdir(parents=True,exist_ok=True)
 for path,data in [(target,draft),(index_path,index)]:
  temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
 return target
