"""Project-wide structural guard for new code (Issue 119).

Conservative first version. Designed to be run from the repo root:

    python3 -B tools/check_code_structure.py [--verbose]

Checks:

1. ``core/`` files must not import ``ui``, ``apps.calculator.ui``, ``PyQt5``, or
   ``tkinter`` (calculator core stays pure-Python / framework-free).
2. ``apps/calculator/ui/`` files must not import ``PyQt5`` or the PyQt ``ui``
   package (Tkinter shell is independent of PyQt).
3. ``app_*.py`` entrypoints at repo root must be thin: no class
   definitions, ≤ 3 module-level ``def``\\s, ≤ 80 LOC.
4. ``apps/calculator/ui/`` lightweight shell anti-pattern: a single file must not
   bundle shell + tab + section + resolver + result-panel
   responsibilities (the 116 spike shape).
5. Soft LOC / class-count limits per production file
   (``core/``, ``ui/``, ``apps/``, ``scripts/``). Known-large
   historical files are allowlisted (see ``LOC_ALLOWLIST`` /
   ``CLASS_ALLOWLIST``).
6. ``apps/calculator/ui/`` visual values are defined in configured owner modules,
   not redeclared as raw colors or local visual constants in components.

The script reads Python source files only — no PyQt / Tkinter
imports, no Excel / numpy / pandas. External dependency: none.

Exit code is non-zero when any check reports a violation. Soft-limit
findings are reported as warnings and do NOT fail the run.
"""

from __future__ import annotations

import argparse
import ast
import re
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
    "core": ("ui", "PyQt5", "tkinter", "apps.calculator.ui"),
    "apps.calculator.ui": ("PyQt5", "ui"),
}

# LOC soft limit (warning, not failure) for production source files.
LOC_SOFT_LIMIT = 400

# Class-count soft limit (warning) per file.
CLASS_SOFT_LIMIT = 5

# Files exempt from LOC soft limit. Paths are relative to repo root.
LOC_ALLOWLIST: Set[str] = {
    "core/calculator_iso16358.py",
    "core/calculator_ks_c9306.py",
    "core/calculator_ahri_hspf2.py",
    "core/calculator_en14825.py",
    "core/calculator_asnzs_hspf_excel.py",
    "ui/spreadsheet_table.py",
    "apps/calculator/ui/metric_input_table.py",
    "apps/calculator/ui/sections/iso_saso_t3_section.py",
    "apps/calculator/ui/sections/bin_detail_panel.py",
    "apps/calculator/ui/batch/matrix_table.py",
    "apps/calculator/ui/batch_dialogs/profiles/saso_t3.py",
}

# Files exempt from class-count soft limit.
CLASS_ALLOWLIST: Set[str] = {
    "ui/spreadsheet_table.py",
    "apps/calculator/ui/batch_dialogs/profiles/saso_t3.py",
    "apps/calculator/ui/batch_dialogs/profiles/iso_iseer_2point.py",
}

# Thin app entrypoint limits.
APP_ENTRYPOINT_MAX_LOC = 80
APP_ENTRYPOINT_MAX_FUNCS = 3

# Roots that get LOC / class-count soft-limit reporting.
PRODUCTION_ROOTS: Tuple[str, ...] = ("core", "ui", "apps", "scripts")

# Tkinter visual values belong to explicit owner modules. This is a path-based
# boundary so other toolkit adapters or projects can configure the same check.
UI_VISUAL_SCAN_ROOTS: Tuple[str, ...] = ("apps/calculator/ui",)
UI_VISUAL_OWNER_PATHS: Set[str] = {
    "apps/calculator/ui/layout_constants.py",
    "ui_common/visual_tokens.py",
}
UI_VISUAL_ALLOWLIST_PATHS: Set[str] = set()
PROFILE_TAB_LIFECYCLE_FORBIDDEN_CALLS: Set[str] = {
    "DynamicContentRefitScheduler",
    "TkContentHuggingShell",
    "TkVisibleContentMeasurement",
    "register_content",
}
RAW_HEX_COLOR_PATTERN = re.compile(
    r"^#[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3})?(?:[0-9A-Fa-f]{2})?$"
)
LOCAL_VISUAL_CONSTANT_PATTERN = re.compile(
    r"(?:_BG|_FG|_COLOR|_FONT|_PAD[A-Z_]*|_WIDTH|_HEIGHT)$"
)
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


