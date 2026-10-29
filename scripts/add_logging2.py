p='src/rounds/routes.py'
s=open(p).read()

# Add logging import
if 'import logging' not in s:
    s=s.replace('import os\nimport json','import os\nimport json\nimport logging',1)

# Add logger after router
if 'logger = logging.getLogger' not in s:
    s=s.replace(
        'router = APIRouter(prefix="/candidate/practice/rounds", tags=["candidate practice rounds"])',
        'router = APIRouter(prefix="/candidate/practice/rounds", tags=["candidate practice rounds"])\nlogger = logging.getLogger("genassess.technical_mcq")',
        1)

# Log when no API key
s=s.replace(
    '    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        return None',
    '    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        logger.info("LLM distractor generation skipped: OPENAI_API_KEY is not configured.")\n        return None',
    1)

# Log success
s=s.replace(
    '            validated = _validate_distractors(question, distractors)\n            if validated is not None:\n                return validated',
    '            validated = _validate_distractors(question, distractors)\n            if validated is not None:\n                logger.info("LLM distractor generation succeeded for %s.", question["id"])\n                return validated\n            logger.warning("LLM distractor validation failed for %s.", question["id"])',
    1)

open(p,'w').write(s)
print('done')