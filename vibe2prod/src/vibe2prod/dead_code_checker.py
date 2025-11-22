import libcst as cst
import libcst.matchers as m


class DeadCodeCollector(cst.CSTVisitor):
    """
    Finds:
    - unreachable code after return/raise/break/continue
    - if False / if 0 blocks
    - unused variables
    - unused parameters
    - unused imports
    """

    def __init__(self):
        # Store issues as strings
        self.issues = []

        # Track variables assigned + used
        self.assigned = set()
        self.used = set()

        # Track parameters per function
        self.current_params = []

        # Track imports
        self.imported_names = set()

    # ---------- IMPORTS ----------
    def visit_Import(self, node):
        for name in node.names:
            self.imported_names.add(name.name.value)

    def visit_ImportFrom(self, node):
        for name in node.names:
            if hasattr(name, "name"):
                self.imported_names.add(name.name.value)

    # ---------- VARIABLE USAGE ----------
    def visit_AssignTarget(self, node):
        if isinstance(node.target, cst.Name):
            self.assigned.add(node.target.value)

    def visit_Name(self, node):
        self.used.add(node.value)

    # ---------- FUNCTION & PARAMS ----------
    def visit_FunctionDef(self, node):
        # Track parameters
        self.current_params = [
            p.name.value
            for p in list(node.params.params)
            + list(node.params.posonly_params)
            + list(node.params.kwonly_params)
            if p.name is not None
        ]

    def leave_FunctionDef(self, original_node: cst.FunctionDef):
        # Check unused params
        for p in self.current_params:
            if p not in self.used:
                self.issues.append(
                    f"Parameter `{p}` in function `{original_node.name.value}` is never used."
                )


    # ---------- ALWAYS FALSE CONDITIONALS ----------
    def visit_If(self, node):
        # if False:
        if m.matches(node.test, m.Name("False")):
            self.issues.append("Found `if False:` block — always unreachable.")

        # if 0:
        if m.matches(node.test, m.Integer("0")):
            self.issues.append("Found `if 0:` block — always unreachable.")

        # if 1 == 2:
        if m.matches(node.test, m.Comparison()):
            try:
                left = node.test.left
                right = node.test.comparisons[0].comparator
                op = node.test.comparisons[0].operator

                if (
                    isinstance(left, cst.Integer)
                    and isinstance(right, cst.Integer)
                    and isinstance(op, cst.Equal)
                    and int(left.value) != int(right.value)
                ):
                    self.issues.append("Found always-false comparison such as `1 == 2`.")
            except Exception:
                pass

    # ---------- UNREACHABLE CODE ----------
    def visit_IndentedBlock(self, node: cst.IndentedBlock):
        saw_terminal = False
        for stmt in node.body:
            if saw_terminal:
                self.issues.append("Unreachable code detected after return/raise/break/continue.")
                break

            if isinstance(stmt, cst.SimpleStatementLine):
                for expr in stmt.body:
                    if isinstance(expr, (cst.Return, cst.Raise, cst.Break, cst.Continue)):
                        saw_terminal = True


    # ---------- END ----------
    def finalize(self):
        # unused variables
        for var in self.assigned:
            if var not in self.used:
                self.issues.append(f"Variable `{var}` is assigned but never used.")

        # unused imports
        for name in self.imported_names:
            if name not in self.used:
                self.issues.append(f"Import `{name}` appears unused.")


def analyze_dead_code(source_code: str):
    """
    Returns list of dead code issues.
    """
    try:
        tree = cst.parse_module(source_code)
    except Exception:
        return []

    visitor = DeadCodeCollector()
    tree.visit(visitor)
    visitor.finalize()
    return visitor.issues
