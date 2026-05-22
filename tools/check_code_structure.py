"""Project-wide structural guard for new code (Issue 119).

Conservative first version. Designed to be run from the repo root:

    python3 -B tools/check_code_structure.py [--verbose]

Checks:

1. ``core/`` files must not import ``ui``, ``ui_tk``, ``PyQt5``, or
   ``tkinter`` (calculator core stays pure-Python / framework-free).
2. ``ui_tk/`` files must not import ``PyQt5`` or the PyQt ``ui``
   package (Tkinter shell is independent of PyQt).
3. ``app_*.py`` entrypoints at repo root must be thin: no class
   definitions, ≤ 3 module-level ``def``\\s, ≤ 80 LOC.
4. ``ui_tk/`` lightweight shell anti-pattern: a single file must not
   bundle shell + tab + section + resolver + result-panel
   responsibilities (the 116 spike shape).
5. Soft LOC / class-count limits per production file
   (``core/``, ``ui/``, ``ui_tk/``, ``scripts/``). Known-large
   historical files are allowlisted (see ``LOC_ALLOWLIST`` /
   ``CLASS_ALLOWLIST``).

The script reads Python source files only — no PyQt / Tkinter
imports, no Excel / numpy / pandas. External dependency: none.

Exit code is non-zero when any check reports a violation. Soft-limit
findings are reported as warnings and do NOT fail the run.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Banned import roots per layer. A file in ``layer`` cannot import any
# module whose dotted name starts with one of these roots.
BANNED_IMPORTS: dict = {
    "core": ("ui", "ui_tk", "PyQt5", "tkinter"),
    "ui_tk": ("PyQt5", "ui"),
}

# LOC soft limit (warning, not failure) for production source files.
LOC_SOFT_LIMIT = 400

# Class-count soft limit (warning) per file.
CLASS_SOFT_LIMIT = 5

# Files exempt from LOC soft limit. Paths are relative to repo root.
LOC_ALLOWLIST: Set[str] = {
    "core/_legacy/calculator_iso16358_legacy.py",
    "core/calculator_iso16358.py",
    "core/calculator_ks_c9306.py",
    "core/calculator_ahri_hspf2.py",
    "core/calculator_en14825.py",
    "core/calculator_asnzs_hspf_excel.py",
    "ui/calc_window.py",
    "ui/calculators_2point.py",
    "ui/spreadsheet_table.py",
}

# Files exempt from class-count soft limit.
CLASS_ALLOWLIST: Set[str] = {
    "core/_legacy/calculator_iso16358_legacy.py",
    "ui/calculators_2point.py",
    "ui/spreadsheet_table.py",
    "ui/calc_window.py",
}

# Thin app entrypoint limits.
APP_ENTRYPOINT_MAX_LOC = 80
APP_ENTRYPOINT_MAX_FUNCS = 3

# Roots that get LOC / class-count soft-limit reporting.
PRODUCTION_ROOTS: Tuple[str, ...] = ("core", "ui", "ui_tk", "scripts")


# ---------------------------------------------------------------------------
# Finding type
# ---------------------------------------------------------------------------


class Finding:
    """A single guard result.

    ``severity`` is either ``"error"`` (fails the run) or ``"warning"``
    (reported but does not change exit code).
    """

    __slots__ = ("severity", "path", "message")

    def __init__(self, severity: str, path: str, message: str) -> None:
        self.severity = severity
        self.path = path
        self.message = message

    def __repr__(self) -> str:  # pragma: no cover — debugging convenience
        return f"Finding({self.severity!r}, {self.path!r}, {self.message!r})"


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested)
# ---------------------------------------------------------------------------


def _module_root(import_name: str) -> str:
    """Return the top-level package portion of an import name."""
    return import_name.split(".", 1)[0]


def _imported_modules(tree: ast.AST) -> Set[str]:
    """Collect top-level module names referenced by ``import`` /
    ``from`` statements in ``tree``."""
    modules: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(_module_root(alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import — skip, not subject to ban list
                continue
            if node.module:
                modules.add(_module_root(node.module))
    return modules


def check_banned_imports(
    source: str,
    relpath: str,
    layer: str,
    banned_roots: Sequence[str],
) -> List[Finding]:
    """Return findings for banned imports inside ``source``.

    ``layer`` is just the human-readable label used in messages
    (e.g. ``"core"``).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Finding("error", relpath, f"syntax error: {exc}")]

    findings: List[Finding] = []
    for module in sorted(_imported_modules(tree)):
        if module in banned_roots:
            findings.append(
                Finding(
                    "error",
                    relpath,
                    f"{layer}/ layer must not import '{module}'",
                )
            )
    return findings


