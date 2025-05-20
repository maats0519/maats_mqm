# module2_terminology_annotation.py

import os
import logging
import pandas as pd
from pathlib import Path

# === MODEL CONFIGURATION ===
MODEL = "claude"  # Options: "gpt", "gemini", "claude"
OUTPUT_DIR = Path("DE_EN")
LANG_PAIR = "de-en"
AFTER_DIR = "de_en"
INPUT_CSV = OUTPUT_DIR / MODEL / f"zero_shot_{AFTER_DIR}.csv"
OUTPUT_CSV = OUTPUT_DIR / MODEL / "terminology_annotations.csv"
SOURCE_LANGUAGE = "German"
TARGET_LANGUAGE = "English"
PROMPT_FILE = "./prompts/terminology.md"

# === API KEYS ===
OPENAI_API_KEY = "Your_OpenAI_Key"
CLAUDE_API_KEY = "Your_Claude_Key"
GEMINI_API_KEY = "Your_Gemini_Key"

# === Logging ===
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === Load API Clients ===
if MODEL == "gpt":
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
elif MODEL == "Gemini":
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    client = genai.GenerativeModel("models/gemini-2.0-flash")
elif MODEL == "claude":
    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
else:
    raise ValueError(f"Unsupported model: {MODEL}")

# === Load Prompt ===


def load_prompt(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Prompt file '{filepath}' not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# === Annotation Functions ===


def annotate_with_gpt(source_text, translated_text, prompt_guidelines):
    try:
        message = f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\nTranslation {TARGET_LANGUAGE}:\n{translated_text}\n\nPlease annotate any terminology errors according to the following guidelines:\n\n{prompt_guidelines}"
        messages = [{"role": "user", "content": message}]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT annotation failed: {e}")
        return None


def annotate_with_gemini(source_text, translated_text, prompt_guidelines):
    try:
        prompt = f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\nTranslation {TARGET_LANGUAGE}:\n{translated_text}\n\nPlease annotate any terminology errors according to the following guidelines:\n\n{prompt_guidelines}"
        response = client.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini annotation failed: {e}")
        return None


def annotate_with_claude(source_text, translated_text, prompt_guidelines):
    try:
        prompt = f"Source {SOURCE_LANGUAGE}:\n{source_text}\n\nTranslation {TARGET_LANGUAGE}:\n{translated_text}\n\nPlease annotate any terminology errors according to the following guidelines:\n\n{prompt_guidelines}"
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
            temperature=0.3
        )
        return response.content[0].text.strip()
    except Exception as e:
        logging.error(f"Claude annotation failed: {e}")
        return None

# === Annotation Dispatcher ===


def call_terminology_annotation(source_text, translated_text, prompt_guidelines):
    if MODEL == "gpt":
        return annotate_with_gpt(source_text, translated_text, prompt_guidelines)
    elif MODEL == "Gemini":
        return annotate_with_gemini(source_text, translated_text, prompt_guidelines)
    elif MODEL == "claude":
        return annotate_with_claude(source_text, translated_text, prompt_guidelines)
    else:
        raise ValueError("Invalid model type")

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
        annotation = call_terminology_annotation(original, translated, prompt)

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
