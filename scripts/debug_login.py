import urllib.request, json, http.cookiejar
cj = http.cookiejar.CookieJar()
o = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
h = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}
req = urllib.request.Request(
    "http://127.0.0.1:8000/auth/login",
    data=json.dumps({"email": "testrounds@example.com", "password": "correct horse battery staple"}).encode(),
    headers=h,
)
try:
    res = o.open(req)
    print(res.status, res.read().decode()[:200])
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())