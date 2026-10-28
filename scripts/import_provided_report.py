"""Preserve the supplied deck's text and expose its full editorial coverage.

This imports supplied claims, not independently verified official statistics.
The raw slide paragraphs are retained alongside every navigable section.
"""
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,sys
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
CIRCLES='①②③④⑤⑥⑦⑧⑨⑩'
def paras(root):return [''.join(p.xpath('.//a:t/text()',namespaces=NS)).strip() for p in root.xpath('.//a:p',namespaces=NS) if ''.join(p.xpath('.//a:t/text()',namespaces=NS)).strip()]
def clean(t):return re.sub(r'\s+',' ',t).strip()
def circled_chunks(lines,policy=False,metric=False):
 starts=[i for i,t in enumerate(lines) if (re.match(r'^[①-⑩].*[｜|]\s*2026',t) if policy else bool(re.match(r'^[①-⑩]\s+\S',t)) if metric else t in CIRCLES)]
 return [lines[a:(starts[i+1] if i+1<len(starts) else len(lines))] for i,a in enumerate(starts)]
def base(id,page,category):return dict(id=id,sourceSlide=page,category=category,verification='provided_unverified')
def main(source):
 source=Path(source);slides=[];roots={}
 with ZipFile(source) as z:
  names=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+.xml',n)],key=lambda n:int(re.search(r'(\d+)\.xml',n)[1]))
  for n in names:
   page=int(re.search(r'(\d+)\.xml',n)[1]);root=etree.fromstring(z.read(n));roots[page]=root;p=paras(root)
   images=[]
   relpath=f'ppt/slides/_rels/slide{page}.xml.rels'
   targets={a.get('Id'):a.get('Target') for a in etree.fromstring(z.read(relpath)) if 'image' in a.get('Type','')}
   for rid in root.xpath('//a:blip/@r:embed',namespaces={**NS,'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}):
    name=Path(targets[rid]).name;dest=ROOT/'assets/provided-original'/name;dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(z.read('ppt/media/'+name));images.append(str(dest.relative_to(ROOT)))
   slides.append(dict(page=page,images=images,title=next((t for t in p if re.match(r'\d+-\d+\.|\d+\.',t)),p[1] if len(p)>1 else p[0]),paragraphs=p))
 bypage={s['page']:s['paragraphs'] for s in slides}
 report=dict(kind='provided',id='provided-2026-09-v5',month='2026-09',cutoff='2026-10-16',provisional=False,reviewedAt=None,sourceName=source.name,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),headline='제공하신 9월 보고서의 전체 지표·현안·정책·분석·일정을 보존합니다. 원본 수치와 공식 검증값은 구분합니다.',metrics=[],news=[],policies=[],supplements=[],calendar=[],slides=slides)
 def add_metric(page,cat,chunk,title=None,value=None):
  body=chunk[1:];meaning=next((clean(t[2:]) for t in body if t.startswith('의미')),'');impact=next((clean(t[2:]) for t in body if t.startswith('파급')),'')
  m=base(f'provided-m-{page}-{len(report["metrics"])+1}',page,cat)
  m['deltaText']=next((clean(t) for t in body if re.match(r'^(?:▲|▼|―|한은|[+-]\d)',t)), '')
  m.update(title=title or re.sub(r'^[①-⑩]\s*','',chunk[0]),valueText=value or (body[1] if len(body)>1 else body[0] if body else ''),meaning=meaning,impact=impact,originalLines=chunk)
  report['metrics'].append(m)
 for chunk in circled_chunks(bypage[4],metric=True):add_metric(4,'macro',chunk)
 # Page 5's headline values live in separate late text boxes in the source.
 chunks=circled_chunks([t for t in bypage[5] if not t.startswith('※')],metric=True)
 for chunk,value in zip(chunks,['0.27%','48,359 건','0.30%','28,080 호']):add_metric(5,'realestate',chunk,value=value)
 p=bypage[6];starts=[i for i,t in enumerate(p) if '비교:' in t]
 for idx,start in enumerate(starts):
  chunk=p[start:(starts[idx+1] if idx+1<len(starts) else len(p))]
  add_metric(6,'mobility' if idx<3 else 'defense',chunk,title=chunk[0].split('비교:')[0].strip(),value=chunk[1])
 for idx,chunk in enumerate(circled_chunks(bypage[7],metric=True)):add_metric(7,'robotics' if idx==0 else 'ai',chunk)
 p=bypage[8];titles=['탄산리튬 가격','양극재 수출액','이차전지 수출액','두바이유 가격','LNG 가격','계통한계가격','국내 배출권 가격','EU 배출권 가격','국내 RE100 기업 수']
 starts=[next(i for i,t in enumerate(p) if t.startswith(title)) for title in titles]
 for idx,start in enumerate(starts):
  chunk=p[start:(starts[idx+1] if idx+1<len(starts) else len(p))]
  add_metric(8,'battery' if idx<3 else 'energy',chunk,title=titles[idx],value=chunk[1])
 def add_news(page,cat,chunk,title=None,tag=None):
  bracket=[clean(t[1:-1]) for t in chunk if t.startswith('[') and t.endswith(']')]
  n=base(f'provided-n-{page}-{len(report["news"])+1}',page,cat)
  n.update(headline=title or (bracket[3] if len(bracket)>=4 else bracket[0] if bracket else chunk[0]),tag=tag or (bracket[0] if bracket else '제공보고서'),originalLines=chunk)
  report['news'].append(n)
 for page in range(11,20):
  for chunk in circled_chunks(bypage[page]):add_news(page,'macro',chunk)
 for page in (22,23):
  for chunk in circled_chunks(bypage[page]):add_news(page,'realestate',chunk)
 for page in (32,33,35,36):
  for chunk in circled_chunks(bypage[page]):add_news(page,'ai' if page<35 else 'robotics',chunk)
 for page in (39,40,41):
  for chunk in circled_chunks(bypage[page]):
   title=next((t.strip('[] ') for t in chunk if t.strip().startswith('[')),chunk[1])
   add_news(page,'battery' if page==39 else 'energy',chunk,title=title,tag='2차전지' if page==39 else '에너지' if page==40 else 'ESG')
 groups=[paras(sp) for sp in roots[26].xpath('/p:sld/p:cSld/p:spTree/p:grpSp',namespaces=NS) if len(paras(sp))>=4]
 for idx,chunk in enumerate(groups):add_news(26,'mobility' if idx<3 else 'defense',chunk,title=clean(chunk[-2]),tag='신기술 혁신')
 p=bypage[27];names=['중국 진영 63.1%','서구 레거시 위기','현대차그룹 글로벌 3위','국내 내수 둔화 24.1%'];starts=[p.index(t) for t in names]
 for idx,start in enumerate(starts):add_news(27,'mobility',p[start:(starts[idx+1] if idx+1<len(starts) else len(p))],title=names[idx],tag='자동차 시장')
 for page in (28,29):
  for sp in roots[page].xpath('/p:sld/p:cSld/p:spTree/p:grpSp',namespaces=NS):
   chunk=paras(sp)
   if len(chunk)>=3:add_news(page,'defense',chunk,title=clean(chunk[1] if page==28 and len(chunk)==3 else chunk[0]),tag='항공·우주 시장' if page==28 else '방위산업 시장')
 for page,cat in [(20,'macro'),(24,'realestate')]:
  for chunk in circled_chunks(bypage[page],policy=True):
   item=base(f'provided-p-{page}-{len(report["policies"])+1}',page,cat);item.update(headline=chunk[0],originalLines=chunk);report['policies'].append(item)
 for page in (10,26,27,28,29,30,34,37,42,43):
  cats=['macro'] if page==10 else ['mobility','defense'] if page in (26,27,28,29,30) else ['ai'] if page==34 else ['robotics'] if page==37 else ['battery','energy']
  report['supplements'].append(dict(id=f'provided-s-{page}',sourceSlide=page,categories=cats,title=next(s['title'] for s in slides if s['page']==page),paragraphs=bypage[page]))
 for page in (44,45):
  p=bypage[page];start=p.index('관전 포인트')+1;tail=p[start:];end=next((i for i,t in enumerate(tail) if t.startswith('출처:')),len(tail));cells=tail[:end]
  for i in range(0,len(cells)-3,4):report['calendar'].append(dict(sourceSlide=page,date=cells[i],sector=cells[i+1],event=cells[i+2],watch=cells[i+3],verification='provided_unverified'))
 report['sectorSummaries']=json.loads((ROOT/'data/provided-overview.json').read_text())
 for metric in report['metrics']:
  if metric['sourceSlide']==7:metric['reviewNote']='예시 수치가 남아 있을 가능성이 있습니다. 공식 원자료 대조 전 활용 보류. 원본 기재값을 보존한 것이며 검증값이 아닙니다.'
 report['coverage']=dict(slides=len(slides),metrics=len(report['metrics']),news=len(report['news']),policies=len(report['policies']),calendar=len(report['calendar']),macroMetrics=sum(m['category']=='macro' for m in report['metrics']),macroNews=sum(n['category']=='macro' for n in report['news']))
 (ROOT/'data/provided-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report['coverage'],ensure_ascii=False))
if __name__=='__main__':main(sys.argv[1])
