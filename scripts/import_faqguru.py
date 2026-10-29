import urllib.request, json, re, os
from collections import Counter, defaultdict

base='https://api.github.com/repos/FAQGURU/FAQGURU/contents/topics/en'
files=json.load(urllib.request.urlopen(base,timeout=30))

category_map={
 'sql.md':'SQL',
 'java.md':'Java',
 'c.md':'C/C++',
 'data-structures.md':'DSA',
 'code-problems.md':'DSA',
 'design-patterns.md':'Software Engineering',
 'git.md':'Software Engineering',
 'agile.md':'Software Engineering',
 'mongodb.md':'DBMS',
 'graphql.md':'DBMS',
 'javascript.md':'JavaScript',
 'typeScript.md':'JavaScript',
 'nodejs.md':'JavaScript',
 'react.md':'Web Development',
 'redux.md':'Web Development',
 'angular.md':'Web Development',
 'angularjs.md':'Web Development',
 'vuejs.md':'Web Development',
 'html5.md':'Web Development',
 'css.md':'Web Development',
 'bootstrap.md':'Web Development',
 'sass.md':'Web Development',
 'webpack.md':'Web Development',
 'aws.md':'Cloud',
 'azure.md':'Cloud',
 'golang.md':'Go',
 'ruby.md':'Ruby',
 'ruby-on-rails.md':'Ruby',
 'net-framework.md':'.NET',
 'asp.net.md':'.NET',
 'asp.net-mvc.md':'.NET',
}

records=[]
counts=defaultdict(int)
for f in files:
    name=f['name']
    if not name.endswith('.md'): continue
    raw=urllib.request.urlopen(f['download_url'],timeout=30).read().decode('utf-8')
    parts=re.split(r'\n(?=### )', raw)
    cat=category_map.get(name, name.replace('.md','').title())
    for part in parts:
        m=re.match(r'###\s*(.+?)\n(.*)', part, re.S)
        if not m: continue
        q=m.group(1).strip()
        ans=m.group(2).strip()
        ans=re.split(r'\[\[\u2191\]\s*Back to top\]', ans)[0].strip()
        ans=re.sub(r'######\s*Source.*','',ans,flags=re.S).strip()
        if len(q)<5 or len(ans)<20: continue
        counts[name]+=1
        idx=counts[name]
        topic=name.replace('.md','').replace('-',' ').title()
        records.append({
            'id': f'faqguru-{name.replace(".md","")}-{idx:03d}',
            'round': 'technical',
            'question': q,
            'correct_answer': ans,
            'explanation': ans[:500],
            'category': cat,
            'topic': topic,
            'difficulty': 'Medium',
            'source': 'FAQGURU/FAQGURU (GitHub)',
            'license': 'MIT',
            'attribution': 'FAQGURU/FAQGURU, MIT license; imported and validated by GenAssess.',
            'tags': ['faqguru', topic.lower(), cat.lower().replace('/','-')],
        })

os.makedirs('data/question_banks',exist_ok=True)
json.dump(records, open('data/question_banks/faqguru_technical.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('imported',len(records))
print(Counter(r['category'] for r in records))