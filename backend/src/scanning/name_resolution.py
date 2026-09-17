from pathlib import Path


def resolve_name(explicit_name: str | None, manifest_path: Path, existing_names: set[str]) -> str:
    """FR-004 name derivation: explicit manifest field > parent directory name >
    repository-path-derived suffix on collision. Does not mutate `existing_names` —
    the caller adds the returned name once it commits to using it.
    """
    # A manifest's name field is free-form user/tool-authored JSON (or XML)
    # content -- a non-string value (number, object, array) would otherwise
    # flow straight into a SQLite String column and fail at insert time.
    if not isinstance(explicit_name, str):
        explicit_name = None
    base_name = explicit_name or manifest_path.parent.name

    if base_name not in existing_names:
        return base_name

    grandparent = manifest_path.parent.parent
    suffix_source = grandparent.name if grandparent.name else manifest_path.parent.name

    candidate = f"{base_name}-{suffix_source}"
    counter = 2
    while candidate in existing_names:
        candidate = f"{base_name}-{suffix_source}-{counter}"
        counter += 1
    return candidate
