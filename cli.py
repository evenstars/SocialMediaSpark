"""End-to-end demo entry point.

Usage:
    python cli.py --demo                       # synthesize sample photos and run
    python cli.py --base a.jpg b.jpg --request "professional headshot, dark background"
    python cli.py --base-dir ./my_photos       # read every image in a folder

Note: v1 outputs are stub placeholder images; real generation arrives in M5.
"""
from __future__ import annotations

import argparse
from pathlib import Path

# Image file types accepted by --base-dir
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}

from PIL import Image

import config
from studio import guardrails
from studio.deps import default_deps
from studio.graph import build_graph, new_job


def synth_sample_images(dir_path: Path, n: int = 3) -> list[str]:
    """Create n distinct sample photos so --demo needs no input files."""
    dir_path.mkdir(parents=True, exist_ok=True)
    paths = []
    for i in range(n):
        p = dir_path / f"sample_{i}.png"
        Image.new("RGB", (256, 256), (50 + i * 40, 90, 140)).save(p)
        paths.append(str(p))
    return paths


def list_images(dir_path: str | Path) -> list[str]:
    """Return all image paths in a folder (sorted), filtered by extension."""
    d = Path(dir_path)
    if not d.is_dir():
        raise SystemExit(f"not a directory: {dir_path}")
    paths = sorted(str(p) for p in d.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not paths:
        raise SystemExit(f"no images found in {dir_path}")
    return paths


def run(request: str, person_id: str, base_paths: list[str], data_dir: Path,
        n_candidates: int = 4, collection: str = "default") -> dict:
    """Wire deps for data_dir, run the pipeline, return the final state."""
    deps = default_deps(data_dir)
    app = build_graph(deps)
    job = new_job(request, person_id, base_paths)
    job["n_candidates"] = n_candidates
    job["collection"] = collection
    return app.invoke(job)


def format_report(state: dict) -> str:
    """Turn the final state into a human-readable report."""
    lines = []
    lines.append("=== SocialMediaSpark — run report ===")
    lines.append(f"request : {state.get('request')}")
    lines.append(f"person  : {state.get('person_id')}")
    lines.append(f"ingested: {len(state.get('assets', []))} base photo(s)")

    approved = state.get("approved", [])
    rejected = state.get("rejected", [])
    lines.append(f"result  : {len(approved)} approved, {len(rejected)} rejected")

    if rejected:
        lines.append("\nrejected:")
        for c in rejected:
            lines.append(f"  - {c.id}  reason: {c.reject_reason}")

    if approved:
        lines.append("\napproved outputs:")
        for c in approved:
            s = c.scores
            lines.append(
                f"  - {c.id}  id={s.get('identity', 0):.2f} "
                f"nat={s.get('naturalness', 0):.2f} aes={s.get('aesthetic', 0):.2f} "
                f"combined={guardrails.combined_score(c):.2f}"
            )
            lines.append(f"        file: {c.path}")
            cred = c.credentials or {}
            lines.append(f"        credentials: {cred.get('standard', 'NONE')} — {cred.get('claim', '')}")

    lines.append(f"\nexported -> collection '{state.get('collection')}': {len(state.get('exported', []))} file(s)")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="SocialMediaSpark pipeline demo")
    parser.add_argument("--demo", action="store_true", help="synthesize sample photos and run")
    parser.add_argument("--base", nargs="+", default=None, help="real source photo paths")
    parser.add_argument("--base-dir", default=None, help="folder of source photos (reads all images)")
    parser.add_argument("--request", default="professional headshot, dark background")
    parser.add_argument("--person", default="me", help="identity key")
    parser.add_argument("--collection", default="default")
    parser.add_argument("--n", type=int, default=4, help="number of candidates to generate")
    parser.add_argument("--data-dir", default=str(config.DATA_DIR), help="where outputs/db live")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if args.demo:
        base_paths = synth_sample_images(data_dir / "base", n=3)
    elif args.base:
        base_paths = args.base
    elif args.base_dir:
        base_paths = list_images(args.base_dir)
    else:
        parser.error("provide --demo, --base <paths>, or --base-dir <folder>")

    state = run(
        request=args.request,
        person_id=args.person,
        base_paths=base_paths,
        data_dir=data_dir,
        n_candidates=args.n,
        collection=args.collection,
    )
    print(format_report(state))


if __name__ == "__main__":
    main()
