from app.repositories.tag_repository import TagRepository


def test_create_and_find_ids_by_names(db):
    repo = TagRepository(db)

    python_id = repo.create("Python", "python")
    fastapi_id = repo.create("FastAPI", "fastapi")

    assert repo.find_ids_by_names(["Python", "FastAPI", "Go"]) == {
        "Python": python_id,
        "FastAPI": fastapi_id,
    }
    assert repo.find_ids_by_names(["Go"]) == {}
    assert repo.find_ids_by_names([]) == {}


def test_find_slugs_starting_with(db, make_tag):
    make_tag("Python", "python")
    make_tag("Python2", "python-2")
    make_tag("Go", "go")

    result = TagRepository(db).find_slugs_starting_with("python")

    assert sorted(result) == ["python", "python-2"]
