import os
import re
import json
import math
import base64
import time
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from google import genai as google_genai
from google.genai import types as genai_types

load_dotenv()

client_1 = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client_3 = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def _load_gemini_keys():
    keys = []
    i = 1
    while True:
        k = os.getenv(f'GEMINI_API_KEY_{i}')
        if k:
            keys.append(k)
            i += 1
        else:
            break
    if not keys:
        k = os.getenv('GEMINI_API_KEY')
        if k:
            keys.append(k)
    return keys

_gemini_keys = _load_gemini_keys()
_gemini_clients = [google_genai.Client(api_key=k) for k in _gemini_keys]
_gemini_index = 0
_gemini_cooldowns = {}  # key index -> unix timestamp when available again

PROMPT_LEAN = (
    "Look at this MCQ screenshot. Output ONLY this JSON, nothing else:\n"
    '{"answer": "<full option text>", "option": "A", "confidence": 0.95}\n'
    "Confidence is 0.0-1.0."
)

PROMPT_REASONING = (
    "Look at this MCQ screenshot. Briefly reason through the options, "
    "then end your response with this JSON on its own line:\n"
    '{"answer": "<full option text>", "option": "A", "confidence": 0.95}\n'
    "Confidence is 0.0-1.0 reflecting how certain you are."
)

THINKING_ENABLED = False

def toggle_thinking():
    global THINKING_ENABLED
    THINKING_ENABLED = not THINKING_ENABLED
    return THINKING_ENABLED

def openai_b64(img_b64):
    response = client_1.chat.completions.create(
        model="gpt-4o",
        max_tokens=150,
        logprobs=True,
        messages=[
            {
                "role": "system",
                "content": "You are a study assistant helping students review MCQ practice questions. Always identify the correct answer and return the requested JSON."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT_LEAN},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}", "detail": "low"}}
                ]
            }
        ]
    )

    text = response.choices[0].message.content

    # Use the LAST A/B/C/D token logprob — with reasoning, the final answer letter
    # appears at the end of the response inside the JSON, not in the reasoning text
    confidence = None
    if response.choices[0].logprobs and response.choices[0].logprobs.content:
        for tlp in response.choices[0].logprobs.content:
            if tlp.token.strip().strip('"') in ("A", "B", "C", "D"):
                confidence = round(math.exp(tlp.logprob), 4)

    # Extract JSON from response (reasoning may precede it)
    for match in reversed(list(re.finditer(r'\{[^{}]+\}', text, re.DOTALL))):
        try:
            data = json.loads(match.group())
            if confidence is not None:
                data["confidence"] = confidence
            return json.dumps(data)
        except (json.JSONDecodeError, ValueError):
            continue
    return text

def anthropic_b64(img_64):
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1500 if THINKING_ENABLED else 150,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": img_64,
                    },
                },
                {"type": "text", "text": PROMPT_LEAN},
            ],
        }]
    }
    if THINKING_ENABLED:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": 1024}

    message = client_3.messages.create(**kwargs)
    for block in message.content:
        if block.type == "text":
            return block.text
    return message.content[0].text

def _gemini_retry_delay(exc_str):
    m = re.search(r"'retryDelay':\s*'(\d+)s'", exc_str)
    return int(m.group(1)) + 5 if m else 60

def gemini_b64(img_b64):
    global _gemini_index
    if not _gemini_clients:
        return "Gemini: No API keys configured"

    image_part = genai_types.Part.from_bytes(
        data=base64.b64decode(img_b64),
        mime_type="image/png",
    )

    n = len(_gemini_clients)
    start = _gemini_index
    last_exc = None

    for attempt in range(n):
        idx = (start + attempt) % n
        cooldown_until = _gemini_cooldowns.get(idx, 0)
        if time.time() < cooldown_until:
            remaining = cooldown_until - time.time()
            print(f"Gemini key {idx + 1} in cooldown ({remaining:.0f}s remaining), trying next")
            continue

        try:
            response = _gemini_clients[idx].models.generate_content(
                model="gemini-2.5-flash",
                contents=[PROMPT_LEAN, image_part],
            )
            _gemini_index = (idx + 1) % n
            text = response.text
            for match in reversed(list(re.finditer(r'\{[^{}]+\}', text, re.DOTALL))):
                try:
                    data = json.loads(match.group())
                    return json.dumps(data)
                except (json.JSONDecodeError, ValueError):
                    continue
            return text
        except Exception as e:
            e_str = str(e)
            last_exc = e
            if "429" in e_str or "RESOURCE_EXHAUSTED" in e_str:
                delay = _gemini_retry_delay(e_str)
                _gemini_cooldowns[idx] = time.time() + delay
                print(f"Gemini key {idx + 1} hit 429, cooldown {delay}s")
                continue
            if "503" in e_str or "UNAVAILABLE" in e_str:
                time.sleep(2)
                _gemini_index = (idx + 1) % n
                continue
            _gemini_index = (idx + 1) % n
            raise

    _gemini_index = (start + 1) % n
    if last_exc:
        return f"429 RESOURCE_EXHAUSTED. {last_exc}"
    return "429 RESOURCE_EXHAUSTED. All Gemini keys in cooldown."