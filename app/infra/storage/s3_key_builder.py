import uuid

def build_post_image_key(post_id: int, filename: str) -> str:
    ext = filename.split(".")[-1]
    return f"posts/{post_id}/{uuid.uuid4()}.{ext}"
