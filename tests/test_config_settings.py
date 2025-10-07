def test_config_settings_exports():
    from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP

    assert isinstance(CHUNK_SIZE, int)
    assert isinstance(CHUNK_OVERLAP, int)