def _imported_modules(tree: ast.AST) -> Set[str]:
    """Collect module names referenced by ``import`` /
    ``from`` statements in ``tree``."""
    modules: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import — skip, not subject to ban list
                continue
            if node.module:
                modules.add(node.module)
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
        for banned in banned_roots:
            if module == banned or module.startswith(banned + "."):
                findings.append(
                    Finding(
                        "error",
                        relpath,
                        f"{layer}/ layer must not import '{banned}'",
                    )
                )
                break
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


def check_apps_calculator_ui_shell_anti_pattern(source: str, relpath: str) -> List[Finding]:
    """Catch the 116 spike shape: shell + tab + section + resolver +
    result panel all *defined* in one ``apps/calculator/ui/`` file.

    Files in ``apps/calculator/ui/`` are expected to specialize. Dedicated modules
    (``calculator_app``, ``tabs/*``, ``sections/*``, ``result_panel``,
    ``profile_resolver``, ``input_widgets``) each define exactly one
    responsibility and are not flagged. The rule trips only when 3 or
    more responsibilities are defined in the same file.
    """
    if not relpath.startswith("apps/calculator/ui/"):
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
                "apps/calculator/ui/ file mixes too many responsibilities "
                f"(defines {len(kinds)}: {kinds_str}). Split into "
                "dedicated modules.",
            )
        ]
    return []


def check_ui_visual_value_ownership(
    source: str,
    relpath: str,
    *,
    scan_roots: Sequence[str],
    owner_paths: Set[str],
    allowlist_paths: Set[str],
) -> List[Finding]:
    """Require component visual values to be consumed from an owner module."""
    if not any(relpath.startswith(f"{root}/") for root in scan_roots):
        return []
    if relpath in owner_paths or relpath in allowlist_paths:
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []  # banned-imports check already reports syntax errors

    findings: List[Finding] = []
    if any(
        isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and RAW_HEX_COLOR_PATTERN.fullmatch(node.value)
        for node in ast.walk(tree)
    ):
        findings.append(
            Finding(
                "error",
                relpath,
                "UI visual values must be defined in an owner module: "
                "raw hex color literal found",
            )
        )

    for node in tree.body:
        targets: Sequence[ast.expr] = ()
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        for target in targets:
            if (
                isinstance(target, ast.Name)
                and LOCAL_VISUAL_CONSTANT_PATTERN.search(target.id)
            ):
                findings.append(
                    Finding(
                        "error",
                        relpath,
                        "UI visual values must be defined in an owner module: "
                        f"local visual constant '{target.id}' found",
                    )
                )
    return findings


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


def check_ui_root_flat_feature_file(relpath: str) -> List[Finding]:
    """Ensure feature-specific files are not added directly to apps/calculator/ui root."""
    findings: List[Finding] = []
    path_parts = relpath.split("/")
    if len(path_parts) == 4 and path_parts[0:3] == ["apps", "calculator", "ui"]:
        filename = path_parts[3]
        # Feature-specific prefixes that must not be flat in root
        banned_prefixes = ("en14825_", "ahri_", "seer2_", "hspf2_", "saso_", "ks_c9306_")
        for prefix in banned_prefixes:
            if filename.startswith(prefix):
                findings.append(
                    Finding(
                        severity="error",
                        path=relpath,
                        message=(
                            f"Feature-specific flat file '{filename}' is not allowed in apps/calculator/ui root. "
                            "Use a feature package directory."
                        ),
                    )
                )
    return findings


def check_sections_flat_model_adapter_table(relpath: str) -> List[Finding]:
    """Ensure feature-specific model/adapter/table files are not placed inside sections/."""
    findings: List[Finding] = []
    path_parts = relpath.split("/")
    if len(path_parts) >= 5 and path_parts[0:4] == ["apps", "calculator", "ui", "sections"]:
        filename = path_parts[-1]
        banned_suffixes = (
            "_adapter.py",
            "_adapters.py",
            "_model.py",
            "_models.py",
            "_table_model.py",
            "_table_models.py",
        )
        for suffix in banned_suffixes:
            if filename.endswith(suffix):
                findings.append(
                    Finding(
                        severity="error",
                        path=relpath,
                        message=(
                            f"Sections folder is for UI glue/routing only. File '{filename}' "
                            "violates clean architecture boundary."
                        ),
                    )
                )
    return findings


