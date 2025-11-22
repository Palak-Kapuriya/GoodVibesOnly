import libcst as cst
import re


SNAKE = re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL = re.compile(r"^[A-Z][a-zA-Z0-9]+$")
SCREAMING = re.compile(r"^[A-Z0-9_]+$")


class NamingIssueCollector(cst.CSTVisitor):
    """
    Collects naming rule violations:
    - function not snake_case
    - class not PascalCase
    - variables too short or not snake_case
    - constants not SCREAMING_SNAKE_CASE
    """

    def __init__(self):
        self.issues = []

    # ---------- Function Definitions ----------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        name = node.name.value
        if not SNAKE.match(name):
            self.issues.append(
                f"Function `{name}` is not snake_case."
            )

        # check parameters
        for p in (
            list(node.params.posonly_params)
            + list(node.params.params)
            + list(node.params.kwonly_params)
        ):
            if p.name is None:
                continue
            pname = p.name.value
            if len(pname) <= 1 and pname not in ("i", "j", "k"):
                self.issues.append(
                    f"Parameter `{pname}` is too short. Prefer descriptive names."
                )
            elif not SNAKE.match(pname):
                self.issues.append(
                    f"Parameter `{pname}` is not snake_case."
                )

    # ---------- Class Definitions ----------
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        name = node.name.value
        if not PASCAL.match(name):
            self.issues.append(
                f"Class `{name}` is not PascalCase."
            )

    # ---------- Assignments ----------
    def visit_Assign(self, node: cst.Assign) -> None:
        for t in node.targets:
            if isinstance(t.target, cst.Name):
                vname = t.target.value

                # detect constant
                if vname.isupper() and len(vname) > 1:
                    if not SCREAMING.match(vname):
                        self.issues.append(
                            f"Constant `{vname}` should be SCREAMING_SNAKE_CASE."
                        )
                    continue

                # too short variable
                if len(vname) == 1 and vname not in ("i", "j", "k"):
                    self.issues.append(
                        f"Variable `{vname}` is too short — unclear purpose."
                    )
                    continue

                # not snake_case
                if not SNAKE.match(vname):
                    self.issues.append(
                        f"Variable `{vname}` is not snake_case."
                    )

def analyze_naming(source_code: str):
    """
    Run naming conventions analysis.
    Returns a list of issues found.
    """
    try:
        tree = cst.parse_module(source_code)
    except Exception:
        return []

    visitor = NamingIssueCollector()
    tree.visit(visitor)
    return visitor.issues
