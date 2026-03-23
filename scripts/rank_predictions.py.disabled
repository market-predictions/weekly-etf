from pathlib import Path
import os
import zipfile
import shutil
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent
ZIP_PATH = BASE_DIR / "Today_Predictions.zip"
BUILD_DIR = BASE_DIR / "build_predictions"
EXTRACT_DIR = BASE_DIR / "extracted_predictions"
PROMPT_PATH = BASE_DIR / "prompts" / "MASTERPROMPT_Top10_Prediction_Auditor_v6.txt"
OUTPUT_DIR = BASE_DIR / "output"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def collect_file_text(root: Path) -> str:
    parts = []

    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in [".json", ".csv", ".txt", ".md", ".log"]:
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                content = f"<<FAILED TO READ FILE: {e}>>"

            parts.append(f"\n--- FILE: {path.relative_to(root)} ---\n")
            parts.append(content)

    return "\n".join(parts)


def extract_zip() -> None:
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"ZIP not found: {ZIP_PATH}")

    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(EXTRACT_DIR)


def get_input_root() -> Path:
    # Prefer direct files from build_predictions
    if BUILD_DIR.exists():
        files = [p for p in BUILD_DIR.rglob("*") if p.is_file()]
        if files:
            print(f"Using direct files from: {BUILD_DIR}")
            return BUILD_DIR

    # Fallback to ZIP
    print("No direct files found in build_predictions, falling back to ZIP")
    extract_zip()
    return EXTRACT_DIR


def main() -> None:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Masterprompt not found: {PROMPT_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_root = get_input_root()

    masterprompt = PROMPT_PATH.read_text(encoding="utf-8", errors="replace")
    files_text = collect_file_text(input_root)

    prompt = f"""
{masterprompt}

Apply this masterprompt to the prediction files below.

Important:
- Use the files as the source of truth.
- Do not invent missing values.
- If fields are missing, say so clearly.
- Prefer ranking/top/integrity files when available.
- Return both:
  1. a readable markdown report
  2. a strict JSON object

Required JSON format:
{{
  "run_date": "",
  "top10": [
    {{
      "rank": 1,
      "symbol": "",
      "side": "",
      "confidence": "",
      "score": null,
      "setup": "",
      "entry": null,
      "stop": null,
      "tp": null,
      "reason": ""
    }}
  ],
  "warnings": []
}}

Prediction files:
{files_text}
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt,
    )

    text = response.output_text

    (OUTPUT_DIR / "daily_top10.md").write_text(text, encoding="utf-8")

    print("Saved output/daily_top10.md")


if __name__ == "__main__":
    main()
