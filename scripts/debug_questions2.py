import urllib.request, json, http.cookiejar
cj = http.cookiejar.CookieJar()
o = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
h = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}
o.open(urllib.request.Request("http://127.0.0.1:8000/auth/login", data=json.dumps({"email":"testrounds@example.com","password":"correct horse battery staple"}).encode(), headers=h))
url = "http://127.0.0.1:8000/candidate/practice/rounds/technical/questions?limit=1&targetRole=Software+Engineer"
r = o.open(urllib.request.Request(url, headers={"Origin":"http://localhost:3000"}))
d = json.loads(r.read())
print("keys:", list(d[0].keys()))
print("has options:", d[0].get("options") is not None)