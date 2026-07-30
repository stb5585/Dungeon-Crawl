"""Keep refactored package initializers limited to public API declarations."""

import ast
from pathlib import Path


SRC_ROOT = Path(__file__).parents[2] / "src"
PACKAGE_INITIALIZERS = tuple(sorted(SRC_ROOT.rglob("__init__.py")))


def test_package_initializers_contain_only_exports():
    allowed_statement_types = (ast.Expr, ast.Import, ast.ImportFrom)

    assert PACKAGE_INITIALIZERS
    for path in PACKAGE_INITIALIZERS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for statement in tree.body:
            if isinstance(statement, ast.Assign):
                assigned_names = {
                    target.id for target in statement.targets if isinstance(target, ast.Name)
                }
                assert assigned_names == {"__all__"}, path
                continue
            assert isinstance(statement, allowed_statement_types), (
                path,
                type(statement).__name__,
            )
