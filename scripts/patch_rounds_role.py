p='src/rounds/routes.py'
s=open(p).read()
# update import for Query
s=s.replace('from fastapi import APIRouter, Depends, HTTPException, status','from fastapi import APIRouter, Depends, HTTPException, Query, status')
# update list_questions signature
old='''def list_questions(
    round_name: str,
    limit: int = 5,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))] = None,
) -> list[RoundQuestion]:'''
new='''def _role_tokens(target_role: str) -> set[str]:
    return {token.lower() for token in target_role.replace("/", " ").replace("-", " ").split()}


def _technical_relevant(question: dict[str, Any], target_role: str) -> bool:
    role = target_role.lower()
    category = question["category"].lower()
    topic = question["topic"].lower()
    if "data" in role or "analytics" in role:
        return category in {"sql", "dbms", "dsa", "software engineering", "cloud"} or any(
            keyword in topic for keyword in ("sql", "database", "data", "query", "table")
        )
    if "ai" in role or "machine learning" in role or "ml" in role:
        return category in {"dsa", "software engineering", "cloud", "python"} or any(
            keyword in topic for keyword in ("algorithm", "data", "python", "model")
        )
    # Default: software engineering roles.
    return True


def _coding_relevant(question: dict[str, Any], target_role: str) -> bool:
    role = target_role.lower()
    topic = question["topic"].lower()
    if "data" in role or "analytics" in role:
        return topic in {"lists", "mathematics", "algorithms"} or "list" in topic or "math" in topic
    if "ai" in role or "machine learning" in role or "ml" in role:
        return topic in {"algorithms", "mathematics", "lists"} or "algorithm" in topic
    return True


def list_questions(
    round_name: str,
    limit: int = 5,
    target_role: str = Query(default="Software Engineer", alias="targetRole"),
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))] = None,
) -> list[RoundQuestion]:'''
assert old in s
s=s.replace(old,new)
# update bank selection inside list_questions
old2='''    bank = _bank(round_name)
    rng = random.SystemRandom()
    chosen = rng.sample(bank, min(limit, len(bank)))'''
new2='''    bank = _bank(round_name)
    if round_name == "technical":
        filtered = [q for q in bank if _technical_relevant(q, target_role)]
    elif round_name == "coding":
        filtered = [q for q in bank if _coding_relevant(q, target_role)]
    else:
        filtered = bank
    if not filtered:
        filtered = bank
    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))'''
assert old2 in s
s=s.replace(old2,new2)
open(p,'w').write(s)
print('done')