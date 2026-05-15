import json
import os

from typing import Dict, Optional

from config import config
from ingestion.checksum import (
    compute_file_hash,
    compute_file_size,
)


MANIFEST_FILENAME = ".ingest_manifest.json"
MANIFEST_VERSION = 1


class IngestManifest:
    def __init__(self):
        self.manifest_path = os.path.join(
            config.vector_db_dir,
            MANIFEST_FILENAME,
        )
        self._data: Optional[Dict] = None

    def _ensure_dir(self):
        os.makedirs(
            config.vector_db_dir,
            exist_ok=True,
        )

    def load(self) -> Dict:
        if self._data is not None:
            return self._data

        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                self._data = json.load(f)
        else:
            self._data = {
                "version": MANIFEST_VERSION,
                "files": {},
            }

        return self._data

    def save(self):
        self._ensure_dir()
        with open(self.manifest_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def is_ingested(self, file_rel_path: str) -> bool:
        data = self.load()
        return file_rel_path in data.get("files", {})

    def get_record(self, file_rel_path: str) -> Optional[Dict]:
        data = self.load()
        return data.get("files", {}).get(file_rel_path)

    def is_changed(
        self,
        file_abs_path: str,
        file_rel_path: str,
    ) -> bool:
        data = self.load()
        record = data.get("files", {}).get(file_rel_path)

        if record is None:
            return True

        current_hash = compute_file_hash(file_abs_path)
        current_size = compute_file_size(file_abs_path)

        if record.get("hash") != current_hash:
            return True
        if record.get("size_bytes") != current_size:
            return True

        return False

    def mark_ingested(
        self,
        file_abs_path: str,
        file_rel_path: str,
    ):
        data = self.load()

        if "files" not in data:
            data["files"] = {}

        data["files"][file_rel_path] = {
            "hash": compute_file_hash(file_abs_path),
            "size_bytes": compute_file_size(file_abs_path),
            "ingested_at": self._iso_now(),
        }

        self.save()

    def remove(self, file_rel_path: str):
        data = self.load()
        if "files" in data and file_rel_path in data["files"]:
            del data["files"][file_rel_path]
            self.save()

    def get_all_tracked(self) -> Dict:
        data = self.load()
        return data.get("files", {})

    def _iso_now(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()