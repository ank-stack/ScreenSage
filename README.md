# 🧠 ScreenSage

ScreenSage is a simple AI automation tool that captures a screenshot, sends it to an AI vision model, and extracts a concise answer in structured format.

> ⚡ Current Stage: Screenshot → AI Response
> 🚧 Upcoming: WhatsApp API integration for automated messaging

---

## 🚀 Features

* 📸 Capture screen automatically
* 🔄 Convert image to Base64
* 🤖 Send image to AI (OpenAI Vision)
* 🧾 Get structured JSON response (one-word answer)
* ⚡ Lightweight automation pipeline

---

## 🧩 Project Workflow

```text
Screen Capture
   ↓
Convert to Base64
   ↓
Send to AI API
   ↓
Extract Answer (JSON)
   ↓
(Soon) Send to WhatsApp
```

---

## 📁 Project Structure

```
ScreenSage/
│── main.py            # Main automation script
│── screenshot.py      # Screenshot + Base64 utilities
│── ai_clients.py      # OpenAI API interaction
│── data/              # Stored screenshots
│── .env               # API keys
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/ank-stack/ScreenSage.git
cd ScreenSage
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Setup

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Usage

Run the main script:

```bash
python main.py
```

### What happens:

* Waits for a few seconds
* Takes a screenshot
* Converts it to Base64
* Sends it to AI
* Prints the response

---

## 🧠 Example Output

```json
{
  "answer": "B"
}
```

---

## ⚠️ Known Limitations

* ❌ Local image paths (`file://`) are not supported by OpenAI API
* ⚠️ Base64 images increase token usage significantly
* ⚠️ Full-screen screenshots may reduce accuracy
* ❌ No error handling for invalid AI responses (yet)

---

## 🔧 Improvements Planned

* 📱 WhatsApp API integration (send answers automatically)
* ✂️ Screenshot cropping (focus on question area)
* 📉 Reduce token usage (optimize image size)
* ✅ Strict JSON validation
* 🔁 Retry logic for failed responses
* ⚡ Switch from Base64 → file upload (better performance)

---

## 💡 Tech Stack

* Python
* OpenAI API (GPT-4o-mini Vision)
* PyAutoGUI
* Base64 Encoding

---

## 🧠 Learning Goals

This project focuses on:

* API integration
* AI automation pipelines
* Image processing basics
* Real-world AI engineering workflows

---

## ⚡ Future Vision

The goal is to evolve ScreenSage into a fully automated system:

```text
Screenshot → AI → Extract Answer → Send to WhatsApp → Real-time automation
```

---

## 📌 Notes

This is an **in-progress learning project**, not production-ready.
The focus is on understanding how AI APIs work in real workflows.

---

## 🤝 Contributing

Feel free to fork and experiment. Improvements and ideas are welcome.

---

## 📄 License

MIT License
