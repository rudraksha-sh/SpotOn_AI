import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from openai import AzureOpenAI
import traceback

# Load .env
load_dotenv()
AZURE_KEY = os.getenv("AZURE_API_KEY_1")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
API_VERSION = "2024-12-01-preview"

if not AZURE_KEY or not AZURE_ENDPOINT or not AZURE_DEPLOYMENT:
    raise ValueError("Please set AZURE_ENDPOINT, AZURE_DEPLOYMENT, and AZURE_API_KEY_1 in .env")

app = Flask(__name__, template_folder="templates", static_folder="static")

client = AzureOpenAI(
    api_version=API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_KEY
)

MAX_INPUT_LENGTH = 3000  # truncate very long articles
CHUNK_SIZE = 1500        # split large text into smaller parts
MAX_TOKENS = 1000        # max tokens for model response

def extract_text_from_url(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = soup.find_all("p")
        return " ".join([p.get_text() for p in paragraphs]).strip()
    except Exception as e:
        print("URL extraction error:", e)
        return None

def clean_text(text):
    if not text:
        return ""
    return re.sub(r"<.*?>", "", text).strip()

def call_azure_openai(prompt_messages, max_tokens=500):
    try:
        res = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=prompt_messages,
            max_completion_tokens=max_tokens
        )
        content = res.choices[0].message.content.strip()
        return content
    except Exception as e:
        print("Azure OpenAI Error:", e)
        traceback.print_exc()
        return None

def summarize_text(text, mode="neutral"):
    text = text[:MAX_INPUT_LENGTH]  # truncate if too long

    # Split text into chunks if necessary
    chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    summaries = []

    for chunk in chunks:
        mode_prompts = {
            "neutral": f"Summarize this news article in neutral 3-4 sentences:\n\n{chunk}",
            "facts": f"Summarize only the facts from this news article in 3-4 sentences:\n\n{chunk}",
            "eli10": f"Summarize this news article like explaining to a 10-year-old:\n\n{chunk}"
        }

        prompt = [
            {"role": "system", "content": "You are a helpful assistant that summarizes news."},
            {"role": "user", "content": mode_prompts.get(mode, mode_prompts["neutral"])}
        ]

        max_tokens = MAX_TOKENS if mode != "neutral" else 700
        summary = clean_text(call_azure_openai(prompt, max_tokens=max_tokens))

        # Fallback to neutral if mode-specific summary fails
        if not summary and mode != "neutral":
            fallback_prompt = [
                {"role": "system", "content": "You are a helpful assistant that summarizes news."},
                {"role": "user", "content": mode_prompts["neutral"]}
            ]
            summary = clean_text(call_azure_openai(fallback_prompt)) or ""

        if summary:
            summaries.append(summary)

    # Combine summaries from chunks
    final_summary = " ".join(summaries)
    return final_summary if final_summary else "Summary could not be generated."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    mode = data.get("mode", "neutral")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if text.startswith("http"):
        fetched = extract_text_from_url(text)
        if not fetched:
            return jsonify({"error": "Could not fetch article. Paste text instead."}), 400
        text = fetched

    summary = summarize_text(text, mode)
    return jsonify({"summary": summary})

@app.route("/bias", methods=["POST"])
def bias():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    if text.startswith("http"):
        fetched = extract_text_from_url(text)
        if not fetched:
            return jsonify({"error": "Could not fetch article. Paste text instead."}), 400
        text = fetched

    text = text[:MAX_INPUT_LENGTH]

    prompt = [
        {"role": "system", "content": "You are a helpful assistant that detects news bias."},
        {"role": "user", "content": f"Analyze the bias (left, right, neutral) of this news article and provide a short explanation:\n\n{text}"}
    ]

    bias_result = clean_text(call_azure_openai(prompt, max_tokens=500)) or "Bias analysis could not be generated."
    return jsonify({"bias": bias_result})

if __name__ == "__main__":
    app.run(debug=True)
