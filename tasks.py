import json
from pathlib import Path

from dotenv import dotenv_values
from invoke import Collection, Failure, task

REMOTE_BRANCHES = ["main"]

with Path("project.d/cc-ctx.json").open() as fd_in:
    CC_CTX = json.load(fd_in)
    CFG = {
        **dotenv_values("../.config/env.global"),
        **dotenv_values(f"../.config/{CC_CTX['scm_slug']}/env.project"),
    }

    CFG = CFG | CC_CTX
    CFG["pkg_idx_url"] = CFG["PYPI_URL"]
    CFG["pkg_idx_user"] = CFG["PYPI_USER"]
    CFG["pkg_idx_passwd"] = CFG["PYPI_PASSWD"]

    if CFG.get("enable_gitflow", False):
        REMOTE_BRANCHES.extend(["develop"])


@task
def bumpversion(ctx, part):
    """Bump the version number, by major, minor or patch/hotfix"""
    part = "patch" if part == "hotfix" else part

    ctx.run(f"bump-my-version bump {part}")
    ctx.run(f"uv lock --upgrade-package {CFG['scm_slug']}")


@task
def clean(ctx):
    """Delete build, dist, cache and other generated files."""
    patterns = [
        "build/",
        "dist/",
        ".mypy_cache/",
        ".pytest_cache/",
        ".ruff_cache/",
    ]

    for pattern in patterns:
        ctx.run(f"rm -rf {pattern}")

    ctx.run("find . -name '__pycache__' -exec rm -rf {} +")


@task
def init(ctx):
    """Initialize git repository. Run this task after cloning the repository."""
    if not Path(".gitignore").exists():
        raise Failure(".gitignore file not found")

    is_new = False
    if not Path(".git").exists():
        is_new = True
        ctx.run("git init")
        ctx.run(f"git remote add origin {CFG['scm_repo_url']}")
        ctx.run("git add .")
        ctx.run('git commit -m "Initial commit from jjstout/cc-py-pkg template"')

    if CFG.get("enable_gitflow", False):
        ctx.run("git flow init -d")
    
    if is_new:
        for branch in REMOTE_BRANCHES:
            ctx.run(f"git push -u origin {branch}")


@task
def lint(ctx):
    """Run code style and quality checks."""
    ctx.run("ruff format src/")
    ctx.run("ruff check --fix src/")
    ctx.run("pydocstyle src/")


@task
def push(ctx):
    """Push all remote branches and tags to the remote repository."""
    for branch in REMOTE_BRANCHES:
        ctx.run(f"git push origin {branch}")

    ctx.run("git push --tags")


@task
def test(ctx):
    """Run the project tests."""
    ctx.run("ty check src/")
    ctx.run("pytest tests/")
    

@task(clean)
def build(ctx):
    """Build the project."""
    ctx.run("uv build")


@task(build)
def release(ctx):
    """Release the project."""
    if CFG.get("enable_publish", False):
        ctx.run(
            f"""uv run twine upload --repository-url {CFG['pkg_idx_url']} \
                                    --username {CFG['pkg_idx_user']} \
                                    --password {CFG['pkg_idx_passwd']} \
                                    dist/*"""
        )


ns = Collection(build, bumpversion, clean, init, lint, push, release, test)
