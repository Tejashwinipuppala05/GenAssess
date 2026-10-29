import urllib.request, json, http.cookiejar
cj = http.cookiejar.CookieJar()
o = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
h = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}
o.open(urllib.request.Request("http://127.0.0.1:8000/auth/login", data=json.dumps({"email":"testrounds@example.com","password":"correct horse battery staple"}).encode(), headers=h))
url = "http://127.0.0.1:8000/candidate/practice/rounds/technical/questions?limit=1&target_role=Software+Engineer"
req = urllib.request.Request(url, headers={"Origin":"http://localhost:3000"})
try:
    r = o.open(req)
    print(r.status, r.read().decode()[:300])
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())