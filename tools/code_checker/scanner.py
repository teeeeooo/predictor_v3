"""AST-based Python source scanner for reference map generation."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

DEFAULT_EXCLUDE_DIRS = {
    "tests",
    "result_reports",
    "docs",
    "__pycache__",
    ".git",
    ".code_checker",
    ".pytest_cache",
    ".devcontainer",
    ".claude",
    "archive",
    "summaries",
    "memory",
    "designs",
    "ui_ux",
    "reference_files",
}


@dataclass
class Symbol:
    name: str
    line: int
    end_line: int
    kind: str  # "class", "top_level_function", "method", "nested_function", "constant"


@dataclass
class FileInfo:
    path: Path
    loc: int
    classes: List[Symbol] = field(default_factory=list)
    top_level_functions: List[Symbol] = field(default_factory=list)
    methods: List[Symbol] = field(default_factory=list)
    nested_functions: List[Symbol] = field(default_factory=list)
    constants: List[Symbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)

    @property
    def functions(self) -> List[Symbol]:
        """All functions for backwards compatibility (hotspot analysis)."""
        return self.top_level_functions + self.methods + self.nested_functions


def _count_loc(source: str) -> int:
    """Count non-empty, non-comment lines (naive)."""
    count = 0
    for line in source.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            count += 1
    return count


class _SymbolVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.classes: List[Symbol] = []
        self.top_level_functions: List[Symbol] = []
        self.methods: List[Symbol] = []
        self.nested_functions: List[Symbol] = []
        self.constants: List[Symbol] = []
        self.imports: List[str] = []
        self._context_stack: List[str] = []

    def _is_module_level(self) -> bool:
        return len(self._context_stack) == 0

    def _current_context(self) -> str | None:
        return self._context_stack[-1] if self._context_stack else None

    def _push(self, ctx: str) -> None:
        self._context_stack.append(ctx)

    def _pop(self) -> None:
        self._context_stack.pop()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(
            Symbol(
                name=node.name,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno),
                kind="class",
            )
        )
        self._push("class")
        self.generic_visit(node)
        self._pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        ctx = self._current_context()
        if self._is_module_level():
            kind = "top_level_function"
            self.top_level_functions.append(
                Symbol(
                    name=node.name,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    kind=kind,
                )
            )
        elif ctx == "class":
            kind = "method"
            self.methods.append(
                Symbol(
                    name=node.name,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    kind=kind,
                )
            )
        else:
            kind = "nested_function"
            self.nested_functions.append(
                Symbol(
                    name=node.name,
                    line=node.lineno,
                    end_line=getattr(node, "end_lineno", node.lineno),
                    kind=kind,
                )
            )
        self._push("function")
        self.generic_visit(node)
        self._pop()

    def visit_Assign(self, node: ast.Assign) -> None:
        if self._is_module_level():
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    self.constants.append(
                        Symbol(
                            name=target.id,
                            line=node.lineno,
                            end_line=getattr(node, "end_lineno", node.lineno),
                            kind="constant",
                        )
                    )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        mod = node.module or ""
        for alias in node.names:
            self.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        self.generic_visit(node)


def scan_file(path: Path) -> FileInfo:
    """Parse a single Python file and extract symbols/imports."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    visitor = _SymbolVisitor()
    visitor.visit(tree)
    return FileInfo(
        path=path,
        loc=_count_loc(source),
        classes=visitor.classes,
        top_level_functions=visitor.top_level_functions,
        methods=visitor.methods,
        nested_functions=visitor.nested_functions,
        constants=visitor.constants,
        imports=visitor.imports,
    )


def discover_python_files(
    root: Path,
    *,
    exclude_dirs: Iterable[str] | None = None,
) -> List[Path]:
    """Find all .py files under *root*, skipping *exclude_dirs*."""
    exclude = set(exclude_dirs or DEFAULT_EXCLUDE_DIRS)
    files: List[Path] = []
    for py_path in root.rglob("*.py"):
        if any(part in exclude for part in py_path.relative_to(root).parts[:-1]):
            continue
        files.append(py_path)
    return sorted(files)
