import urllib.request, json, http.cookiejar
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
base = "http://127.0.0.1:8000"
headers = {"Origin": "http://localhost:3000", "Content-Type": "application/json"}
# register
try:
    req = urllib.request.Request(base + "/auth/register", data=json.dumps({"name":"Test","email":"testrounds@example.com","password":"correct horse battery staple"}).encode(), headers=headers)
    opener.open(req)
except Exception as e:
    print("register:", e)
# login
req = urllib.request.Request(base + "/auth/login", data=json.dumps({"email":"testrounds@example.com","password":"correct horse battery staple"}).encode(), headers=headers)
opener.open(req)
for round_name in ["technical", "coding", "behavioral"]:
    req = urllib.request.Request(base + f"/candidate/practice/rounds/{round_name}/questions?limit=2", headers={"Origin":"http://localhost:3000"})
    res = opener.open(req)
    data = json.loads(res.read())
    print(round_name, "questions:", len(data), data[0]["id"] if data else None)