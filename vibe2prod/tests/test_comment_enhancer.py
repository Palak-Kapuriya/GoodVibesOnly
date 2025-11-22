from vibe2prod.comment_enhancer import enhance_comments

def test_enhance_comments_noop_without_llm():
    code = "def f(x):\n    return x\n"
    out = enhance_comments(code, use_llm=False)
    assert out == code
