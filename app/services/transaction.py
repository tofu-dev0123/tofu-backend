from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def transaction(db: Session) -> Iterator[None]:
    """ブロックが正常終了したら commit し、例外発生時は rollback して再送出する"""
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise
