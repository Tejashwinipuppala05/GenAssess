p='src/rounds/routes.py'
s=open(p).read()
s=s.replace(
'    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        logger.info("LLM distractor generation skipped: OPENAI_API_KEY is not configured.")\n        return None',
'    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        logger.info("LLM distractor generation skipped: OPENAI_API_KEY is not configured.")\n        return None\n    logger.info("LLM distractor generation using configured OpenAI-compatible endpoint with model %s.", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))')
open(p,'w').write(s)
print('done')