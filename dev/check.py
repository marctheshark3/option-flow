"""Check package portability and executable evaluation controls using stdlib."""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "skills" / "option-flow"


def check_package() -> None:
    entry = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", entry, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")
    fields = dict(line.split(":", 1) for line in match[1].splitlines())
    if fields.get("name", "").strip() != PACKAGE.name:
        raise ValueError("Skill name must match its package directory")
    if not fields.get("description", "").strip():
        raise ValueError("Skill description is missing")
    if (PACKAGE / "LICENSE").read_bytes() != (ROOT / "LICENSE").read_bytes():
        raise ValueError("Installed package license differs from repository license")
    for path in PACKAGE.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Skill package contains a symbolic link: {path}")
    for document in [ROOT / "README.md", *PACKAGE.rglob("*.md")]:
        for destination in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", destination):
                continue
            relative = destination.split("#", 1)[0]
            if not relative:
                continue
            resolved = (document.parent / relative).resolve()
            boundary = PACKAGE if document.is_relative_to(PACKAGE) else ROOT
            if not resolved.is_relative_to(boundary) or not resolved.exists():
                raise ValueError(f"Missing or external local reference in {document.name}: {destination}")


def main() -> None:
    check_package()
    subprocess.run([sys.executable, str(ROOT / "evals" / "evaluator" / "selftest.py")],
                   cwd=ROOT, check=True)
    print("Package references, license, and fixture controls passed.")


if __name__ == "__main__":
    main()
