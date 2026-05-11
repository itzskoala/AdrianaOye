"""
Evaluator agent — checks whether Adriana's response actually answered the question.
Uses Gemini Flash Lite (fast + cheap). Returns (is_acceptable, feedback).

Designed to be balanced: catches genuinely bad responses (apologies, empty answers,
missed actions) without being so strict that every response triggers a retry.
Max 1 retry is enforced in adriana.py to cap token usage.
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)

_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
_MODEL  = "gemini-2.5-flash-lite"

_SYSTEM = """\
You are a quality evaluator for an AI social intelligence assistant called Adriana.
Given a user question and Adriana's response, decide if the response is acceptable.

A response is ACCEPTABLE if it:
- Contains actual data, facts, or findings (even if limited)
- Completed any requested action (e.g. sent an email, performed a search)
- Honestly explains when data is genuinely unavailable (e.g. no public data exists for that market)
- Partially answers with real information and explains what it couldn't find

A response NEEDS REVISION if it:
- Only apologizes or says it cannot help without trying
- Was asked to take an action (send email, search something) and clearly did not do it
- Returns completely empty or placeholder content with no real data
- Answers a completely different question than what was asked

Reply with ONLY one of these two formats:
ACCEPTABLE
REVISE: [one sentence explaining specifically what is missing or wrong]

Be lenient — if there is any real data or honest explanation, it is ACCEPTABLE.
"""


def evaluate(question: str, response: str) -> tuple[bool, str]:
    """
    Returns (True, "") if acceptable, or (False, feedback) if revision needed.
    On any API error, returns (True, "") to avoid blocking the user.
    """
    try:
        result = _client.models.generate_content(
            model=_MODEL,
            contents=f"User question: {question}\n\nAdriana's response:\n{response}",
            config=types.GenerateContentConfig(system_instruction=_SYSTEM),
        )
        verdict = (result.text or "").strip()
        if verdict.startswith("REVISE:"):
            feedback = verdict[len("REVISE:"):].strip()
            return False, feedback
        return True, ""
    except Exception:
        return True, ""
