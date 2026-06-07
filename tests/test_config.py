"""Config composition + override tests."""
import textwrap

from uavroadmark.utils.config import load_config, merge_configs


def test_merge_is_deep():
    base = {"a": {"x": 1, "y": 2}, "b": 3}
    over = {"a": {"y": 20}, "c": 4}
    out = merge_configs(base, over)
    assert out["a"]["x"] == 1   # untouched
    assert out["a"]["y"] == 20  # overridden
    assert out["b"] == 3
    assert out["c"] == 4


def test_base_composition_and_override(tmp_path):
    (tmp_path / "base.yaml").write_text(textwrap.dedent("""
        train:
          lr: 0.001
          epochs: 10
    """))
    (tmp_path / "exp.yaml").write_text(textwrap.dedent("""
        _base_: base.yaml
        train:
          epochs: 50
        run_name: exp1
    """))
    cfg = load_config(tmp_path / "exp.yaml", overrides=["train.lr=3e-4"])
    assert cfg["train"]["epochs"] == 50      # exp overrides base
    assert cfg["train"]["lr"] == 3e-4        # CLI overrides everything
    assert cfg["run_name"] == "exp1"


def test_dotted_access():
    cfg = load_config_from_dict({"a": {"b": {"c": 7}}})
    assert cfg.get_dotted("a.b.c") == 7
    assert cfg.get_dotted("a.b.missing", default=-1) == -1


def load_config_from_dict(d):
    from uavroadmark.utils.config import _to_config
    return _to_config(d)
