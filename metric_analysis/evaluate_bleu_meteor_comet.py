import os
import logging
import pandas as pd
import nltk
import matplotlib.pyplot as plt
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from pathlib import Path
from comet import download_model, load_from_checkpoint
from bleurt import score as bleurt_score
# === Setup ===
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")

# Change here
BASE_DIR = Path("DE_EN")
MODEL = Path("claude")
abbrve = "de_en"
ANALYSIS = Path("analysis")
# === Input/Output Paths ===
INPUT_ZERO = BASE_DIR / MODEL / f"zero_shot_{abbrve}.csv"
INPUT_IMPROVED = BASE_DIR / MODEL / "improved_translations.csv"
INPUT_SINGLE_AGENT = BASE_DIR / MODEL / "single_agent_improved_translation.csv"
OUTPUT_CSV = ANALYSIS / BASE_DIR / MODEL / "translation_evaluation_scores.csv"


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

smoother = SmoothingFunction().method1


def main():

    if not all(os.path.exists(p) for p in [INPUT_ZERO, INPUT_IMPROVED, INPUT_SINGLE_AGENT]):
        logging.error("Missing one or more required input files.")
        return
    logging.info("Downloading and loading COMET model...")
    model_path = download_model("Unbabel/wmt22-comet-da")
    comet_model = load_from_checkpoint(model_path)
    logging.info("COMET model loaded.")


    bleurt_checkpoint = "BLEURT-20"
    bleurt_scorer = bleurt_score.BleurtScorer(bleurt_checkpoint)

    df_zero = pd.read_csv(INPUT_ZERO).set_index("index")
    df_improved = pd.read_csv(INPUT_IMPROVED).set_index("index")
    df_single = pd.read_csv(INPUT_SINGLE_AGENT).set_index("index")

    results = []

    for idx in df_zero.index:
        try:
            # === Read translations as strings ===
            ref = str(df_zero.at[idx, "reference_translation"])
            zero_shot = str(df_zero.at[idx, "zero_shot_translation"])
            source = str(df_zero.at[idx, "original"])
            improved = str(df_improved.at[idx, "improved_translation"])
            single_agent = str(
                df_single.at[idx, "single_agent_improved_translation"])

            # === BLEU ===
            ref_tokens = nltk.word_tokenize(ref)
            zero_tokens = nltk.word_tokenize(zero_shot)
            improved_tokens = nltk.word_tokenize(improved)
            single_tokens = nltk.word_tokenize(single_agent)

            bleu_zero = sentence_bleu(
                [ref_tokens], zero_tokens, smoothing_function=smoother)
            bleu_improved = sentence_bleu(
                [ref_tokens], improved_tokens, smoothing_function=smoother)
            bleu_single = sentence_bleu(
                [ref_tokens], single_tokens, smoothing_function=smoother)

            # === METEOR ===
            reference = [ref.split()]
            machine_translation = zero_shot.split()
            refined_translation = improved.split()
            single_agent_translation = single_agent.split()

            meteor_zero = meteor_score(reference, machine_translation)
            meteor_improved = meteor_score(reference, refined_translation)
            meteor_single = meteor_score(reference, single_agent_translation)
            # === COMET ===
            comet_data = [
                {"src": source, "mt": zero_shot, "ref": ref},
                {"src": source, "mt": improved, "ref": ref},
                {"src": source, "mt": single_agent, "ref": ref},
            ]
            comet_scores = comet_model.predict(comet_data, batch_size=1).scores
            comet_zero, comet_improved, comet_single = comet_scores

             # BLEURT
            # bleurt_zero = bleurt_scorer.score([ref], [zero_shot])[0]
            bleurt_zero = bleurt_scorer.score(references=[ref], candidates=[zero_shot])[0]
            bleurt_improved = bleurt_scorer.score(references = [ref], candidates = [improved])[0]
            bleurt_single = bleurt_scorer.score(references = [ref], candidates = [single_agent])[0]
            logging.info(f"index: {idx}, BLEURT scores: {bleurt_zero}, {bleurt_improved}, {bleurt_single}")

            results.append({
                "index": idx,
                "reference": ref,
                "zero_shot_translation": zero_shot,
                "improved_translation": improved,
                "single_agent_translation": single_agent,
                "bleu_zero_shot": round(bleu_zero, 4),
                "bleu_improved": round(bleu_improved, 4),
                "bleu_single_agent": round(bleu_single, 4),
                "meteor_zero_shot": round(meteor_zero, 4),
                "meteor_improved": round(meteor_improved, 4),
                "meteor_single_agent": round(meteor_single, 4),
                "bleurt_zero_shot": round(bleurt_zero, 4),
                "bleurt_improved": round(bleurt_improved, 4),
                "bleurt_single_agent": round(bleurt_single, 4),
                "comet_zero_shot": round(comet_zero, 4),
                "comet_improved": round(comet_improved, 4),
                "comet_single_agent": round(comet_single, 4)
            })

        except Exception as e:
            logging.warning(f"Error on segment {idx}: {e}")
            continue

    df_results = pd.DataFrame(results)
    df_results.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    logging.info(f"Saved full evaluation results to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
