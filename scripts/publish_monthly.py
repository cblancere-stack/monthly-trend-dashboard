"""Expose only a completed, Gemini-assisted monthly run in the summary selector.

Old manually researched snapshots remain separate and are not re-exposed by this bridge.
"""
import calendar,json
from pathlib import Path

def register_summary(index,report,status):
 month=report['month']
 year,number=map(int,month.split('-'))
 final_day=f'{month}-{calendar.monthrange(year,number)[1]:02}'
 if report.get('cutoff')!=final_day or not status.get('geminiSucceeded') or not report.get('news'):
  return False
 # At least one fact must survive independent original-page checking this run.
 if not status.get('acceptedNewsUpdates') and not status.get('acceptedMetricUpdates'):
  return False
 entry={'id':'automatic-'+month,'month':month,'label':f'{year}년 {number}월 · 월간 요약','path':f'data/reports/{month}.json'}
 entries=[entry]+[e for e in index.get('summaryReports',[]) if e.get('month',e.get('id','')[8:15])!=month]
 index['summaryReports']=sorted(entries,key=lambda e:e.get('month',e.get('id','')[8:15]),reverse=True)
 return True
