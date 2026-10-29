p='frontend/src/app/candidate/dashboard/page.tsx'
s=open(p).read()
s=s.replace('label: "Coming soon", current: false }','label: "Available now", current: false }')
open(p,'w').write(s)
print('done')