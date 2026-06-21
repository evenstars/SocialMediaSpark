"""Storage unit tests: sqlite metadata, numpy vectors, local files."""
import tempfile
from pathlib import Path

import numpy as np

from studio.state import Asset, Candidate
from studio.storage.local_files import LocalFileStore
from studio.storage.numpy_vectors import NumpyVectorStore
from studio.storage.sqlite_store import SqliteMetadataStore


def test_sqlite_roundtrip():
    tmp = Path(tempfile.mkdtemp())
    store = SqliteMetadataStore(tmp / "db.sqlite")
    store.save_asset(Asset(id="a1", path="x.png", tags={"lighting": "natural"}))
    store.save_candidate(Candidate(id="c1", path="c.png", source_asset_id="a1", latent=np.ones(4)))
    store.add_to_collection("headshots", "c1")
    assert store.list_collection("headshots") == ["c1"]


def test_numpy_vector_search_and_persist():
    tmp = Path(tempfile.mkdtemp())
    vs = NumpyVectorStore(tmp / "v.npz")
    vs.add("near", np.array([1.0, 0.0, 0.0]))
    vs.add("far", np.array([-1.0, 0.0, 0.0]))
    top = vs.search(np.array([0.9, 0.1, 0.0]), k=1)
    assert top[0][0] == "near"
    vs.save()
    vs2 = NumpyVectorStore(tmp / "v.npz")
    vs2.load()
    assert set(vs2.search(np.array([1.0, 0.0, 0.0]), k=2)) and len(vs2.search(np.zeros(3), k=2)) == 2


def test_local_file_store():
    tmp = Path(tempfile.mkdtemp())
    fs = LocalFileStore(tmp / "files")
    path = fs.put(b"hello", "a.txt")
    assert Path(path).read_bytes() == b"hello"
