import urllib.request, json, re, os
base='https://api.github.com/repos/FAQGURU/FAQGURU/contents/topics/en'
files=json.load(urllib.request.urlopen(base,timeout=30))
allqs=[]
for f in files:
    name=f['name']
    if not name.endswith('.md'): continue
    raw=urllib.request.urlopen(f['download_url'],timeout=30).read().decode('utf-8')
    # parse headings ### question then answer until next ### or [[↑]
    # remove table of contents before first ###
    parts=re.split(r'\n(?=### )', raw)
    topic_name=name.replace('.md','').replace('-',' ').title()
    for part in parts:
        m=re.match(r'###\s*(.+?)\n(.*)', part, re.S)
        if not m: continue
        q=m.group(1).strip()
        ans=m.group(2).strip()
        # remove back-to-top and source sections
        ans=re.split(r'\[\[\u2191\]\s*Back to top\]', ans)[0].strip()
        ans=re.sub(r'######\s*Source.*','',ans,flags=re.S).strip()
        # clean markdown links? keep text
        if len(q)<5 or len(ans)<20: continue
        allqs.append((name,q,ans))
print('total parsed',len(allqs))
from collections import Counter
print(Counter(q[0] for q in allqs))