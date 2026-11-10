from app.models.timeline import Timeline
from app.repositories.timeline_repository import TimelineRepository


def _timeline(year: int, sort_order: int, title: str = "title") -> Timeline:
    return Timeline(year=year, title=title, body=None, sort_order=sort_order)


def test_create_and_exists_by_id(db):
    repo = TimelineRepository(db)

    timeline_id = repo.create(_timeline(2024, 0))

    assert repo.exists_by_id(timeline_id) is True
    assert repo.exists_by_id(timeline_id + 1) is False


# sort_order 昇順 → year 降順で並ぶ
def test_find_all_order(db):
    repo = TimelineRepository(db)
    a = repo.create(_timeline(2020, 1))
    b = repo.create(_timeline(2022, 0))
    c = repo.create(_timeline(2023, 0))

    result = repo.find_all()

    assert [t.timeline_id for t in result] == [c, b, a]


def test_update(db):
    repo = TimelineRepository(db)
    timeline_id = repo.create(_timeline(2020, 0))

    repo.update(timeline_id, 2021, "new", "body", 3)
    db.expire_all()

    timeline = repo.find_all()[0]
    assert timeline.year == 2021
    assert timeline.title == "new"
    assert timeline.body == "body"
    assert timeline.sort_order == 3


def test_delete(db):
    repo = TimelineRepository(db)
    timeline_id = repo.create(_timeline(2020, 0))

    repo.delete(timeline_id)

    assert repo.exists_by_id(timeline_id) is False
