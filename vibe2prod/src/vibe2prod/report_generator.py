import libcst as cst
from typing import Dict, Any, List

from .naming_checker import analyze_naming
from .dead_code_checker import analyze_dead_code
from .duplicate_checker import analyze_duplicates


# --------------------------------------------------
# Utility: Walk CST to extract function statistics
# --------------------------------------------------

class FunctionCollector(cst.CSTVisitor):
    def __init__(self):
        self.functions: List[Dict[str, Any]] = []

    def visit_FunctionDef(self, node: cst.FunctionDef):
        name = node.name.value
        body = node.body.body

        # Count loops / ifs / depth
        loops, ifs, depth = analyze_complexity(body)

        # Count statements
        stmt_count = len(body)

        # Magic numbers
        magic = extract_magic_numbers(node)

        self.functions.append(
            {
                "name": name,
                "loops": loops,
                "ifs": ifs,
                "depth": depth,
                "stmts": stmt_count,
                "magic": magic,
            }
        )


# --------------------------------------------------
# Complexity Scanner from earlier steps
# --------------------------------------------------

def analyze_complexity(statements, depth=1):
    loops = 0
    ifs = 0
    max_depth = depth

    for stmt in statements:
        if isinstance(stmt, cst.For) or isinstance(stmt, cst.While):
            loops += 1
            child_loops, child_ifs, child_depth = analyze_complexity(
                stmt.body.body, depth + 1
            )
            loops += child_loops
            ifs += child_ifs
            max_depth = max(max_depth, child_depth)

            if stmt.orelse:
                o_body = stmt.orelse.body.body
                child_loops, child_ifs, child_depth = analyze_complexity(
                    o_body, depth + 1
                )
                loops += child_loops
                ifs += child_ifs
                max_depth = max(max_depth, child_depth)

        elif isinstance(stmt, cst.If):
            ifs += 1
            child_loops, child_ifs, child_depth = analyze_complexity(
                stmt.body.body, depth + 1
            )
            loops += child_loops
            ifs += child_ifs
            max_depth = max(max_depth, child_depth)

            if stmt.orelse:
                o_body = stmt.orelse.body.body
                child_loops, child_ifs, child_depth = analyze_complexity(
                    o_body, depth + 1
                )
                loops += child_loops
                ifs += child_ifs
                max_depth = max(max_depth, child_depth)

    return loops, ifs, max_depth


# --------------------------------------------------
# Magic Number Extraction
# --------------------------------------------------

def extract_magic_numbers(func_node: cst.FunctionDef):
    class LiteralCollector(cst.CSTVisitor):
        def __init__(self):
            self.nums = set()

        def visit_Integer(self, node):
            try:
                value = int(node.value)
                if value not in (0, 1, -1):
                    self.nums.add(value)
            except Exception:
                pass

        def visit_Float(self, node):
            try:
                value = float(node.value)
                self.nums.add(value)
            except Exception:
                pass

    collector = LiteralCollector()
    func_node.visit(collector)
    return collector.nums


# --------------------------------------------------
# Main Report Generator
# --------------------------------------------------

def generate_report(source_code: str, filename: str) -> str:
    lines = []
    lines.append(f"# Quality Report for `{filename}`\n")

    # Parse module
    try:
        module = cst.parse_module(source_code)
    except Exception:
        return "# Report Unavailable — Parsing Failed"

    # Collect per-function metrics
    fc = FunctionCollector()
    module.visit(fc)

    # --------------------------------------------------
    # Per-function metrics
    # --------------------------------------------------
    for func in fc.functions:
        lines.append(f"## Function: `{func['name']}`")
        lines.append(f"- Loops: {func['loops']}")
        lines.append(f"- Conditionals: {func['ifs']}")
        lines.append(f"- Max Nesting Depth: {func['depth']}")
        lines.append(f"- Total Statements: {func['stmts']}")

        # Magic numbers sorted safely
        if func["magic"]:
            nums = ", ".join(sorted(str(n) for n in func["magic"]))
            lines.append(f"- Magic Numbers: {nums}")
        else:
            lines.append("- Magic Numbers: None")

        # Recommendations
        recs = []
        if func["depth"] >= 4:
            recs.append("⚠️ High nesting — consider splitting logic.")
        if func["loops"] >= 3:
            recs.append("⚠️ Loop-heavy — may indicate repeated patterns.")
        if func["ifs"] >= 5:
            recs.append("⚠️ Many conditionals — may hide complex behavior.")
        if func["stmts"] >= 15:
            recs.append("⚠️ Function is long — consider breaking into helpers.")

        if recs:
            lines.append("\n### Recommendations")
            for r in recs:
                lines.append(f"- {r}")
        lines.append("")

    # --------------------------------------------------
    # Naming Analysis (F)
    # --------------------------------------------------

    naming_issues = analyze_naming(source_code)

    lines.append("## Naming Issues")

    if naming_issues:
        for issue in naming_issues:
            lines.append(f"- {issue}")
    else:
        lines.append("No naming issues detected.")

    lines.append("")
    
    # ---------- Dead Code Analysis ----------
    dead_issues = analyze_dead_code(source_code)

    lines.append("## Dead Code Issues")

    if dead_issues:
        for issue in dead_issues:
            lines.append(f"- {issue}")
    else:
        lines.append("No dead code detected.")

    lines.append("")

    # ---------- Duplicate Logic / Clone Detection ----------
    dupes = analyze_duplicates(source_code)

    lines.append("## Duplicate Logic")

    if dupes:
        for h, items in dupes.items():
            func_list = sorted({fn for fn, _ in items})
            lines.append(f"- Duplicate block (hash `{h[:6]}`) found in functions: {', '.join(func_list)}")
    else:
        lines.append("No duplicate logic detected.")

    lines.append("")



    # Done
    return "\n".join(lines)
