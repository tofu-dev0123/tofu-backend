from app.repositories.user_repository import UserRepository


def test_find_by_username(db, test_user):
    repo = UserRepository(db)

    assert repo.find_by_username("test@example.com") == test_user
    assert repo.find_by_username("none@example.com") is None


def test_find_by_id(db, test_user):
    repo = UserRepository(db)

    assert repo.find_by_id(test_user.user_id) == test_user
    assert repo.find_by_id(999) is None


def test_exists_by_username(db, test_user):
    repo = UserRepository(db)

    assert repo.exists_by_username("test@example.com") is True
    assert repo.exists_by_username("none@example.com") is False


# 更新メソッドは値を設定するだけで、commit は Service 側で行う
def test_update_methods(db, test_user):
    repo = UserRepository(db)

    repo.update_account_name(test_user, "new_name")
    repo.update_password(test_user, "new_hash")
    repo.update_email(test_user, "new@example.com")
    db.commit()
    db.expire_all()

    user = repo.find_by_id(test_user.user_id)
    assert user is not None
    assert user.account_name == "new_name"
    assert user.password == "new_hash"
    assert user.username == "new@example.com"
