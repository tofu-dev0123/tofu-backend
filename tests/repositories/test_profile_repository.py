from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


def test_get_none(db):
    assert ProfileRepository(db).get() is None


# 先頭（profile_id 最小）のプロフィールを返す
def test_get(db):
    first = Profile(headline="first", bio="", site_description="")
    second = Profile(headline="second", bio="", site_description="")
    db.add_all([first, second])
    db.flush()

    assert ProfileRepository(db).get() == first


def test_update(db):
    profile = Profile(headline="old", bio="old", site_description="old")
    db.add(profile)
    db.flush()
    repo = ProfileRepository(db)

    repo.update(profile.profile_id, "headline", "bio", "desc")
    db.expire_all()

    result = repo.get()
    assert result is not None
    assert result.headline == "headline"
    assert result.bio == "bio"
    assert result.site_description == "desc"
