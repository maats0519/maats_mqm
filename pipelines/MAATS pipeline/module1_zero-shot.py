import os
import logging
import pandas as pd
from datasets import load_dataset
from pathlib import Path

# === Configurations ===
MODEL_TYPE = "claude"  # Options: "gpt", "gemini", "claude"
OUTPUT_DIR = Path("DE_EN")
LANG_PAIR = "de-en"  # Language pair for translation
after_dir = "de_en"
OUTPUT_CSV = OUTPUT_DIR / MODEL_TYPE / f"zero_shot_{after_dir}.csv"
Source_Language = "German"
Target_Language = "English"
source_language_abbre = "de"
target_language_abbre = "en"

# === API KEYS (Insert Yours Here) ===
OPENAI_API_KEY = "Your_OpenAI_Key"
CLAUDE_API_KEY = "Your_Claude_Key"
GEMINI_API_KEY = "Your_Gemini_Key"

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === Load API Clients ===
if MODEL_TYPE == "gpt":
    from openai import OpenAI
    gpt_client = OpenAI(api_key=OPENAI_API_KEY)

elif MODEL_TYPE == "claude":
    import anthropic
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

elif MODEL_TYPE == "Gemini":
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

else:
    raise ValueError(f"Unsupported model type: {MODEL_TYPE}")

# === Translation Functions ===


def translate_with_gpt(source_text):
    try:
        messages = {
            "role": "user", "content": f"Translate from {Source_Language} to {Target_Language}:\n\n{source_text}, just provide the translation without any additional text."},
        response = gpt_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=5000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT translation failed: {e}")
        return None


def translate_with_claude(source_text):
    try:
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2500,
            temperature=0.3,
            messages=[{
                "role": "user",
                "content": f"Translate the following from {Source_Language} to {Target_Language}:\n\n{source_text}, just provide the translation without any additional text."
            }]
        )
        return response.content[0].text.strip()
    except Exception as e:
        logging.error(f"Claude translation failed: {e}")
        return None


def translate_with_gemini(source_text):
    try:
        prompt = f"Translate the following from {Source_Language} to {Target_Language}:\n\n{source_text}, just provide the translation without any additional text."
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini translation failed: {e}")
        return None

# === Unified Wrapper ===


def call_zero_shot_translation(source_text):
    if MODEL_TYPE == "gpt":
        return translate_with_gpt(source_text)
    elif MODEL_TYPE == "claude":
        return translate_with_claude(source_text)
    elif MODEL_TYPE == "Gemini":
        return translate_with_gemini(source_text)
    else:
        raise ValueError("Invalid model type")

# === Main Function ===


def main():
    try:
        logging.info("Loading dataset...")
        dataset = load_dataset("haoranxu/WMT23-Test", LANG_PAIR, split="test")
        subset = dataset.select(range(500))
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")
        return

    results = []

    for idx, sample in enumerate(subset):
        source_text = sample[LANG_PAIR][source_language_abbre]
        reference_text = sample[LANG_PAIR][target_language_abbre]
        logging.info(f"Translating segment {idx}...")

        translated_text = call_zero_shot_translation(source_text)
        if translated_text:
            results.append({
                "index": idx,
                "original": source_text,
                "zero_shot_translation": translated_text,
                "reference_translation": reference_text
            })
        else:
            logging.warning(
                f"Skipping segment {idx} due to translation error.")

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    logging.info(f"Saved {len(df)} translations to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
