import subprocess
import tempfile
from pathlib import Path


def _run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception:
        pass


def make_production_ready(source_code: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / "temp.py"
        tmp_file.write_text(source_code)

        _run_cmd(["black", str(tmp_file)])
        _run_cmd(["ruff", "check", str(tmp_file), "--fix"])

        return tmp_file.read_text()
