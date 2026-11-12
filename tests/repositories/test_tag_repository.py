from app.repositories.tag_repository import TagRepository


def test_create_and_find_id_by_name(db):
    repo = TagRepository(db)

    tag_id = repo.create("Python", "python")

    assert repo.find_id_by_name("Python") == tag_id
    assert repo.find_id_by_name("Go") is None


def test_find_slugs_starting_with(db, make_tag):
    make_tag("Python", "python")
    make_tag("Python2", "python-2")
    make_tag("Go", "go")

    result = TagRepository(db).find_slugs_starting_with("python")

    assert sorted(result) == ["python", "python-2"]
