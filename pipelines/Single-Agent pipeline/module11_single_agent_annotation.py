# module11_single_agent_annotation.py

import os
import logging
import pandas as pd
from pathlib import Path

# === Configurations ===
MODEL_TYPE = "claude"  # Options: "gpt-4o", "claude", "Gemini"
OUTPUT_DIR = Path("DE_EN")         # ✅ Corrected
abbrve = "de_en"                   # ✅ Corrected
source_language = "German"       # ✅ Corrected
target_language = "English"        # ✅ Corrected
PROMPT_FILE = "./prompts/single_agent.md"

# Input & Output paths
INPUT_CSV = OUTPUT_DIR / MODEL_TYPE / f"zero_shot_{abbrve}.csv"
OUTPUT_CSV = OUTPUT_DIR / MODEL_TYPE / "single_agent_annotation.csv"
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = "Your_OpenAI_Key"
CLAUDE_API_KEY = "Your_Claude_Key"
GEMINI_API_KEY = "Your_Gemini_Key"

# Logging setup
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# === Load Clients ===
if MODEL_TYPE == "gpt-4o":
    import openai
    openai.api_key = OPENAI_API_KEY

elif MODEL_TYPE == "claude":
    import anthropic
    claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

elif MODEL_TYPE == "Gemini":
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

else:
    raise ValueError(f"Unsupported model type: {MODEL_TYPE}")


# === Load Prompt ===
def load_prompt(filepath):
    if not os.path.exists(filepath):
        logging.error(f"Prompt file '{filepath}' not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


# === Call Agent ===
def call_single_agent_annotation(source_text, trasnlation, prompt_template):
    try:
        message = (
            f"{prompt_template}\n\n"
            f"Source ({source_language}):\n{source_text}"
            f"Translated ({target_language}):\n{trasnlation}"
        )

        if MODEL_TYPE == "gpt-4o":
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": message}],
                temperature=0.3,
                max_tokens=5000
            )
            return response.choices[0].message.content.strip()

        elif MODEL_TYPE == "claude":
            response = claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": message}]
            )
            return response.content[0].text.strip()

        elif MODEL_TYPE == "Gemini":
            response = gemini_model.generate_content(message)
            return response.text.strip()

    except Exception as e:
        logging.error(f"Single agent annotation failed: {e}")
        return None


# === Main ===
def main():
    if not os.path.exists(INPUT_CSV):
        logging.error(f"Input file '{INPUT_CSV}' not found.")
        return

    df = pd.read_csv(INPUT_CSV)
    if "original" not in df.columns:
        logging.error("Expected column 'original' not found in the input CSV.")
        return

    prompt_template = load_prompt(PROMPT_FILE)
    if not prompt_template:
        return

    # === Resume Logic ===
    processed_indices = set()
    # if OUTPUT_CSV.exists():
    #     existing_df = pd.read_csv(OUTPUT_CSV)
    #     processed_indices = set(existing_df["index"])
    #     logging.info(f"Resuming from index {max(processed_indices, default=-1) + 1}...")

    results = []

    for _, row in df.iterrows():
        idx = row["index"]
        if idx in processed_indices:
            continue  # Skip already processed rows

        source = row["original"]
        zero_shot = row.get("zero_shot_translation", "")

        logging.info(f"Annotating segment {idx} with single-agent model...")
        annotation = call_single_agent_annotation(source, zero_shot, prompt_template)

        if annotation:
            results.append({
                "index": idx,
                "original": source,
                "zero_shot_translation": zero_shot,
                "annotation": annotation
            })
        else:
            logging.warning(f"Skipping segment {idx} due to failure.")

        # Save after each annotation
        if results:
            result_df = pd.DataFrame(results)
            if OUTPUT_CSV.exists():
                result_df.to_csv(OUTPUT_CSV, mode="a", index=False, header=False, encoding="utf-8")
            else:
                result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
            results.clear()  # Clear buffer after saving

    logging.info(f"All annotations completed. Results saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
