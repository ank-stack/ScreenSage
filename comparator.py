import re
import json
from collections import Counter

def parse_answer(text):
    if not text:
        return None
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Find the LAST JSON object in text (reasoning may precede the final answer)
        for match in reversed(list(re.finditer(r'\{[^{}]+\}', text, re.DOTALL))):
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                continue
    return None

def sanitize_answer(text):
    if not text:
        return ""
    text = re.sub(r'^\s*answer\s*[:\-]\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\s*\(?[A-D]\)?[.)]\s*', '', text)
    return text.strip()[:90]

def compare(ans1, ans2):
    if ans1 and ans2:
        return ans1.get("option", "").strip().upper() == ans2.get("option", "").strip().upper()
    return False

def majority_vote(results):
    """
    results: dict of {model_name: parsed_answer or None}
    Returns (winning_option, winner_names, is_unanimous)
    """
    valid = {k: v for k, v in results.items() if v is not None}
    if not valid:
        return None, [], False

    option_counts = Counter(v.get('option', '').strip().upper() for v in valid.values())
    top_option, top_count = option_counts.most_common(1)[0]

    winners = [k for k, v in valid.items() if v.get('option', '').strip().upper() == top_option]
    return top_option, winners, top_count == len(valid)
