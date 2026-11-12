import re
from unittest.mock import patch


# タグリストが空→空リストを返す
def test_get_or_create_tag_ids_returns_empty_list_when_no_tags(tag_service):
    empty_list = []

    result = tag_service.get_or_create_tag_ids(empty_list)

    assert result == []
    tag_service.tag_repo.find_ids_by_names.assert_not_called()
    tag_service.tag_repo.create.assert_not_called()


# 既存のタグ→既存のタグIDを返す
def test_get_or_create_tag_ids_returns_existing_id(tag_service):
    tag_service.tag_repo.find_ids_by_names.return_value = {"test": 1}
    tag_list = ["test"]

    result = tag_service.get_or_create_tag_ids(tag_list)

    assert result == [1]
    tag_service.tag_repo.create.assert_not_called()


# 新規タグ衝突なし→base_slugで作成
@patch("app.services.tag_service.generate_slug", return_value="test")
def test_get_or_create_tag_ids_create_with_base_slug_when_no_conflict(
    mock_gen, tag_service
):
    tag_service.tag_repo.find_ids_by_names.return_value = {}
    tag_service.tag_repo.find_slugs_starting_with.return_value = []
    tag_service.tag_repo.create.return_value = 1
    tag_list = ["Test"]

    result = tag_service.get_or_create_tag_ids(tag_list)

    assert result == [1]
    tag_service.tag_repo.create.assert_called_once_with("Test", "test")


# 新規タグ衝突あり→インクリメントスラグで作成
@patch("app.services.tag_service.generate_slug", return_value="test")
@patch("app.services.tag_service.increment_slug_suffix", return_value="test-1")
def test_get_or_create_tag_ids_create_with_incremented_slug_when_conflict(
    mock_inc, mock_gen, tag_service
):
    tag_service.tag_repo.find_ids_by_names.return_value = {}
    tag_service.tag_repo.find_slugs_starting_with.return_value = ["test"]
    tag_service.tag_repo.create.return_value = 1
    tag_list = ["Test"]

    result = tag_service.get_or_create_tag_ids(tag_list)

    assert result == [1]
    tag_service.tag_repo.create.assert_called_once_with("Test", "test-1")


# 複数タグ混在パターン
@patch("app.services.tag_service.increment_slug_suffix", return_value="nextjs-1")
@patch("app.services.tag_service.generate_slug", side_effect=["fastapi", "nextjs"])
def test_get_or_create_tag_ids_multiple_tags(mock_gen_slug, mock_inc, tag_service):
    tag_service.tag_repo.find_ids_by_names.return_value = {"python": 5}
    tag_service.tag_repo.find_slugs_starting_with.side_effect = [[], ["nextjs"]]
    tag_service.tag_repo.create.side_effect = [10, 20]

    tags = ["python", "fastapi", "nextjs"]

    result = tag_service.get_or_create_tag_ids(tags)

    assert result == [5, 10, 20]
    tag_service.tag_repo.find_ids_by_names.assert_called_once_with(tags)
    tag_service.tag_repo.create.assert_any_call("fastapi", "fastapi")
    tag_service.tag_repo.create.assert_any_call("nextjs", "nextjs-1")


# 同一リクエスト内の重複タグ→1 回だけ作成し、同じIDを返す
@patch("app.services.tag_service.generate_slug", return_value="fastapi")
def test_get_or_create_tag_ids_duplicate_new_tags(mock_gen, tag_service):
    tag_service.tag_repo.find_ids_by_names.return_value = {}
    tag_service.tag_repo.find_slugs_starting_with.return_value = []
    tag_service.tag_repo.create.return_value = 10

    result = tag_service.get_or_create_tag_ids(["fastapi", "fastapi"])

    assert result == [10, 10]
    tag_service.tag_repo.create.assert_called_once_with("fastapi", "fastapi")


# 既存・新規タグ混在→リクエストのタグ順でIDを返す
@patch("app.services.tag_service.generate_slug", return_value="go")
def test_get_or_create_tag_ids_keeps_request_order(mock_gen, tag_service):
    tag_service.tag_repo.find_ids_by_names.return_value = {"python": 5, "rust": 7}
    tag_service.tag_repo.find_slugs_starting_with.return_value = []
    tag_service.tag_repo.create.return_value = 10

    result = tag_service.get_or_create_tag_ids(["rust", "go", "python"])

    assert result == [7, 10, 5]


# 新規タグのスラグ生成失敗→UUIDベースのスラグで作成
@patch("app.services.tag_service.generate_slug", return_value="")
def test_get_or_create_tag_ids_fallback_slug_when_generation_failed(
    mock_gen, tag_service
):
    tag_service.tag_repo.find_ids_by_names.return_value = {}
    tag_service.tag_repo.find_slugs_starting_with.return_value = []
    tag_service.tag_repo.create.return_value = 1

    result = tag_service.get_or_create_tag_ids(["・"])

    assert result == [1]
    created_slug = tag_service.tag_repo.create.call_args[0][1]
    assert re.match(r"^tag-[0-9a-f]{8}$", created_slug)

