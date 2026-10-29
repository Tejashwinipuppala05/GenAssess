p='src/rounds/routes.py'
s=open(p).read()
# add logging import
s=s.replace('import os\nimport json','import os\nimport json\nimport logging')
# add logger after router definition
s=s.replace('router = APIRouter(prefix="/candidate/practice/rounds", tags=["candidate practice rounds"])',
            'router = APIRouter(prefix="/candidate/practice/rounds", tags=["candidate practice rounds"])\nlogger = logging.getLogger("genassess.technical_mcq")')
# log in _llm_distractors when no key
s=s.replace('    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        return None',
            '    api_key = os.getenv("OPENAI_API_KEY")\n    if not api_key:\n        logger.info("LLM distractor generation skipped: OPENAI_API_KEY is not configured.")\n        return None')
# log success/failure
s=s.replace('            validated = _validate_distractors(question, distractors)\n            if validated is not None:\n                return validated',
            '            validated = _validate_distractors(question, distractors)\n            if validated is not None:\n                logger.info("LLM distractor generation succeeded for %s.", question["id"])\n                return validated\n            logger.warning("LLM distractor validation failed for %s.", question["id"])')
# log exception
s=s.replace('        except Exception:\n            continue',
            '        except Exception as exc:\n            logger.warning("LLM distractor generation error for %s: %s", question["id"], exc)\n            continue')
# log fallback in list_questions
s=s.replace('''                distractors = _llm_distractors(question)
                if distractors is None:
                    # No valid options available without LLM; mark as descriptive.
                    question["_options"] = None
                    continue''',
'''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)''')
open(p,'w').write(s)
print('done')
PY