import ast
from typing import Dict

def check_comment_drift(source: str) -> Dict[str, str]:
    """
    Detect mismatches between code and its comments/docstrings.
    Returns suggestions for updates.
    """

    issues = {}
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            fn_name = node.name
            doc = ast.get_docstring(node) or ""

            # Parameters actually present
            real_params = [a.arg for a in node.args.args]

            # Parameters mentioned in docstring
            doc_params = []
            for line in doc.splitlines():
                if ":" in line:
                    maybe_param = line.split(":")[0].strip()
                    doc_params.append(maybe_param)

            # Find missing or outdated parameter descriptions
            missing = set(real_params) - set(doc_params)
            extra = set(doc_params) - set(real_params)

            msg = []

            if missing:
                msg.append(f"Missing param docs: {', '.join(missing)}")
            if extra:
                msg.append(f"Docstring mentions params not in code: {', '.join(extra)}")

            # Return mismatch
            returns_something = any(isinstance(n, ast.Return) and n.value is not None
                                    for n in ast.walk(node))
            if returns_something and "return" not in doc.lower():
                msg.append("Docstring missing return description.")
            if not returns_something and "return" in doc.lower():
                msg.append("Docstring claims a return value but function returns nothing.")

            if msg:
                issues[fn_name] = "\n".join(msg)

    return issues
