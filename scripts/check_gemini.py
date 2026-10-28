"""Manual connection check. Never print API credentials or remote response bodies."""
import json,os,re,sys
from urllib.request import Request,urlopen
from urllib.error import HTTPError

def check():
 key=os.environ.get('GEMINI_API_KEY')
 if not key:
  print('GEMINI_API_KEY is missing. Add it under Settings > Secrets and variables > Actions.');return 1
 model=os.environ.get('GEMINI_MODEL') or 'gemini-flash-latest'
 if not re.fullmatch(r'[a-zA-Z0-9_.-]+',model):
  print('GEMINI_MODEL is invalid.');return 1
 payload={'contents':[{'parts':[{'text':'Reply with OK only.'}]}],'generationConfig':{'maxOutputTokens':64}}
 req=Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key},method='POST')
 try:
  with urlopen(req,timeout=45) as response:result=json.load(response)
  parts=result.get('candidates',[{}])[0].get('content',{}).get('parts',[])
  if not any(part.get('text') for part in parts):raise ValueError('No generated text')
 except HTTPError as error:
  print(f'Gemini connection failed (HTTP {error.code}). Check key, model access, quota and API billing.');return 1
 except Exception as error:
  print('Gemini connection failed: '+type(error).__name__);return 1
 print('Gemini API connection succeeded. Research with Google Search is checked separately in the monthly workflow.');return 0
if __name__=='__main__':sys.exit(check())
