p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('        except Exception:\n            continue','        except Exception as exc:\n            logger.warning("LLM distractor generation error for %s: %s", question["id"], exc)\n            continue')
open(p,'w').write(s)
print('done')