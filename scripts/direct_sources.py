"""Deterministic adapters for public official tables. No generated numbers."""
import copy
from datetime import date,datetime,timedelta
import io
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

SMP_URL='https://www.kpx.or.kr/smpMonthly.es?device=pc&mid=a10606080300'
ROBO_URL='https://index-docs.vettafi.com/Factsheets/ROBO%20Factsheet.pdf'
AA_URL='https://artificialanalysis.ai/leaderboards/models'
MODEL='GPT-6.1 Sol (max)'

def normalize(text):return re.sub(r'\s+',' ',text).strip()
def plain(raw):
 soup=BeautifulSoup(raw,'html.parser')
 for t in soup(['script','style','nav','header','footer','form']):t.decompose()
 return normalize(soup.get_text(' ',strip=True))
def numeric(text):return float(text.replace(',','').replace('$','').strip())
def parse_robo(text):
 match=re.search(r'as of\s+([A-Za-z]+ \d{1,2}, \d{4})',text,re.I)
 row=re.search(r'Price Return\s+(-?\d+(?:\.\d+)?)%\s+(-?\d+(?:\.\d+)?)%\s+(-?\d+(?:\.\d+)?)%',text)
 if not match or not row:raise ValueError('ROBO dated price-return table missing')
 day=datetime.strptime(match[1],'%B %d, %Y').date()
 return day,float(row[1]),float(row[3])
def parse_aa(raw):
 soup=BeautifulSoup(raw,'html.parser')
 for table in soup.find_all('table'):
  rows=table.find_all('tr')
  # Nested headers vary; resolve the exact column name rather than a position.
  for idx,header in enumerate(rows):
   columns=[normalize(c.get_text(' ',strip=True)) for c in header.find_all(['th','td'])]
   cost=next((i for i,c in enumerate(columns) if 'Cost per Task' in c),None)
   if cost is None:continue
   for row in rows[idx+1:]:
    cells=[normalize(c.get_text(' ',strip=True)) for c in row.find_all(['th','td'])]
    if len(cells)>cost and cells[0]==MODEL and re.fullmatch(r'\$[\d,]+(?:\.\d+)?',cells[cost]):return numeric(cells[cost])
 raise ValueError('Exact AA model/cost table unavailable')
def expand_table(table):
 grid=[];spans={}
 for row in table.find_all('tr'):
  values=[];col=0
  def carry():
   nonlocal col
   while col in spans:
    text,left=spans[col];values.append(text)
    if left<=1:del spans[col]
    else:spans[col]=(text,left-1)
    col+=1
  for cell in row.find_all(['th','td'],recursive=False):
   carry();text=normalize(cell.get_text(' ',strip=True));rs=int(cell.get('rowspan',1));cs=int(cell.get('colspan',1))
   for _ in range(cs):
    values.append(text)
    if rs>1:spans[col]=(text,rs-1)
    col+=1
  carry();grid.append(values)
 return grid

def parse_smp(raw,period):
 year,month=map(int,period.split('-'));soup=BeautifulSoup(raw,'html.parser')
 for table in soup.find_all('table'):
  grid=expand_table(table)
  for row in grid:
   if not row or '통합 SMP' not in row[0]:continue
   yi=next((i for i,c in enumerate(row) if c in (f'{str(year)[2:]}년',f'{year}년')),None)
   if yi is None or len(row)<=yi+month:continue
   val=row[yi+month]
   if re.fullmatch(r'\d+(?:\.\d+)?',val):return float(val)
 raise ValueError('Dated integrated SMP row missing')

def parse_motir(raw,kind):
 text=plain(raw)
 pub=re.search(r'등록일\s*(20\d{2}-\d{2}-\d{2})',text)
 title=re.search(r'(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(?:자동차산업|수출입)',text)
 if not pub or not title:raise ValueError('Official publication date/title missing')
 period=f'{title[1]}-{int(title[2]):02}'
 if kind=='auto':
  patterns={'auto_exports':r'수출.{0,90}?([\d,]+(?:\.\d+)?)\s*억\s*(?:달러|불)','auto_domestic':r'내수(?:\s*판매량)?(?:는|은)?[^\d]{0,15}([\d.]+)\s*만\s*대','auto_production':r'생산(?:량)?(?:는|은|이)?[^\d]{0,15}([\d.]+)\s*만\s*대'}
 else:patterns={'exports':r'수출은.{0,70}?([\d,]+(?:\.\d+)?)\s*억\s*달러','battery_exports':r'이차전지\s*수출\s*\(?([\d.]+)\s*억\s*달러'}
 values={}
 for key,pattern in patterns.items():
  match=re.search(pattern,text)
  if match:values[key]=numeric(match[1])
 if not values:raise ValueError('Official numeric statements missing')
 return date.fromisoformat(pub[1]),period,values

