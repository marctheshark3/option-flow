"""Check package portability and executable evaluation controls using stdlib."""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "skills" / "option-flow"


def check_package(package=PACKAGE) -> None:
    entry = (package / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", entry, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    fields = dict(line.split(":", 1) for line in match[1].splitlines())
    if fields.get("name", "").strip() != package.name:
        raise ValueError("Skill name must match its package directory")
    if not fields.get("description", "").strip():
        raise ValueError("Skill description is missing")
    if (package / "LICENSE").read_bytes() != (ROOT / "LICENSE").read_bytes():
        raise ValueError("Installed package license differs from repository license")
    for path in package.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Skill package contains a symbolic link: {path}")
    for document in [ROOT / "README.md", *package.rglob("*.md")]:
        for destination in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", destination):
                continue
            relative = destination.split("#", 1)[0]
            if not relative:
                continue
            resolved = (document.parent / relative).resolve()
            boundary = package if document.is_relative_to(package) else ROOT
            if not resolved.is_relative_to(boundary) or not resolved.exists():
                raise ValueError(f"Missing or external local reference in {document.name}: {destination}")


def main() -> None:
    for package in sorted((ROOT / "skills").iterdir()):
        if (package / "SKILL.md").is_file():
            check_package(package)
    subprocess.run([sys.executable, str(ROOT / "evals" / "evaluator" / "selftest.py")],
                   cwd=ROOT, check=True)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "evals", "-p", "test_tool_flow.py", "-v"], cwd=ROOT, check=True)
    print("Package references, license, and fixture controls passed.")


if __name__ == "__main__":
    main()
