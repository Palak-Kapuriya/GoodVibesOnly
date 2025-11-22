import sys
import argparse
from pathlib import Path

from .pipeline import process_file


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert vibe-coded Python into production-ready code with comments, "
            "static analysis, optional AI refactor, and documentation."
        )
    )
    parser.add_argument("input", help="Path to the Python file to process.")
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Enable AI-based refactoring (if configured in llm_client.py).",
    )

    args = parser.parse_args()
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: File not found: {input_path}")
        sys.exit(1)

    print(">>")

    try:
        commented_path, prod_path, report_path, ai_path, docs_path = process_file(
            input_path, use_llm=args.use_llm
        )
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

    print(f"Commented file written to: {commented_path}")
    print(f"Production-ready file written to: {prod_path}")
    print(f"Quality report written to: {report_path}")
    if ai_path is not None:
        print(f"AI-refactored file written to: {ai_path}")
    print(f"Documentation written to: {docs_path}")
