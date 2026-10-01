from functools import lru_cache

from data_assistant.data.catalog import Catalog
from data_assistant.data.postgres import load_catalog

from data_assistant.data.semantic import (
    apply_semantic_metadata,
    load_semantic_metadata
)

@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    catalog = load_catalog()
    metadata = load_semantic_metadata()

    return apply_semantic_metadata(
        catalog,
        metadata,
    )

def refresh_catalog() -> Catalog:
    get_catalog.cache_clear()
    return get_catalog()