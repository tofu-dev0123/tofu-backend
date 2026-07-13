from unittest.mock import MagicMock, patch


# タグリストが空→空リストを返す
def test_get_or_create_tag_ids_returns_empty_list_when_no_tags(tag_service):
    tag_service.tag_repo = MagicMock()
    empty_list = []

    result = tag_service.get_or_create_tag_ids(empty_list)

    assert result == []
    tag_service.tag_repo.create.assert_not_called()


# 既存のタグ→既存のタグIDを返す
def test_get_or_create_tag_ids_returns_existing_id(tag_service):
    tag_service.tag_repo = MagicMock()
    tag_service.tag_repo.find_id_by_name.return_value = 1
    tag_list = ["test"]

    result = tag_service.get_or_create_tag_ids(tag_list)

    assert result == [1]
    tag_service.tag_repo.create.assert_not_called()


# 新規タグ衝突なし→base_slugで作成
@patch("app.services.tag_service.generate_slug", return_value="test")
def test_get_or_create_tag_ids_create_with_base_slug_when_no_conflict(
    mock_gen, tag_service
):
    tag_service.tag_repo = MagicMock()
    tag_service.tag_repo.find_id_by_name.return_value = None
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
    tag_service.tag_repo = MagicMock()
    tag_service.tag_repo.find_id_by_name.return_value = None
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
    tag_service.tag_repo = MagicMock()
    tag_service.tag_repo.find_id_by_name.side_effect = [5, None, None]
    tag_service.tag_repo.find_slugs_starting_with.side_effect = [[], ["nextjs"]]
    tag_service.tag_repo.create.side_effect = [10, 20]

    tags = ["python", "fastapi", "nextjs"]

    result = tag_service.get_or_create_tag_ids(tags)

    assert result == [5, 10, 20]
    tag_service.tag_repo.create.assert_any_call("fastapi", "fastapi")
    tag_service.tag_repo.create.assert_any_call("nextjs", "nextjs-1")
