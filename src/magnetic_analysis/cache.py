"""
src/magnetic_analysis/cache.py
Persistent disk caching for expensive operations (fieldline traces, ray tracing).
"""

from pathlib import Path
from typing import Optional, Dict, Any, Union
import hashlib
import numpy as np


class Cache:
    """
    Manages persistent caching of NumPy arrays in the project's root `cache/` directory.
    Can be enabled or disabled via flag.
    """

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None, enabled: bool = True):
        self.enabled = enabled
        if cache_dir is None:
            self.cache_dir = Path(__file__).resolve().parent.parent.parent / "cache"
        else:
            self.cache_dir = Path(cache_dir)

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _generate_key(self, prefix: str, **kwargs) -> str:
        key_str = f"{prefix}_" + "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        hash_digest = hashlib.md5(key_str.encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{hash_digest}.npz"

    def has(self, prefix: str, **kwargs) -> bool:
        if not self.enabled:
            return False
        file_path = self.cache_dir / self._generate_key(prefix, **kwargs)
        return file_path.exists()

    def get(self, prefix: str, **kwargs) -> Optional[Dict[str, np.ndarray]]:
        if not self.enabled:
            return None
        file_path = self.cache_dir / self._generate_key(prefix, **kwargs)
        if file_path.exists():
            with np.load(file_path, allow_pickle=True) as data:
                return {k: data[k] for k in data.files}
        return None

    def set(self, prefix: str, data: Dict[str, Any], **kwargs) -> Optional[Path]:
        if not self.enabled:
            return None
        file_path = self.cache_dir / self._generate_key(prefix, **kwargs)
        save_dict = {k: np.asarray(v) for k, v in data.items()}
        np.savez_compressed(file_path, **save_dict)
        return file_path

    def clear(self) -> int:
        if not self.cache_dir.exists():
            return 0
        count = 0
        for f in self.cache_dir.glob("*.npz"):
            f.unlink()
            count += 1
        return count