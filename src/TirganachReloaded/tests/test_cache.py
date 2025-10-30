"""
Tests for CFF cache functionality
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from TirganachReloaded.cff_editor.data_model import CFFDataModel, CACHE_VERSION


class TestCacheFunctionality:
    """Test cache loading, saving, and fingerprinting"""

    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.cache_dir = self.temp_dir / "cache"
        self.cache_dir.mkdir()

        # Create a mock data model with cache dir
        self.data_model = CFFDataModel.__new__(CFFDataModel)
        self.data_model.cache_dir = self.cache_dir
        self.data_model.project_root = self.temp_dir

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_fingerprint_generation(self):
        """Test that fingerprints are generated consistently"""
        # Create a test file
        test_file = self.temp_dir / "test.cff"
        test_content = b"test content for fingerprinting"
        test_file.write_bytes(test_content)

        # Generate fingerprint
        fp1 = self.data_model._generate_fingerprint(str(test_file))
        fp2 = self.data_model._generate_fingerprint(str(test_file))

        # Should be identical for same file
        assert fp1 == fp2
        assert len(fp1) == 64  # SHA-256 hex length

        # Modify file - fingerprint should change
        test_file.write_bytes(b"modified content")
        fp3 = self.data_model._generate_fingerprint(str(test_file))
        assert fp3 != fp1

    def test_cache_paths(self):
        """Test cache file path generation"""
        fingerprint = "abcd1234" * 8  # 64 char hex string
        cache_file, meta_file = self.data_model._get_cache_paths(fingerprint)

        assert cache_file.name == f"GameData_{fingerprint}.pkl"
        assert meta_file.name == f"GameData_{fingerprint}.meta.json"
        assert cache_file.parent == self.cache_dir
        assert meta_file.parent == self.cache_dir

    def test_cache_save_load(self):
        """Test saving and loading from cache"""
        # Create mock GameData-like object
        class MockGameData:
            def __init__(self, data):
                self.data = data

        mock_data = MockGameData({"test": "data"})
        fingerprint = "test_fingerprint_" + "a" * 32

        # Save to cache
        self.data_model._save_to_cache(mock_data, fingerprint, "/fake/path.cff")

        # Verify files exist
        cache_file, meta_file = self.data_model._get_cache_paths(fingerprint)
        assert cache_file.exists()
        assert meta_file.exists()

        # Load from cache
        loaded_data = self.data_model._load_from_cache(fingerprint)
        assert loaded_data is not None
        assert loaded_data.data == mock_data.data

    def test_cache_invalidation_version(self):
        """Test cache invalidation on version change"""
        # Create mock GameData
        class MockGameData:
            def __init__(self, data):
                self.data = data

        mock_data = MockGameData({"test": "data"})
        fingerprint = "test_fingerprint_" + "b" * 32

        # Save with current version
        self.data_model._save_to_cache(mock_data, fingerprint, "/fake/path.cff")

        # Load should work
        loaded_data = self.data_model._load_from_cache(fingerprint)
        assert loaded_data is not None

        # Modify metadata to have wrong version
        cache_file, meta_file = self.data_model._get_cache_paths(fingerprint)
        import json
        with open(meta_file, 'r') as f:
            meta = json.load(f)
        meta['cache_version'] = "wrong.version"
        with open(meta_file, 'w') as f:
            json.dump(meta, f)

        # Load should fail due to version mismatch
        loaded_data = self.data_model._load_from_cache(fingerprint)
        assert loaded_data is None

    def test_nonexistent_file_fingerprint(self):
        """Test fingerprint generation for nonexistent file"""
        with pytest.raises(FileNotFoundError):
            self.data_model._generate_fingerprint("/nonexistent/file.cff")


if __name__ == "__main__":
    pytest.main([__file__])