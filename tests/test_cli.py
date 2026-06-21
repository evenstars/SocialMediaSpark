"""CLI end-to-end: --demo path runs the pipeline and reports outputs."""
import tempfile
from pathlib import Path

import cli


def test_demo_run_produces_report():
    tmp = Path(tempfile.mkdtemp())
    base = cli.synth_sample_images(tmp / "base", n=3)
    state = cli.run("professional headshot", "me", base, data_dir=tmp, n_candidates=4)

    # gate enforced: some approved, the drifted one rejected, all approved credentialed
    assert len(state["approved"]) >= 1
    assert len(state["rejected"]) >= 1
    assert all(c.credentials for c in state["approved"])

    report = cli.format_report(state)
    assert "approved outputs" in report
    assert "rejected" in report
    assert "credentials: C2PA" in report


def test_demo_synth_creates_files():
    tmp = Path(tempfile.mkdtemp())
    base = cli.synth_sample_images(tmp / "base", n=3)
    assert len(base) == 3
    assert all(Path(p).exists() for p in base)


def test_list_images_reads_folder():
    tmp = Path(tempfile.mkdtemp())
    folder = tmp / "photos"
    cli.synth_sample_images(folder, n=2)          # creates sample_*.png
    (folder / "notes.txt").write_text("ignore me")  # non-image should be skipped
    found = cli.list_images(folder)
    assert len(found) == 2
    assert all(p.endswith(".png") for p in found)
