"""
Static (non-AI) comment / docstring enhancer.

Uses libcst to parse the Python file and:
- Adds a module-level docstring if missing.
- Adds class docstrings if missing.
- Adds function docstrings if missing.
- Adds simple inline comments before loops and conditionals inside functions.
- Adds a per-function complexity summary comment (loops, conditionals, nesting depth).
- Adds a per-function magic-number summary comment so they can be extracted to config/constants.

Existing docstrings are preserved.
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import libcst as cst


# ---------- Helpers for docstring detection/creation ----------


def _has_leading_docstring(statements: List[cst.BaseStatement]) -> bool:
    """
    Return True if the first non-empty statement is a string literal (docstring).
    """
    for stmt in statements:
        if isinstance(stmt, cst.EmptyLine):
            continue

        if (
            isinstance(stmt, cst.SimpleStatementLine)
            and len(stmt.body) == 1
            and isinstance(stmt.body[0], cst.Expr)
            and isinstance(stmt.body[0].value, cst.SimpleString)
        ):
            return True

        # First non-empty is not a docstring -> bail
        return False

    return False


def _body_starts_with_comment(body: Sequence[cst.BaseStatement]) -> bool:
    """
    True if the first statement in a block is already a comment-only line.
    """
    if not body:
        return False

    first = body[0]
    return isinstance(first, cst.EmptyLine) and first.comment is not None


def _make_module_docstring() -> cst.SimpleStatementLine:
    text = '"""TODO: Describe this module."""'
    return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(text))])


def _make_class_docstring(name: str) -> cst.SimpleStatementLine:
    inner = f"{name} class.\n\nTODO: Describe this class."
    text = f'"""{inner}"""'
    return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(text))])


def _make_function_docstring(
    name: str, param_names: List[str], has_return: bool
) -> cst.SimpleStatementLine:
    lines: List[str] = [
        f"{name} function.",
        "",
        "TODO: Describe this function.",
        "",
    ]

    if param_names:
        lines.append("Args:")
        for p in param_names:
            lines.append(f"    {p}: TODO: describe {p}.")
        lines.append("")

    if has_return:
        lines.append("Returns:")
        lines.append("    TODO: describe return value.")
        lines.append("")

    inner = "\n".join(lines).rstrip()
    text = f'"""{inner}"""'
    return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(text))])


# ---------- Inline comments for loops / conditionals ----------


def _make_loop_comment() -> cst.EmptyLine:
    comment = "# TODO: Review this loop."
    return cst.EmptyLine(comment=cst.Comment(comment))


def _make_if_comment() -> cst.EmptyLine:
    comment = "# TODO: Review this conditional."
    return cst.EmptyLine(comment=cst.Comment(comment))


# ---------- Complexity analysis ----------


def _analyze_complexity(
    statements: Sequence[cst.BaseStatement], depth: int = 1
) -> Tuple[int, int, int]:
    """
    Very rough static complexity estimate for a function body.

    Returns (loop_count, if_count, max_nesting_depth).

    depth=1 is top level inside function, depth grows when we enter loop/if bodies.
    """
    loops = 0
    ifs = 0
    max_depth = depth

    for stmt in statements:
        # For loop
        if isinstance(stmt, cst.For):
            loops += 1
            child_loops, child_ifs, child_depth = _analyze_complexity(
                stmt.body.body, depth + 1
            )
            loops += child_loops
            ifs += child_ifs
            max_depth = max(max_depth, child_depth)

            if stmt.orelse is not None:
                o_body = stmt.orelse.body.body
                child_loops, child_ifs, child_depth = _analyze_complexity(
                    o_body, depth + 1
                )
                loops += child_loops
                ifs += child_ifs
                max_depth = max(max_depth, child_depth)

        # While loop
        elif isinstance(stmt, cst.While):
            loops += 1
            child_loops, child_ifs, child_depth = _analyze_complexity(
                stmt.body.body, depth + 1
            )
            loops += child_loops
            ifs += child_ifs
            max_depth = max(max_depth, child_depth)

            if stmt.orelse is not None:
                o_body = stmt.orelse.body.body
                child_loops, child_ifs, child_depth = _analyze_complexity(
                    o_body, depth + 1
                )
                loops += child_loops
                ifs += child_ifs
                max_depth = max(max_depth, child_depth)

        # If statement
        elif isinstance(stmt, cst.If):
            ifs += 1
            child_loops, child_ifs, child_depth = _analyze_complexity(
                stmt.body.body, depth + 1
            )
            loops += child_loops
            ifs += child_ifs
            max_depth = max(max_depth, child_depth)

            if stmt.orelse is not None:
                o_body = stmt.orelse.body.body
                child_loops, child_ifs, child_depth = _analyze_complexity(
                    o_body, depth + 1
                )
                loops += child_loops
                ifs += child_ifs
                max_depth = max(max_depth, child_depth)

        # Other statements: may contain nested defs, but we ignore those for now.

    return loops, ifs, max_depth


def _make_complexity_comment(loops: int, ifs: int, depth: int) -> cst.EmptyLine | None:
    """
    Build a TODO comment summarising complexity, if it's non-trivial.

    Heuristics:
    - More than 1 loop, or
    - Nesting depth >= 3, or
    - More than 2 conditionals
    """
    if loops <= 1 and depth < 3 and ifs <= 2:
        return None

    comment = (
        f"# TODO: Review complexity: {loops} loop(s), "
        f"{ifs} conditional(s), max nesting depth {depth}."
    )
    return cst.EmptyLine(comment=cst.Comment(comment))


def _insert_complexity_comment(
    statements: List[cst.BaseStatement], complexity_comment: cst.EmptyLine | None
) -> List[cst.BaseStatement]:
    """
    Insert a complexity comment after the leading docstring (if any).

    Avoids inserting if a 'Review complexity' comment already exists.
    """
    if complexity_comment is None:
        return statements

    # Avoid duplicates if run multiple times.
    for s in statements:
        if (
            isinstance(s, cst.EmptyLine)
            and s.comment is not None
            and "Review complexity" in s.comment.value
        ):
            return statements

    new_statements = list(statements)

    # Skip initial empty lines
    idx = 0
    while idx < len(new_statements) and isinstance(new_statements[idx], cst.EmptyLine):
        idx += 1

    # Insert after first non-empty (usually docstring)
    insert_pos = idx + 1 if idx < len(new_statements) else len(new_statements)
    new_statements.insert(insert_pos, complexity_comment)
    return new_statements


# ---------- Magic number analysis ----------


def _collect_magic_numbers(func: cst.FunctionDef) -> List[str]:
    """
    Collect numeric literals used inside the function body, excluding trivial values.

    We treat -1, 0 and 1 as non-magic (they're very common).
    """

    class _Collector(cst.CSTVisitor):
        def __init__(self) -> None:
            self.ints = set()
            self.floats = set()

        def visit_Integer(self, node: cst.Integer) -> None:
            text = node.value.replace("_", "")
            try:
                value = int(text, 10)
            except ValueError:
                return
            if value not in (-1, 0, 1):
                self.ints.add(text)

        def visit_Float(self, node: cst.Float) -> None:
            # Any float is considered potentially magic.
            self.floats.add(node.value)

    collector = _Collector()
    func.body.visit(collector)
    nums = list(collector.ints | collector.floats)
    nums.sort()
    return nums


def _make_magic_numbers_comment(nums: List[str]) -> cst.EmptyLine | None:
    """
    Create a TODO comment summarising magic numbers, if any were found.
    """
    if not nums:
        return None

    joined = ", ".join(nums)
    comment = (
        "# TODO: Extract magic numbers into named constants / config: "
        f"{joined}."
    )
    return cst.EmptyLine(comment=cst.Comment(comment))


def _insert_magic_comment(
    statements: List[cst.BaseStatement], magic_comment: cst.EmptyLine | None
) -> List[cst.BaseStatement]:
    """
    Insert the magic-number comment near the top of the function body.

    Prefer to put it after the complexity comment if present, otherwise
    after the docstring.
    """
    if magic_comment is None:
        return statements

    # Avoid duplicates
    for s in statements:
        if (
            isinstance(s, cst.EmptyLine)
            and s.comment is not None
            and "magic numbers" in s.comment.value.lower()
        ):
            return statements

    new_statements = list(statements)

    # Find complexity comment if present
    complexity_pos = None
    for i, s in enumerate(new_statements):
        if (
            isinstance(s, cst.EmptyLine)
            and s.comment is not None
            and "Review complexity" in s.comment.value
        ):
            complexity_pos = i
            break

    if complexity_pos is not None:
        insert_pos = complexity_pos + 1
    else:
        # Otherwise insert after docstring (first non-empty)
        idx = 0
        while idx < len(new_statements) and isinstance(
            new_statements[idx], cst.EmptyLine
        ):
            idx += 1
        insert_pos = idx + 1 if idx < len(new_statements) else len(new_statements)

    new_statements.insert(insert_pos, magic_comment)
    return new_statements


# ---------- Main transformer ----------


class DocstringAndCommentAdder(cst.CSTTransformer):
    """
    Add docstrings to module, classes and functions if missing.
    Also add simple inline comments before loops and conditionals, and
    a per-function complexity summary comment and magic-number summary comment.
    """

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if _has_leading_docstring(list(updated_node.body)):
            return updated_node

        doc = _make_module_docstring()
        new_body = [doc] + list(updated_node.body)
        return updated_node.with_changes(body=new_body)

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        statements = list(updated_node.body.body)

        if _has_leading_docstring(statements):
            return updated_node

        doc = _make_class_docstring(updated_node.name.value)
        new_body = [doc] + statements
        new_block = updated_node.body.with_changes(body=new_body)
        return updated_node.with_changes(body=new_block)

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        # Start from the function body statements
        statements = list(updated_node.body.body)

        # Ensure function-level docstring exists
        if not _has_leading_docstring(statements):
            params = updated_node.params
            param_names: List[str] = []

            for p in (
                list(params.posonly_params)
                + list(params.params)
                + list(params.kwonly_params)
            ):
                if p.name is not None:
                    param_names.append(p.name.value)

            has_return = updated_node.returns is not None

            doc = _make_function_docstring(
                updated_node.name.value, param_names, has_return
            )
            statements = [doc] + statements

        # Complexity analysis based on the *original* body
        loops, ifs, depth = _analyze_complexity(original_node.body.body, depth=1)
        complexity_comment = _make_complexity_comment(loops, ifs, depth)
        statements = _insert_complexity_comment(statements, complexity_comment)

        # Magic number analysis based on original function
        magic_nums = _collect_magic_numbers(original_node)
        magic_comment = _make_magic_numbers_comment(magic_nums)
        statements = _insert_magic_comment(statements, magic_comment)

        # Inline comments for loops/ifs
        statements = self._add_inline_comments_to_block(statements)

        new_block = updated_node.body.with_changes(body=statements)
        return updated_node.with_changes(body=new_block)

    # ----- Inline comments for loops / conditionals inside a block -----

    def _add_inline_comments_to_block(
        self, statements: List[cst.BaseStatement]
    ) -> List[cst.BaseStatement]:
        """
        Walk a list of statements and, for any For/While/If inside, prepend a comment
        line inside their body if none exists yet.
        """
        new_statements: List[cst.BaseStatement] = []

        for stmt in statements:
            # For loop
            if isinstance(stmt, cst.For):
                body_stmts = list(stmt.body.body)
                if not _body_starts_with_comment(body_stmts):
                    loop_comment = _make_loop_comment()
                    body_stmts = [loop_comment] + body_stmts
                new_body = stmt.body.with_changes(body=body_stmts)
                stmt = stmt.with_changes(body=new_body)

            # While loop
            if isinstance(stmt, cst.While):
                body_stmts = list(stmt.body.body)
                if not _body_starts_with_comment(body_stmts):
                    loop_comment = _make_loop_comment()
                    body_stmts = [loop_comment] + body_stmts
                new_body = stmt.body.with_changes(body=body_stmts)
                stmt = stmt.with_changes(body=new_body)

            # If statement
            if isinstance(stmt, cst.If):
                body_stmts = list(stmt.body.body)
                if not _body_starts_with_comment(body_stmts):
                    if_comment = _make_if_comment()
                    body_stmts = [if_comment] + body_stmts
                new_body = stmt.body.with_changes(body=body_stmts)
                stmt = stmt.with_changes(body=new_body)

            new_statements.append(stmt)

        return new_statements


# ---------- Public API ----------


def enhance_comments(source_code: str, use_llm: bool = False) -> str:
    """
    Static implementation: ignore use_llm and always use the CST-based enhancer.

    If parsing fails for any reason, return the original code unchanged.
    """
    try:
        module = cst.parse_module(source_code)
    except Exception:
        # If the file is not valid Python, don't break the pipeline.
        return source_code

    new_module = module.visit(DocstringAndCommentAdder())
    return new_module.code
