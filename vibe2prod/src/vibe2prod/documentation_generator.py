from __future__ import annotations

import ast
from typing import List, Dict, Any


def _format_args(args: ast.arguments) -> str:
    parts: List[str] = []

    # positional-only args (Python 3.8+)
    for arg in getattr(args, "posonlyargs", []):
        parts.append(arg.arg)

    # regular positional args
    for arg in args.args:
        parts.append(arg.arg)

    # *args
    if args.vararg is not None:
        parts.append("*" + args.vararg.arg)

    # keyword-only args
    for arg in args.kwonlyargs:
        parts.append(arg.arg + "=?")

    # **kwargs
    if args.kwarg is not None:
        parts.append("**" + args.kwarg.arg)

    return ", ".join(parts)


def _extract_functions(tree: ast.Module) -> List[Dict[str, Any]]:
    funcs: List[Dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ""
            sig = f"{node.name}({_format_args(node.args)})"
            funcs.append(
                {
                    "name": node.name,
                    "signature": sig,
                    "doc": doc.strip(),
                }
            )

    return funcs


def _extract_classes(tree: ast.Module) -> List[Dict[str, Any]]:
    classes: List[Dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node) or ""
            methods: List[Dict[str, Any]] = []

            for body_item in node.body:
                if isinstance(body_item, ast.FunctionDef):
                    m_doc = ast.get_docstring(body_item) or ""
                    m_sig = f"{body_item.name}({_format_args(body_item.args)})"
                    methods.append(
                        {
                            "name": body_item.name,
                            "signature": m_sig,
                            "doc": m_doc.strip(),
                        }
                    )

            classes.append(
                {
                    "name": node.name,
                    "doc": class_doc.strip(),
                    "methods": methods,
                }
            )

    return classes


def generate_docs(source_code: str, filename: str) -> str:
    """
    Generate Markdown documentation for a Python module.

    Uses:
    - The module docstring as high-level overview (if present).
    - Class and function docstrings.
    - Simple signatures derived from the AST.

    This is static (no LLM). If you want AI-enriched docs later,
    you can pass this output through an LLM as a second step.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return f"# Documentation for `{filename}`\n\nUnable to parse file."

    module_doc = ast.get_docstring(tree) or ""
    funcs = _extract_functions(tree)
    classes = _extract_classes(tree)

    lines: List[str] = []
    lines.append(f"# Documentation for `{filename}`")
    lines.append("")

    # Module overview
    if module_doc:
        lines.append("## Module Overview")
        lines.append(module_doc.strip())
    else:
        lines.append("## Module Overview")
        lines.append("No module-level docstring found. Add one to describe the purpose of this module.")
    lines.append("")

    # Classes
    if classes:
        lines.append("## Classes")
        lines.append("")
        for cls in classes:
            lines.append(f"### `{cls['name']}`")
            lines.append("")
            if cls["doc"]:
                lines.append(cls["doc"])
            else:
                lines.append("_No class docstring provided._")
            lines.append("")

            if cls["methods"]:
                lines.append("#### Methods")
                lines.append("")
                for m in cls["methods"]:
                    lines.append(f"- **`{m['signature']}`**")
                    if m["doc"]:
                        lines.append(f"  - {m['doc']}")
                    else:
                        lines.append("  - _No method docstring provided._")
                lines.append("")
    else:
        lines.append("## Classes")
        lines.append("No classes found.")
        lines.append("")

    # Functions
    if funcs:
        lines.append("## Functions")
        lines.append("")
        for fn in funcs:
            lines.append(f"### `{fn['signature']}`")
            lines.append("")
            if fn["doc"]:
                lines.append(fn["doc"])
            else:
                lines.append("_No function docstring provided._")
            lines.append("")
    else:
        lines.append("## Functions")
        lines.append("No top-level functions found.")
        lines.append("")

    return "\n".join(lines)
