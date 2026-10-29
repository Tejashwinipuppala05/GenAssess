p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('logger = logging.getLogger("genassess.technical_mcq")\nlogger.setLevel(logging.INFO)',
            'logger = logging.getLogger("genassess.technical_mcq")\nlogger.setLevel(logging.INFO)\nif not logger.handlers:\n    _handler = logging.StreamHandler()\n    _handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))\n    logger.addHandler(_handler)')
open(p,'w').write(s)
print('done')