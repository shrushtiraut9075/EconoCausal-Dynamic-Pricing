"""Unit tests for file-based model registry."""

import json
import tempfile
from pathlib import Path

import pandas as pd

from econocausal.registry.store import ModelRegistry


def test_model_registry_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        reg = ModelRegistry(base_dir=Path(tmpdir))
        model_id = "test_model_1"

        # Save metadata
        m_dir = Path(tmpdir) / model_id
        m_dir.mkdir(parents=True, exist_ok=True)
        (m_dir / "meta.json").write_text(json.dumps({"model_id": model_id, "score": 0.95}))

        models = reg.list_models()
        assert model_id in models

        meta = reg.get_metadata(model_id)
        assert meta is not None
        assert meta["score"] == 0.95

        # Save reference stats
        df = pd.DataFrame(
            {
                "age": [20, 30, 40],
                "tier": ["gold", "silver", "bronze"],
            }
        )
        reg.save_reference_stats(model_id, df)
        ref_file = m_dir / "reference_stats.json"
        assert ref_file.exists()
        ref_data = json.loads(ref_file.read_text())
        assert "numeric" in ref_data
        assert "categorical" in ref_data