def update_metric(old,current,period,url,name,**fields):
 result=copy.deepcopy(old)
 result.update(current=current,period=period,source=dict(name=name,url=url),status='verified',validation='direct_official_adapter',fresh=True)
 # Preserve only identical observations' prior comparisons. Advance by exactly
 # one calendar month; rolling returns and snapshot costs never get MoM here.
 if old.get('period')==period and old.get('current')!=current:
  result.update(previous=None,previousPeriod=None,comparable=False)
 elif len(period)==7 and old.get('period')==(date.fromisoformat(period+'-01')-timedelta(days=1)).strftime('%Y-%m'):
  result.update(previous=old['current'],previousPeriod=old['period'],previousSource=old['source'],comparable=old.get('current') is not None)
 elif old.get('period')!=period:result.update(previous=None,previousPeriod=None,comparable=False)
 if old.get('period')!=period or old.get('current')!=current:
  # Old prose and YoY figures describe the previous observation.
  for key in ('reportedChange','reportedChangeLabel'):result.pop(key,None)
 result.update(fields);return result

def collect_direct(metrics,month,cutoff,today,read_url):
 old={m['id']:m for m in metrics};updates=[];issues=[]
 def attempt(label,fn):
  try:fn()
  except Exception as e:issues.append(label+': '+type(e).__name__)
 target=(date.fromisoformat(month+'-01')-timedelta(days=1)).strftime('%Y-%m')
 def smp():
  if 'smp' not in old:return
  raw,_=read_url(SMP_URL,['kpx.or.kr']);val=parse_smp(raw,target)
  current=update_metric(old['smp'],val,target,SMP_URL,'전력거래소',note='공식 월별 통합 SMP 표. 가중평균 SMP와 구분합니다.')
  prev=(date.fromisoformat(target+'-01')-timedelta(days=1)).strftime('%Y-%m')
  try:current.update(previous=parse_smp(raw,prev),previousPeriod=prev,comparable=True)
  except ValueError:pass
  updates.append(current)
 def robo():
  if 'robo_return' not in old:return
  raw,_=read_url(ROBO_URL,['index-docs.vettafi.com'])
  from pypdf import PdfReader
  text=normalize(' '.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages))
  day,val,ytd=parse_robo(text)
  if day>cutoff or day.isoformat()<old['robo_return']['period']:raise ValueError('Factsheet date outside range')
  updates.append(update_metric(old['robo_return'],val,day.isoformat(),ROBO_URL,'VettaFi · 공식 팩트시트',previous=None,previousPeriod=None,comparable=False,published=day.isoformat(),fresh=day.strftime('%Y-%m')==month,note=f'{day.isoformat()} 기준 최근 3개월 {val:+.1f}%, 연초 이후 {ytd:+.1f}%. 전월 대비 수익률이 아닙니다.'))
 def aa():
  if 'aa_cost_sol' not in old or month!=today.strftime('%Y-%m'):return
  raw,_=read_url(AA_URL,['artificialanalysis.ai']);val=parse_aa(raw)
  updates.append(update_metric(old['aa_cost_sol'],val,today.isoformat(),AA_URL,'Artificial Analysis',previous=None,previousPeriod=None,comparable=False,note='공개 표의 GPT-6.1 Sol (max) 과제당 비용. 평가 버전 미확인으로 과거값 증감 비교 제외.'))
 def motir():
  needed=set(old)&{'exports','battery_exports','auto_exports','auto_domestic','auto_production'}
  if not needed:return
  base='https://www.motir.go.kr';targets={}
  y,m=map(int,target.split('-'))
  for page in range(1,4):
   raw,_=read_url(base+f'/kor/article/ATCL3f49a5a8c?pageIndex={page}',['motir.go.kr'])
   soup=BeautifulSoup(raw,'html.parser')
   for a in soup.find_all('a',href=True):
    text=normalize(a.get_text(' ',strip=True))
    if not re.search(rf'{y}\s*년\s*{m}\s*월',text):continue
    kind='auto' if '자동차산업' in text else 'trade' if '수출입' in text else None
    if kind and kind not in targets and '/view' in a['href']:targets[kind]=urljoin(base,a['href'])
   if len(targets)==2:break
  for kind,url in targets.items():
   raw,_=read_url(url,['motir.go.kr']);pub,period,values=parse_motir(raw,kind)
   if pub.strftime('%Y-%m')!=month or pub>cutoff or period!=target:continue
   for id,val in values.items():
    if id not in old or period<old[id]['period']:continue
    updates.append(update_metric(old[id],val,period,url,'산업통상부',published=pub.isoformat(),note='공식 보도자료의 발표값. 전월 자료 정정 및 반올림 차이는 원문에서 확인하세요.'))
  if not targets:raise ValueError('Monthly release links not found in recent three pages')
 for label,fn in [('KPX SMP',smp),('ROBO factsheet',robo),('AA model cost',aa),('MOTIR monthly releases',motir)]:attempt(label,fn)
 return updates,issues
