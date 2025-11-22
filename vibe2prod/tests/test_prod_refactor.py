from vibe2prod.prod_refactor import make_production_ready

def test_make_production_ready_returns_string():
    code = "x=1\n"
    out = make_production_ready(code)
    assert isinstance(out, str)
    assert "x" in out