def check_core_root_flat_helper_misc_utils(relpath: str) -> List[Finding]:
    """Warn when new helper/misc/utils flat files are added directly under core root."""
    findings: List[Finding] = []
    path_parts = relpath.split("/")
    if len(path_parts) == 2 and path_parts[0] == "core":
        filename = path_parts[1]
        banned_suffixes = (
            "_helper.py",
            "_helpers.py",
            "_misc.py",
            "_utils.py",
        )
        for suffix in banned_suffixes:
            if filename.endswith(suffix):
                findings.append(
                    Finding(
                        severity="warning",
                        path=relpath,
                        message=(
                            f"Avoid adding new flat helper/misc/utils files like '{filename}' directly in core root. "
                            "Place them inside standard/domain packages."
                        ),
                    )
                )
    return findings


def check_tests_mega_test_naming(relpath: str) -> List[Finding]:
    """Warn when generic mega-test files are added under tests/."""
    findings: List[Finding] = []
    path_parts = relpath.split("/")
    if len(path_parts) >= 2 and path_parts[0] == "tests":
        filename = path_parts[-1]
        if filename.startswith("test_") and (filename.endswith("_everything.py") or filename.endswith("_all.py")):
            findings.append(
                Finding(
                    severity="warning",
                    path=relpath,
                    message=(
                        f"Avoid using generic mega-test names like '{filename}'. "
                        "Use focused test files mapping to source packages."
                    ),
                )
            )
    return findings


def check_ui_package_registry(relpath: str) -> List[Finding]:
    """Warn if a new subdirectory is added under apps/calculator/ui without being registered."""
    findings: List[Finding] = []
    path_parts = relpath.split("/")
    if len(path_parts) >= 5 and path_parts[0:3] == ["apps", "calculator", "ui"]:
        subdir = path_parts[3]
        allowed_packages = {
            "ahri",
            "ahri_m",
            "batch",
            "batch_dialogs",
            "brazil_cspf",
            "en14825",
            "lifecycle",
            "sections",
            "table",
            "tabs",
        }
        if subdir not in allowed_packages:
            findings.append(
                Finding(
                    severity="warning",
                    path=relpath,
                    message=(
                        f"Directory '{subdir}' is not in the allowed package registry under apps/calculator/ui. "
                        "Consider registering it if it is a new feature package."
                    ),
                )
            )
    return findings


def check_profile_tab_lifecycle_owner(source: str, relpath: str) -> List[Finding]:
    """Reject direct lifecycle primitive assembly in production profile tabs."""

    path_parts = relpath.split("/")
    if path_parts[:4] != ["apps", "calculator", "ui", "tabs"]:
        return []
    if len(path_parts) != 5 or not path_parts[-1].endswith(".py"):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    findings: List[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
        else:
            continue
        if call_name not in PROFILE_TAB_LIFECYCLE_FORBIDDEN_CALLS:
            continue
        findings.append(
            Finding(
                severity="error",
                path=relpath,
                message=(
                    f"Profile tab must not call {call_name} directly; "
                    "delegate visible-content lifecycle assembly to "
                    "ProfileVisibleContentLifecycleController."
                ),
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

    # 1. core/ banned imports + flat helper/misc/utils checks
    for path in _iter_py_files(repo_root, "core"):
        relpath = _relpath(path, repo_root)
        source = path.read_text(encoding="utf-8")
        findings.extend(
            check_banned_imports(source, relpath, "core", BANNED_IMPORTS["core"])
        )
        findings.extend(check_core_root_flat_helper_misc_utils(relpath))

    # 2. apps/calculator/ui/ banned imports + shell anti-pattern + visual-value ownership + boundary checks
    for path in _iter_py_files(repo_root, "apps/calculator/ui"):
        relpath = _relpath(path, repo_root)
        source = path.read_text(encoding="utf-8")
        findings.extend(
            check_banned_imports(source, relpath, "apps.calculator.ui", BANNED_IMPORTS["apps.calculator.ui"])
        )
        findings.extend(check_apps_calculator_ui_shell_anti_pattern(source, relpath))
        findings.extend(
            check_ui_visual_value_ownership(
                source,
                relpath,
                scan_roots=UI_VISUAL_SCAN_ROOTS,
                owner_paths=UI_VISUAL_OWNER_PATHS,
                allowlist_paths=UI_VISUAL_ALLOWLIST_PATHS,
            )
        )
        findings.extend(check_ui_root_flat_feature_file(relpath))
        findings.extend(check_sections_flat_model_adapter_table(relpath))
        findings.extend(check_ui_package_registry(relpath))
        findings.extend(check_profile_tab_lifecycle_owner(source, relpath))

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

    # 5. tests/ naming checks
    for path in _iter_py_files(repo_root, "tests"):
        relpath = _relpath(path, repo_root)
        findings.extend(check_tests_mega_test_naming(relpath))

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
            "UI visual-value ownership, and soft LOC / class-count limits "
            "for new code."
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
