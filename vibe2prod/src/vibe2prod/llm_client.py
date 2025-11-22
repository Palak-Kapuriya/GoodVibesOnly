"""
llm_client.py

OpenAI-powered refactoring engine for vibe2prod.
Uses .env for API key loading.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file automatically
load_dotenv()


def get_client():
    """
    Returns an OpenAI client using OPENAI_API_KEY.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OPENAI_API_KEY. "
            "Add it to your .env file like: OPENAI_API_KEY=sk-xxxx"
        )
    return OpenAI(api_key=api_key)


# ------------------- PROMPT TEMPLATE ---------------------

REWRITE_PROMPT = """
You are an advanced senior-level Python refactoring engine.

Your task:
- Take the user's Python code.
- Improve structure, naming, clarity, and readability.
- Keep behavior EXACTLY the same.
- Break overly big functions into smaller helpers when logical.
- Add missing docstrings where appropriate.
- Remove unused imports, variables, dead branches.
- Replace magic numbers with descriptive named constants.
- Preserve functionality, but improve maintainability.
- Keep code Pythonic and production-ready.
- If you modify behavior, explain why in comments above the change.
- Avoid unnecessary abstractions or over-engineering.

Rewrite the FULL FILE into a clean, production-grade version.

User's code:
--------------------
{code}
--------------------

Return ONLY valid Python code with no commentary outside code.
"""


# ------------------- LLM CALL ----------------------------

def rewrite_code_with_llm(source_code: str) -> str:
    """
    Send vibe-coded source to OpenAI and return improved code.
    """
    client = get_client()
    prompt = REWRITE_PROMPT.format(code=source_code)

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a highly skilled Python engineer."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        # NEW SDK FORMAT — correct way to access content
        improved = response.choices[0].message.content
        return improved.strip()

    except Exception as e:
        # If anything goes wrong, return original code with error header
        return (
            f"# LLM ERROR: {e}\n"
            f"# Returning original source code.\n\n"
            f"{source_code}"
        )
