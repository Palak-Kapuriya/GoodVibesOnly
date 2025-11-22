from pathlib import Path

from .comment_enhancer import enhance_comments
from .prod_refactor import make_production_ready
from .report_generator import generate_report
from .llm_client import rewrite_code_with_llm
from .documentation_generator import generate_docs
from .comment_drift_checker import check_comment_drif

def process_file(input_path: Path, use_llm: bool = False):
    # Read original source
    original_code = input_path.read_text(encoding="utf-8")

    # Step 1 — Comment enrichment
    commented_code = enhance_comments(original_code, use_llm=use_llm)
    commented_path = input_path.with_name(
        input_path.stem + "_commented" + input_path.suffix
    )
    commented_path.write_text(commented_code, encoding="utf-8")
    
    from .comment_drift_checker import check_comment_drift

    # After commented_code is generated:
    drift_issues = check_comment_drift(commented_code)

    if drift_issues:
        # Optional: Add drift issues into report
        report_text += "\n\n## Comment Drift Detected\n"
        for fn, issue in drift_issues.items():
            report_text += f"### {fn}\n{issue}\n\n"


    # Step 2 — Report
    report_text = generate_report(commented_code, input_path.name)
    report_path = input_path.with_name(input_path.stem + "_report.md")
    report_path.write_text(report_text, encoding="utf-8")

    # Step 3 — Static production refactor
    prod_code = make_production_ready(commented_code)
    prod_path = input_path.with_name(
        input_path.stem + "_prod" + input_path.suffix
    )
    prod_path.write_text(prod_code, encoding="utf-8")

    # Step 4 — AI refactor (optional)
    ai_code = None
    ai_path = None
    if use_llm:
        ai_code = rewrite_code_with_llm(commented_code)
        ai_path = input_path.with_name(
            input_path.stem + "_ai" + input_path.suffix
        )
        ai_path.write_text(ai_code, encoding="utf-8")

    # Step 5 — Documentation
    doc_source = ai_code if ai_code is not None else prod_code
    docs_text = generate_docs(doc_source, input_path.name)
    docs_path = input_path.with_name(input_path.stem + "_docs.md")
    docs_path.write_text(docs_text, encoding="utf-8")

    return commented_path, prod_path, report_path, ai_path, docs_path
