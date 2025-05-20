# module12_single_agent_improvement.py

import os
import json
import logging
import pandas as pd
from pathlib import Path
from openai import OpenAI
import google.generativeai as genai
import anthropic

# === Model Configuration ===
MODEL = "claude"  # Options: "gpt-4o", "Gemini", "claude"
SOURCE_LANG = "German"
TARGET_LANG = "English"
OUTPUT_DIR = Path("DE_EN")
INPUT_CSV = OUTPUT_DIR / MODEL /f"single_agent_annotation.csv"
OUTPUT_CSV = OUTPUT_DIR / MODEL / f"single_agent_improved_translation.csv"
PROMPT_FILE = "./prompts/translation_improvement.md"

OPENAI_API_KEY = "Your_OpenAI_Key"
CLAUDE_API_KEY = "Your_Claude_Key"
GEMINI_API_KEY = "Your_Gemini_Key"
# === API Setup ===
client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# === File Paths ===


# === Logging ===
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


# === Prompt Loader ===
def load_prompt(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Prompt file '{filepath}' not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# === Model-Specific Callers ===
def improve_with_gpt4o(source, translation, annotation, guidelines):
    try:
        full_message = (
            f"{guidelines}\n\n"
            f"Source ({SOURCE_LANG}):\n{source}\n\n"
            f"Initial Translation ({TARGET_LANG}):\n{translation}\n\n"
            f"Error Annotations:\n{annotation}\n\n"
            f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
            f"Your final answer should only include the improved Translation Sentence."
        )
        messages = [{"role": "user", "content": full_message}]
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=5000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT-4o failed: {e}")
        return None


def improve_with_gemini(source, translation, annotation, guidelines):
    try:
        full_prompt = (
            f"{guidelines}\n\n"
            f"Source ({SOURCE_LANG}):\n{source}\n\n"
            f"Initial Translation ({TARGET_LANG}):\n{translation}\n\n"
            f"Error Annotations:\n{annotation}\n\n"
            f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
            f"Your final answer should only include the improved Translation Sentence."
        )
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Gemini failed: {e}")
        return None


def improve_with_claude(source, translation, annotation, guidelines):
    try:
        full_prompt = (
            f"{guidelines}\n\n"
            f"Source ({SOURCE_LANG}):\n{source}\n\n"
            f"Initial Translation ({TARGET_LANG}):\n{translation}\n\n"
            f"Error Annotations:\n{annotation}\n\n"
            f"Using the above annotations, please provide an improved translation that corrects all identified errors.\n\n"
            f"Your final answer should only include the improved Translation Sentence."
        )
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.content[0].text.strip()
    except Exception as e:
        logging.error(f"Claude failed: {e}")
        return None


# === Dispatcher ===
def call_improvement_agent(source, translation, annotation, prompt, model):
    if model == "gpt-4o":
        return improve_with_gpt4o(source, translation, annotation, prompt)
    elif model == "Gemini":
        return improve_with_gemini(source, translation, annotation, prompt)
    elif model == "claude":
        return improve_with_claude(source, translation, annotation, prompt)
    else:
        logging.error(f"Unsupported model: {model}")
        return None


# === Main Script ===
def main():
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Missing input file: {INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV)
    required_cols = ["index", "original", "zero_shot_translation", "annotation"]
    if not all(col in df.columns for col in required_cols):
        logging.error(f"Input file must include columns: {required_cols}")
        return

    prompt = load_prompt(PROMPT_FILE)
    if not prompt:
        return

    # Resume mode
    if os.path.exists(OUTPUT_CSV):
        existing_df = pd.read_csv(OUTPUT_CSV)
        processed = set(existing_df["index"].tolist())
        results = existing_df.to_dict(orient="records")
        logging.info(f"Resuming from previous run. Found {len(processed)} completed segments.")
    else:
        processed = set()
        results = []

    for _, row in df.iterrows():
        idx = row["index"]
        if idx in processed:
            logging.info(f"Skipping already processed segment {idx}.")
            continue

        original = row["original"]
        translation = row["zero_shot_translation"]
        annotation = row["annotation"]

        logging.info(f"Improving segment {idx} using {MODEL}...")
        improved = call_improvement_agent(original, translation, annotation, prompt, MODEL)

        if improved:
            results.append({
                "index": idx,
                "original": original,
                "single_agent_translation": translation,
                "single_agent_improved_translation": improved
            })
            # Save after each successful result
            pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
        else:
            logging.warning(f"Skipping segment {idx} due to improvement failure.")

    logging.info(f"Finished. Total segments saved: {len(results)} to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