def _count_module_classes(tree: ast.AST) -> int:
    return sum(
        1
        for node in tree.body  # type: ignore[attr-defined]
        if isinstance(node, ast.ClassDef)
    )


def _count_module_functions(tree: ast.AST) -> int:
    return sum(
        1
        for node in tree.body  # type: ignore[attr-defined]
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def _loc(source: str) -> int:
    return source.count("\n") + (0 if source.endswith("\n") else 1)


def check_app_entrypoint_thin(source: str, relpath: str) -> List[Finding]:
    """``app_*.py`` files at repo root must be thin."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Finding("error", relpath, f"syntax error: {exc}")]

    findings: List[Finding] = []
    class_count = _count_module_classes(tree)
    if class_count > 0:
        findings.append(
            Finding(
                "error",
                relpath,
                f"app entrypoint must not define classes (found {class_count})",
            )
        )

    func_count = _count_module_functions(tree)
    if func_count > APP_ENTRYPOINT_MAX_FUNCS:
        findings.append(
            Finding(
                "error",
                relpath,
                "app entrypoint must stay thin: at most "
                f"{APP_ENTRYPOINT_MAX_FUNCS} module-level functions "
                f"(found {func_count})",
            )
        )

    loc = _loc(source)
    if loc > APP_ENTRYPOINT_MAX_LOC:
        findings.append(
            Finding(
                "error",
                relpath,
                f"app entrypoint must stay thin: at most "
                f"{APP_ENTRYPOINT_MAX_LOC} LOC (found {loc})",
            )
        )

    return findings


def _responsibility_kinds_defined(tree: ast.Module) -> Set[str]:
    """Return the set of responsibility kinds *defined* in ``tree``.

    Uses AST definitions only — class names, function names, top-level
    assignment targets. Imports do not count.
    """
    kinds: Set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            name = node.name
            if name.endswith("Tab"):
                kinds.add("tab")
            elif name.endswith("Section"):
                kinds.add("section")
            elif name.endswith("ResultPanel"):
                kinds.add("result_panel")
            elif name.endswith("EntryRow"):
                kinds.add("input_widget")
            elif name.endswith("App") or name.endswith("TkApp"):
                kinds.add("shell")
        elif isinstance(node, ast.FunctionDef):
            if node.name == "resolve_profile_id":
                kinds.add("resolver")
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "REGION_BY_LABEL":
                    kinds.add("resolver")
    return kinds


def check_ui_tk_shell_anti_pattern(source: str, relpath: str) -> List[Finding]:
    """Catch the 116 spike shape: shell + tab + section + resolver +
    result panel all *defined* in one ``ui_tk/`` file.

    Files in ``ui_tk/`` are expected to specialize. Dedicated modules
    (``calculator_app``, ``tabs/*``, ``sections/*``, ``result_panel``,
    ``profile_resolver``, ``input_widgets``) each define exactly one
    responsibility and are not flagged. The rule trips only when 3 or
    more responsibilities are defined in the same file.
    """
    if not relpath.startswith("ui_tk/"):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # banned-imports check already reports syntax errors
    kinds = _responsibility_kinds_defined(tree)
    if len(kinds) >= 3:
        kinds_str = "/".join(sorted(kinds))
        return [
            Finding(
                "error",
                relpath,
                "ui_tk/ file mixes too many responsibilities "
                f"(defines {len(kinds)}: {kinds_str}). Split into "
                "dedicated modules.",
            )
        ]
    return []


def check_soft_limits(
    source: str,
    relpath: str,
    *,
    loc_allowlist: Set[str],
    class_allowlist: Set[str],
) -> List[Finding]:
    findings: List[Finding] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [Finding("error", relpath, f"syntax error: {exc}")]

    loc = _loc(source)
    if loc > LOC_SOFT_LIMIT and relpath not in loc_allowlist:
        findings.append(
            Finding(
                "warning",
                relpath,
                f"file exceeds {LOC_SOFT_LIMIT} LOC soft limit ({loc}). "
                "Consider splitting before adding more responsibilities.",
            )
        )

    class_count = _count_module_classes(tree)
    if class_count > CLASS_SOFT_LIMIT and relpath not in class_allowlist:
        findings.append(
            Finding(
                "warning",
                relpath,
                f"file defines {class_count} top-level classes "
                f"(soft limit {CLASS_SOFT_LIMIT}). Consider splitting "
                "into per-class modules.",
            )
        )

    return findings


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def _iter_py_files(repo_root: Path, root_name: str) -> Iterable[Path]:
    root = repo_root / root_name
    if not root.exists():
        return ()
    return (
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def _iter_app_entrypoints(repo_root: Path) -> Iterable[Path]:
    return (
        p
        for p in repo_root.glob("app_*.py")
        if p.is_file()
    )


def _relpath(path: Path, repo_root: Path) -> str:
    return path.relative_to(repo_root).as_posix()


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def run_checks(repo_root: Path) -> List[Finding]:
    findings: List[Finding] = []

    # 1. core/ banned imports
    for path in _iter_py_files(repo_root, "core"):
        relpath = _relpath(path, repo_root)
        source = path.read_text(encoding="utf-8")
        findings.extend(
            check_banned_imports(source, relpath, "core", BANNED_IMPORTS["core"])
        )

    # 2. ui_tk/ banned imports + shell anti-pattern
    for path in _iter_py_files(repo_root, "ui_tk"):
        relpath = _relpath(path, repo_root)
        source = path.read_text(encoding="utf-8")
        findings.extend(
            check_banned_imports(source, relpath, "ui_tk", BANNED_IMPORTS["ui_tk"])
        )
        findings.extend(check_ui_tk_shell_anti_pattern(source, relpath))

    # 3. app_*.py thin entrypoint
    for path in _iter_app_entrypoints(repo_root):
        relpath = _relpath(path, repo_root)
        source = path.read_text(encoding="utf-8")
        findings.extend(check_app_entrypoint_thin(source, relpath))

    # 4. soft limits on production roots
    seen: Set[str] = set()
    for root_name in PRODUCTION_ROOTS:
        for path in _iter_py_files(repo_root, root_name):
            relpath = _relpath(path, repo_root)
            if relpath in seen:
                continue
            seen.add(relpath)
            source = path.read_text(encoding="utf-8")
            findings.extend(
                check_soft_limits(
                    source,
                    relpath,
                    loc_allowlist=LOC_ALLOWLIST,
                    class_allowlist=CLASS_ALLOWLIST,
                )
            )

    return findings


def _format_report(findings: Sequence[Finding], *, verbose: bool) -> str:
    if not findings:
        return "code structure guard: OK (no findings)\n"

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    lines: List[str] = []
    if errors:
        lines.append(f"errors: {len(errors)}")
        for finding in errors:
            lines.append(f"  [E] {finding.path}: {finding.message}")
    if warnings:
        if errors:
            lines.append("")
        lines.append(f"warnings: {len(warnings)}")
        if verbose or not errors:
            for finding in warnings:
                lines.append(f"  [W] {finding.path}: {finding.message}")
        else:
            lines.append("  (use --verbose to list warnings)")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Project-wide structural guard for predictor_v3. "
            "Checks layer import boundaries, thin app entrypoints, "
            "and soft LOC / class-count limits for new code."
        )
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="also list warnings even when errors are present",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="repository root (defaults to the parent of this script)",
    )
    args = parser.parse_args(argv)

    findings = run_checks(args.repo_root)
    report = _format_report(findings, verbose=args.verbose)
    sys.stdout.write(report)

    has_errors = any(f.severity == "error" for f in findings)
    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
