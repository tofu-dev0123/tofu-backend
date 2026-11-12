def format_extensions(exts: set[str]) -> str:
    return ",".join(f"「.{ext}」" for ext in sorted(exts))
