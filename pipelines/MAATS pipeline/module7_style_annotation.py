import os
import logging
import pandas as pd
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai
import anthropic
import time

# === Setup ===

client = OpenAI(api_key="Your_OpenAI_Key")
CLAUDE_API_KEY = "Your_Claude_Key"
GEMINI_API_KEY = "Your_Gemini_Key"

BASE_DIR = Path("DE_EN")
SOURCE_LANGUAGE = "German"
TARGET_LANGUAGE = "English"
MODEL = "claude"  # Options: "gpt-4o", "Gemini", "claude"
abbrev = "de_en"

INPUT_CSV = BASE_DIR / MODEL / f"zero_shot_{abbrev}.csv"
PROMPT_FILE = "./prompts/style.md"
OUTPUT_CSV = BASE_DIR / MODEL / "style_annotations.csv"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === Clients ===
genai.configure(api_key=GEMINI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# === Load Prompt File ===

def load_prompt(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Prompt file '{filepath}' not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# === Annotation Functions ===

def annotate_with_chatgpt(source_text, translated_text, guidelines):
    message = (
        f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\n"
        f"Translation {TARGET_LANGUAGE}:\n{translated_text}\n\n"
        f"Please annotate any **style** errors according to the following guidelines:\n\n{guidelines}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": message}],
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"gpt-4o annotation failed: {e}")
        return None


def annotate_with_gemini(source_text, translated_text, guidelines):
    try:
        prompt = (
            f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\n"
            f"Translation {TARGET_LANGUAGE}:\n{translated_text}\n\n"
            f"Please annotate any style errors according to the following guidelines:\n\n{guidelines}"
        )
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini annotation failed: {e}")
        return None


def annotate_with_claude(source_text, translated_text, guidelines, max_retries=5, retry_delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            prompt = (
                f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\n"
                f"Translation {TARGET_LANGUAGE}:\n{translated_text}\n\n"
                f"Please annotate any style errors according to the following guidelines:\n\n{guidelines}"
            )
            response = claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(retry_delay)

    logging.error("Claude annotation failed after maximum retries.")
    return None

# === Dispatcher ===

def call_locale_annotation(source_text, translated_text, prompt_guidelines, model):
    if model == "gpt-4o":
        return annotate_with_chatgpt(source_text, translated_text, prompt_guidelines)
    elif model == "Gemini":
        return annotate_with_gemini(source_text, translated_text, prompt_guidelines)
    elif model == "claude":
        return annotate_with_claude(source_text, translated_text, prompt_guidelines)
    else:
        logging.error(f"Unsupported model: {model}")
        return None

# === Main ===

def main():
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Input file '{INPUT_CSV}' not found.")
        return

    df = pd.read_csv(INPUT_CSV)
    prompt = load_prompt(PROMPT_FILE)
    if not prompt:
        return

    results = []

    for _, row in df.iterrows():
        idx = row["index"]
        original = row["original"]
        translated = row["zero_shot_translation"]

        logging.info(f"Annotating segment {idx} with model {MODEL}...")
        annotation = call_locale_annotation(original, translated, prompt, model=MODEL)

        if annotation:
            results.append({
                "index": idx,
                "original": original,
                "translated": translated,
                "locale_convention_annotation": annotation
            })
        else:
            logging.warning(f"Skipping segment {idx} due to annotation failure.")

    annotated_df = pd.DataFrame(results)
    annotated_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    logging.info(f"Saved locale convention annotations to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
