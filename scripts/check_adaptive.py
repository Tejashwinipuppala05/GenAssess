import urllib.request, json, http.cookiejar
cj = http.cookiejar.CookieJar()
o = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
h = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}
o.open(urllib.request.Request("http://127.0.0.1:8000/auth/login", data=json.dumps({"email":"testrounds@example.com","password":"correct horse battery staple"}).encode(), headers=h))
# start session
res = o.open(urllib.request.Request("http://127.0.0.1:8000/candidate/practice/technical/sessions", data=json.dumps({"targetRole":"Software Engineer","experienceLevel":"Fresher","topic":"General","totalQuestions":3}).encode(), headers=h))
session = json.loads(res.read())
print("First question difficulty:", session["question"]["difficulty"])
# submit a good answer (use ideal answer)
qid = session["question"]["id"]
ans = "This is a correct and detailed answer covering all concepts."
r = o.open(urllib.request.Request(f"http://127.0.0.1:8000/candidate/practice/technical/sessions/{session['id']}/answers/{qid}", data=json.dumps({"answer": ans}).encode(), headers=h))
ev = json.loads(r.read())
print("Score:", ev["score"], "Next difficulty:", ev["nextQuestion"]["difficulty"] if ev["nextQuestion"] else None)