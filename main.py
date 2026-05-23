import os
import keyboard
from concurrent.futures import ThreadPoolExecutor
from screenshot import capture_screen, image_to_base64
from ai_clients import openai_b64, anthropic_b64, gemini_b64, toggle_thinking
from comparator import parse_answer, majority_vote, sanitize_answer
from telegram import send_telegram

def get_data_num():
    data_list = [f for f in os.listdir("data") if f.startswith("screenshot_")]
    if data_list:
        nums = [int(f.split("_")[1].split(".")[0]) for f in data_list]
        return max(nums)
    return 0

MODEL_LABELS = {
    "openai":    "GPT-4o",
    "anthropic": "Claude Sonnet",
    "gemini":    "Gemini Flash",
}

def fmt_conf(val):
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.0%}"
    except (ValueError, TypeError):
        return str(val)

def build_message(answers, errors):
    results = {k: answers.get(k) for k in ("openai", "anthropic", "gemini")}
    active = {k: v for k, v in results.items() if v is not None and not errors.get(k)}

    if not active:
        lines = ["All 3 APIs failed!"]
        for k, e in errors.items():
            if e:
                lines.append(f"{MODEL_LABELS[k]}: {str(e)[:80]}")
        return "\n".join(lines)

    top_option, winners, unanimous = majority_vote(active)

    winning_answer = active[winners[0]] if winners else None
    answer_text = sanitize_answer(winning_answer.get("answer", "")) if winning_answer else ""

    if unanimous:
        header = f"👉 Option {top_option} — All agree"
    elif len(winners) >= 2:
        header = f"👉 Option {top_option} — Majority ({len(winners)}/3)"
    else:
        header = f"👉 Split — No majority"

    lines = [header]
    if answer_text:
        lines.append(f"✅ {answer_text}")
    lines.append("")

    for key, label in MODEL_LABELS.items():
        err = errors.get(key)
        ans = results.get(key)
        if err:
            lines.append(f"{label}: ERROR")
            continue
        if ans is None:
            lines.append(f"{label}: no response")
            continue
        opt = ans.get("option", "?").upper()
        conf = fmt_conf(ans.get("confidence"))
        marker = "✓" if opt == top_option else "✗"
        lines.append(f"{marker} {label}: {opt}  conf {conf}")

    return "\n".join(lines)

def process():
    data_num = get_data_num()
    img_path = capture_screen(data_num + 1)
    print(f"Screenshot saved: {img_path}")

    b64 = image_to_base64(img_path=img_path)
    print("Base64 encoded. Querying APIs...")

    with ThreadPoolExecutor(max_workers=3) as executor:
        f_openai    = executor.submit(openai_b64,    b64)
        f_anthropic = executor.submit(anthropic_b64, b64)
        f_gemini    = executor.submit(gemini_b64,    b64)

    raw = {}
    errors = {}
    for key, future in [("openai", f_openai), ("anthropic", f_anthropic), ("gemini", f_gemini)]:
        try:
            raw[key] = future.result()
            errors[key] = None
        except Exception as e:
            raw[key] = None
            errors[key] = e
            print(f"{MODEL_LABELS[key]} error: {e}")

    for key, label in MODEL_LABELS.items():
        print(f"{label}: {raw[key] or errors[key]}")

    answers = {k: parse_answer(raw[k]) for k in raw}

    message = build_message(answers, errors)
    print(f"\n--- Answer ---\n{message}\n---")
    try:
        msg_id = send_telegram(message)
        print(f"Telegram sent (msg_id: {msg_id})")
    except Exception as e:
        print(f"Telegram failed (answer shown above): {e}")

import ai_clients

def on_toggle_thinking():
    state = toggle_thinking()
    print(f"Thinking {'ON' if state else 'OFF'}")

keyboard.add_hotkey('f3', on_toggle_thinking)
print("ScreenSage ready — F2 to capture and analyze | F3 to toggle thinking | Ctrl+C to exit.\n")
try:
    while True:
        keyboard.wait('f2')
        thinking_str = " [thinking ON]" if ai_clients.THINKING_ENABLED else ""
        print(f"F2 pressed — capturing{thinking_str}...")
        process()
        print("Done. Press F2 for next question.\n")
except KeyboardInterrupt:
    print("\nExiting.")
