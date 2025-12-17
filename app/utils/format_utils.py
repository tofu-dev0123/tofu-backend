def extension_formatter(exts: set[str]) -> str:
    return ",".join(f"「.{ext}」" for ext in sorted(exts))
