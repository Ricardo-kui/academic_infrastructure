"""
ForwardIndex — persistent embedding storage with Windows-compatible locking.

Replaces Unix-only fcntl with filelock (preferred) or atomic rename fallback.
"""

import json
import os
import pickle
import shutil
from pathlib import Path
from typing import Optional

import numpy as np

from .models import Chunk


class ForwardIndex:
    """Persistent store for chunk embeddings with mmap-friendly reads."""

    def __init__(self, index_dir: Path):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_path = self.index_dir / "embeddings.npy"
        self.chunks_path = self.index_dir / "chunks.pkl"
        self.manifest_path = self.index_dir / "manifest.json"

        self._embeddings: Optional[np.ndarray] = None
        self._chunks: list[Chunk] = []
        self._manifest: dict[str, dict] = {}
        self._load()

    def _load(self) -> None:
        if self.embeddings_path.exists():
            self._embeddings = np.load(
                str(self.embeddings_path), mmap_mode="r"
            )
        else:
            self._embeddings = np.zeros((0, 0), dtype=np.float32)

        if self.chunks_path.exists():
            with open(self.chunks_path, "rb") as f:
                self._chunks = pickle.load(f)
        else:
            self._chunks = []

        if self.manifest_path.exists():
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                self._manifest = json.load(f)
        else:
            self._manifest = {}

    def _save(self) -> None:
        """Atomic save: write to temp then rename."""
        # Save embeddings
        tmp_emb = self.embeddings_path.with_suffix(".npy.tmp")
        np.save(str(tmp_emb), self._embeddings)
        tmp_emb.replace(self.embeddings_path)

        # Save chunks
        tmp_pkl = self.chunks_path.with_suffix(".pkl.tmp")
        with open(tmp_pkl, "wb") as f:
            pickle.dump(self._chunks, f)
        tmp_pkl.replace(self.chunks_path)

        # Save manifest
        tmp_json = self.manifest_path.with_suffix(".json.tmp")
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(self._manifest, f, ensure_ascii=False, indent=2)
        tmp_json.replace(self.manifest_path)

    def _acquire_lock(self) -> Optional[object]:
        """Try to use filelock; fall back to None (atomic rename is enough for single-process)."""
        try:
            from filelock import FileLock
            lock_path = self.index_dir / ".index.lock"
            lock = FileLock(str(lock_path))
            lock.acquire()
            return lock
        except Exception:
            return None

    def _release_lock(self, lock: Optional[object]) -> None:
        if lock is not None:
            try:
                lock.release()
            except Exception:
                pass

    def update_file(
        self, file_path: str, chunks: list[Chunk], embeddings: list[np.ndarray]
    ) -> None:
        """Update or add chunks for a single file."""
        lock = self._acquire_lock()
        try:
            self._load()  # Refresh in case another process wrote

            old_indices = self._manifest.get(file_path, {}).get("indices", [])
            if old_indices:
                # Remove old chunks and embeddings
                mask = np.ones(len(self._chunks), dtype=bool)
                mask[old_indices] = False
                self._chunks = [c for c, m in zip(self._chunks, mask) if m]
                self._embeddings = self._embeddings[mask]

                # Remap manifest indices
                old_to_new = {}
                new_idx = 0
                for i, m in enumerate(mask):
                    if m:
                        old_to_new[i] = new_idx
                        new_idx += 1
                for fp, info in list(self._manifest.items()):
                    info["indices"] = [
                        old_to_new[idx]
                        for idx in info["indices"]
                        if idx in old_to_new
                    ]

            # Append new chunks
            start_idx = len(self._chunks)
            self._chunks.extend(chunks)
            new_emb = np.stack(embeddings) if embeddings else np.zeros((0, 0), dtype=np.float32)
            if self._embeddings.size == 0:
                self._embeddings = new_emb
            else:
                self._embeddings = np.vstack([self._embeddings, new_emb])

            end_idx = len(self._chunks)
            self._manifest[file_path] = {
                "mtime": os.path.getmtime(file_path),
                "indices": list(range(start_idx, end_idx)),
            }

            self._save()
        finally:
            self._release_lock(lock)

    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> list[tuple[float, Chunk]]:
        """Cosine similarity search."""
        if self._embeddings.size == 0 or len(self._chunks) == 0:
            return []

        # Normalize
        emb = self._embeddings
        q = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        norms = np.linalg.norm(emb, axis=1) + 1e-10
        sims = emb @ q / norms

        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(float(sims[i]), self._chunks[i]) for i in top_idx]

    def get_manifest(self) -> dict:
        return dict(self._manifest)
