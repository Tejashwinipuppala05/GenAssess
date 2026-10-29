p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('logger = logging.getLogger("genassess.technical_mcq")',
            'logger = logging.getLogger("genassess.technical_mcq")\nlogger.setLevel(logging.INFO)')
open(p,'w').write(s)
print('done')