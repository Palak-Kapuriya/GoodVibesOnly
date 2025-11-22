import hashlib
import libcst as cst
from libcst import metadata


def normalize_node(node: cst.CSTNode) -> str:
    """
    Convert a CST node into a normalized structural string:
    - variable names removed
    - function names removed
    - whitespace irrelevant
    """
    class Normalizer(cst.CSTTransformer):
        def leave_Name(self, original_node, updated_node):
            return updated_node.with_changes(value="<var>")

        def leave_Attribute(self, original_node, updated_node):
            return updated_node.with_changes(attr=cst.Name("<attr>"))

        def leave_FunctionDef(self, original_node, updated_node):
            return updated_node.with_changes(name=cst.Name("<func>"))

    try:
        # First normalize the CST structure
        new_node = node.visit(Normalizer())

        # Safely convert *any* CST node into code
        wrapper = cst.Module(body=[])
        return wrapper.code_for_node(new_node)

    except Exception:
        # Fallback: try best-effort serialization
        wrapper = cst.Module(body=[])
        return wrapper.code_for_node(node)



def structural_hash(text: str) -> str:
    """
    MD5 hash of normalized text.
    """
    text = text.strip()
    return hashlib.md5(text.encode("utf-8")).hexdigest()


class BlockCollector(cst.CSTVisitor):
    """
    Collects structural blocks inside functions.
    Uses AST-based normalization and full multi-statement
    block hashing.
    """

    METADATA_DEPENDENCIES = (metadata.PositionProvider,)

    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.blocks = []  # list of (hash, func_name, text)

    def visit_FunctionDef(self, node: cst.FunctionDef):
        func_name = node.name.value

        # We analyze the full sequence of statements inside the function
        stmts = node.body.body

        # slide windows of size 2–6 consecutive statements
        for window_size in range(2, 7):
            for i in range(len(stmts) - window_size + 1):
                block = stmts[i : i + window_size]

                # get the actual source code for each statement sequentially
                pos_start = self.get_metadata(metadata.PositionProvider, block[0]).start.line - 1
                pos_end = self.get_metadata(metadata.PositionProvider, block[-1]).end.line
                raw_text = "\n".join(self.source_lines[pos_start:pos_end])

                # normalize by CST structure
                structural_repr = "\n".join(
                    normalize_node(stmt) for stmt in block
                )

                h = structural_hash(structural_repr)

                self.blocks.append((h, func_name, raw_text))


def analyze_duplicates(source_code: str):
    """
    Detect duplicate multi-line logic blocks.
    Returns {hash: [(func_name, block), ...]}
    """
    try:
        module = cst.parse_module(source_code)
    except Exception:
        return {}

    wrapper = cst.metadata.MetadataWrapper(module)
    lines = source_code.split("\n")

    collector = BlockCollector(lines)
    wrapper.visit(collector)

    dup_map = {}

    for h, fn, text in collector.blocks:
        if h not in dup_map:
            dup_map[h] = []
        dup_map[h].append((fn, text))

    # filter only hashes with more than one occurrence
    return {h: v for h, v in dup_map.items() if len(v) > 1}
