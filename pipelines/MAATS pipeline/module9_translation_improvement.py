# module9_translation_improvement.py

import os
import json
import logging
import pandas as pd
from openai import OpenAI
from pathlib import Path
import google.generativeai as genai
import anthropic
import time

# === Configuration ===
MODEL_TYPE = "claude"  # Options: "gpt-4o", "Gemini", "claude"
abbrve = "de_en"
source_language = "German"
target_language = "English"
BASE_DIR = Path("DE_EN")

INPUT_CSV = BASE_DIR / MODEL_TYPE / f"zero_shot_{abbrve}.csv"
PROMPT_FILE = Path("prompts") / "translation_improvement.md"
OUTPUT_CSV = BASE_DIR / MODEL_TYPE / "improved_translations.csv"

ANNOTATION_FILES = {
    "terminology": BASE_DIR / MODEL_TYPE / "terminology_annotations.csv",
    "accuracy": BASE_DIR / MODEL_TYPE / "accuracy_annotations.csv",
    "linguistic_conventions": BASE_DIR / MODEL_TYPE / "linguistic_convention_annotations.csv",
    "locale_conventions": BASE_DIR / MODEL_TYPE / "locale_convention_annotations.csv",
    "design_and_markup": BASE_DIR / MODEL_TYPE / "design_and_markup_annotations.csv",
    "style": BASE_DIR / MODEL_TYPE / "style_annotations.csv",
    "audience_appropriateness": BASE_DIR / MODEL_TYPE / "audience_appropriateness_annotations.csv"
}

# === Logging Setup ===
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === API Setup ===
client = OpenAI(api_key="Your_OpenAI_Key")  # Set this env var before running
genai.configure(api_key="Your_Gemini_Key")  # Set this env var before running
claude_client = anthropic.Anthropic(api_key="Your_Claude_Key")  # Set this env var before running


# === Load Prompt File ===
def load_prompt(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Prompt file '{filepath}' not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# === Improvement Functions by Model ===
def improve_with_gpt4o(source_text, translation, annotations_dict, prompt_guidelines):
    try:
        annotations_summary = json.dumps(annotations_dict, indent=2, ensure_ascii=False)
        full_message = (
            f"{prompt_guidelines}\n\n"
            f"Source ({source_language}):\n{source_text}\n\n"
            f"Initial Translation ({target_language}):\n{translation}\n\n"
            f"Error Annotations (from Agents 2–8):\n{annotations_summary}\n\n"
            f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
            f"Your final answer should only include the improved Translation Sentence."
        )
        messages = [{"role": "user", "content": full_message}]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT-4o improvement failed: {e}")
        return None


def improve_with_gemini(source_text, translation, annotations_dict, prompt_guidelines):
    try:
        annotations_summary = json.dumps(annotations_dict, indent=2, ensure_ascii=False)
        prompt = (
            f"{prompt_guidelines}\n\n"
            f"Source ({source_language}):\n{source_text}\n\n"
            f"Initial Translation ({target_language}):\n{translation}\n\n"
            f"Error Annotations (from Agents 2–8):\n{annotations_summary}\n\n"
            f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
            f"Your final answer should only include the improved Translation Sentence."
        )
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini improvement failed: {e}")
        return None


def improve_with_claude(source_text, translation, annotations_dict, prompt_guidelines,  max_retries=5, retry_delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            annotations_summary = json.dumps(annotations_dict, indent=2, ensure_ascii=False)
            prompt = (
                f"{prompt_guidelines}\n\n"
                f"Source ({source_language}):\n{source_text}\n\n"
                f"Initial Translation ({target_language}):\n{translation}\n\n"
                f"Error Annotations (from Agents 2–8):\n{annotations_summary}\n\n"
                f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
                f"Your final answer should only include the improved Translation Sentence."
            )
            response = claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4096,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logging.error(f"Claude improvement failed: {e}")
            attempt += 1
            time.sleep(retry_delay)
    logging.error("Claude annotation failed after maximum retries.")
    return None


# === Dispatcher ===
def call_improvement_agent(source_text, translation, annotations_dict, prompt_guidelines, model="gpt-4o"):
    if model == "gpt-4o":
        return improve_with_gpt4o(source_text, translation, annotations_dict, prompt_guidelines)
    elif model == "Gemini":
        return improve_with_gemini(source_text, translation, annotations_dict, prompt_guidelines)
    elif model == "claude":
        return improve_with_claude(source_text, translation, annotations_dict, prompt_guidelines)
    else:
        logging.error(f"Unsupported model: {model}")
        return None


# === Main Script ===
def main():
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Missing input file: {INPUT_CSV}")
        return
    base_df = pd.read_csv(INPUT_CSV)

    # Load prompt
    prompt = load_prompt(PROMPT_FILE)
    if not prompt:
        return

    # Load previous results if exist
    if os.path.exists(OUTPUT_CSV):
        existing_df = pd.read_csv(OUTPUT_CSV)
        processed_indexes = set(existing_df["index"].tolist())
        results = existing_df.to_dict(orient="records")
        logging.info(f"Resuming from previous run. Found {len(processed_indexes)} already processed segments.")
    else:
        processed_indexes = set()
        results = []

    # Load all annotation files
    annotations = {}
    for key, path in ANNOTATION_FILES.items():
        if not os.path.exists(path):
            logging.warning(f"Missing annotation file: {path}")
            continue
        annotations[key] = pd.read_csv(path).set_index("index")

    for _, row in base_df.iterrows():
        idx = row["index"]
        if idx in processed_indexes:
            logging.info(f"Skipping already processed segment {idx}.")
            continue

        original = row["original"]
        zero_shot = row["zero_shot_translation"]

        # Gather all annotation errors for this index
        error_annotations = {}
        for key, df in annotations.items():
            if idx in df.index:
                annotation_column = df.columns[-1]
                error_annotations[key] = df.at[idx, annotation_column]
            else:
                error_annotations[key] = "No annotation available."

        logging.info(f"Improving segment {idx} using {MODEL_TYPE}...")
        improved = call_improvement_agent(original, zero_shot, error_annotations, prompt, model=MODEL_TYPE)

        if improved:
            results.append({
                "index": idx,
                "original": original,
                "zero_shot_translation": zero_shot,
                "improved_translation": improved
            })
            # Save progress after each successful annotation
            pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        else:
            logging.warning(f"Skipped segment {idx} due to improvement failure.")

    logging.info(f"Finished. Total saved: {len(results)} segments to {OUTPUT_CSV}")
    

if __name__ == "__main__":
    main()
