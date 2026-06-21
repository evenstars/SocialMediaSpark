"""SQLite implementation of MetadataStore (v1).

Stores assets, candidates, and collection membership. JSON columns hold the
flexible bits (tags, scores, credentials).
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from studio.state import Asset, Candidate
from studio.storage.interfaces import MetadataStore


class SqliteMetadataStore(MetadataStore):
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.init_schema()

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                tags TEXT
            );
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                source_asset_id TEXT,
                status TEXT,
                scores TEXT,
                credentials TEXT
            );
            CREATE TABLE IF NOT EXISTS collection_items (
                collection TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                PRIMARY KEY (collection, candidate_id)
            );
            """
        )
        self.conn.commit()

    def save_asset(self, asset: Asset) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO assets (id, path, tags) VALUES (?, ?, ?)",
            (asset.id, asset.path, json.dumps(asset.tags, ensure_ascii=False)),
        )
        self.conn.commit()

    def save_candidate(self, candidate: Candidate) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO candidates "
            "(id, path, source_asset_id, status, scores, credentials) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                candidate.id,
                candidate.path,
                candidate.source_asset_id,
                candidate.status,
                json.dumps(candidate.scores),
                json.dumps(candidate.credentials),
            ),
        )
        self.conn.commit()

    def add_to_collection(self, collection: str, candidate_id: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO collection_items (collection, candidate_id) VALUES (?, ?)",
            (collection, candidate_id),
        )
        self.conn.commit()

    def list_collection(self, collection: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT candidate_id FROM collection_items WHERE collection = ?",
            (collection,),
        ).fetchall()
        return [r["candidate_id"] for r in rows]
