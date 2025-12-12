import pytest
from app.schemas.post import PostsPostRequest
from app.core.exceptions.post_exceptions import ImageNotExistError
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# 一覧取得正常系
def test_get_posts_success(post_service):
    mock_posts = Mock()
    post_service.post_repo = MagicMock()
    post_service.post_repo.get_posts.return_value = mock_posts

    user_id = 1
    offset = 0
    limit = 1

    post_service.post_repo.get_posts(user_id, offset, limit)

    post_service.post_repo.get_posts.assert_called_once


# 画像の存在チェック正常系
def test_check_image_list_success(post_service):
    mock_image = Mock()
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_image_id.return_value = mock_image

    images = [1, 2, 3]

    result = post_service.check_image_list(images)
    assert result is None
    assert post_service.image_repo.find_by_image_id.call_count == len(images)


# 指定した画像が存在しない
def test_image_not_exist(post_service):
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_image_id.return_value = None

    images = [1]

    with pytest.raises(ImageNotExistError):
        post_service.check_image_list(images)


# タイトルスラグ衝突なし→新規作成
def test_generate_slug_of_title_no_conflict(post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_slugs_like.return_value = []

    title = "Test title"
    base_slug = "test-title"

    result = post_service.generate_slug_of_title(title)

    assert result == base_slug
    post_service.post_repo.find_slugs_like.assert_called_once_with(base_slug)


# タイトルスラグ衝突→increment_suffixで作成
@patch("app.services.post_service.increment_slug_suffix", return_value="test-title-1")
def test_generate_slug_of_title_conflict(mock_inc, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_slugs_like.return_value = ["test-title"]

    title = "Test title"

    result = post_service.generate_slug_of_title(title)

    assert result == "test-title-1"


# タグリストが空→空リストを返す
def test_generate_slug_returns_empty_list_when_no_tags(post_service):
    post_service.tag_repo = MagicMock()
    empty_list = []

    result = post_service.generate_slug_of_tag_and_get_id(empty_list)

    assert result == []
    post_service.tag_repo.create.assert_not_called()


# 既存のタグ→既存のタグIDを返す
def test_generate_slug_returns_existing_id(post_service):
    post_service.tag_repo = MagicMock()
    post_service.tag_repo.find_id_by_name.return_value = 1
    tag_list = ["test"]

    result = post_service.generate_slug_of_tag_and_get_id(tag_list)

    assert result == [1]
    post_service.tag_repo.create.assert_not_called()


# 新規タグ衝突なし→base_slugで作成
@patch("app.services.post_service.generate_slug", return_value="test")
def test_generate_slug_create_with_base_slug_when_no_conflict(mock_inc, post_service):
    post_service.tag_repo = MagicMock()
    post_service.tag_repo.find_id_by_name.return_value = None
    post_service.tag_repo.find_slugs_starting_with.return_value = []
    post_service.tag_repo.create.return_value = 1
    tag_list = ["Test"]

    result = post_service.generate_slug_of_tag_and_get_id(tag_list)

    assert result == [1]
    post_service.tag_repo.create.assert_called_once_with("Test", "test")


# 新規タグ衝突あり→base_slugで作成
@patch("app.services.post_service.generate_slug", return_value="test")
@patch("app.services.post_service.increment_slug_suffix", return_value="test-1")
def test_generate_slug_create_with_incremented_slug_when_conflict(
    mock_gen, mock_inc, post_service
):
    post_service.tag_repo = MagicMock()
    post_service.tag_repo.find_id_by_name.return_value = None
    post_service.tag_repo.find_slugs_starting_with.return_value = ["test"]
    post_service.tag_repo.create.return_value = 1
    tag_list = ["Test"]

    result = post_service.generate_slug_of_tag_and_get_id(tag_list)

    assert result == [1]
    post_service.tag_repo.create.assert_called_once_with("Test", "test-1")


# 複数タグ混在パターン
@patch("app.services.post_service.increment_slug_suffix", return_value="nextjs-1")
@patch("app.services.post_service.generate_slug", side_effect=["fastapi", "nextjs"])
def test_generate_slug_multiple_tags(mock_gen_slug, mock_inc, post_service):
    post_service.tag_repo = MagicMock()
    post_service.tag_repo.find_id_by_name.side_effect = [5, None, None]

    post_service.tag_repo.find_slugs_starting_with.side_effect = [[], ["nextjs"]]

    post_service.tag_repo.create.side_effect = [10, 20]

    tags = ["python", "fastapi", "nextjs"]

    result = post_service.generate_slug_of_tag_and_get_id(tags)

    assert result == [5, 10, 20]

    post_service.tag_repo.create.assert_any_call("fastapi", "fastapi")
    post_service.tag_repo.create.assert_any_call("nextjs", "nextjs-1")


# 公開ステータスがPUBLISHED→現在時刻を返す
@patch("app.services.post_service.datetime")
def test_check_status_and_setting_date_with_PUBLISHED(mock_datetime, post_service):
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time

    result = post_service.check_status_and_setting_date("PUBLISHED")

    assert result == fixed_time


# 公開ステータスがDRAFT→None
def test_check_status_and_setting_date_with_DRAFT(post_service):
    result = post_service.check_status_and_setting_date("DRAFT")

    assert result is None


# 記事の登録処理
@patch("app.services.post_service.PostService.db", create=True)
@patch("app.services.post_service.PostService.attach_post_id_to_image")
@patch("app.services.post_service.PostService.create_post_tag")
@patch("app.services.post_service.PostService.create_post")
@patch("app.services.post_service.PostService.check_status_and_setting_date")
@patch("app.services.post_service.PostService.generate_slug_of_tag_and_get_id")
@patch("app.services.post_service.PostService.generate_slug_of_title")
@patch("app.services.post_service.PostService.check_image_list")
def test_create_all_success_with_tags_and_images(
    mock_check_image_list,
    mock_generate_slug_of_title,
    mock_generate_slug_of_tag_and_get_id,
    mock_check_status_date,
    mock_create_post,
    mock_create_post_tag,
    mock_attach_image,
    mock_db,
    post_service,
):
    req = PostsPostRequest(
        title="Test",
        content_md="test_md",
        content_html="test_html",
        thumbnail_url="test_thumb",
        status="PUBLISHED",
        tags=["python", "fastapi"],
        images=[1, 2],
    )
    mock_generate_slug_of_title.return_value = "test-slug"
    mock_generate_slug_of_tag_and_get_id.return_value = [10, 20]
    mock_check_status_date.return_value = datetime(2025, 1, 1)
    mock_create_post.return_value = 999

    result = post_service.create_all(req, user_id=123)

    assert result == 999

    post_service.check_image_list.assert_called_once_with([1, 2])
    post_service.generate_slug_of_title.assert_called_once_with("Test")
    post_service.generate_slug_of_tag_and_get_id.assert_called_once_with(
        ["python", "fastapi"]
    )
    post_service.check_status_and_setting_date.assert_called_once_with("PUBLISHED")
    post_service.create_post.assert_called_once()
    post_service.create_post_tag.assert_called_once_with([10, 20], 999)
    post_service.attach_post_id_to_image.assert_called_once_with([1, 2], 999)
    post_service.db.commit.assert_called_once()

    # 記事の登録→例外スロー


@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.check_image_list",
    side_effect=ImageNotExistError("not found"),
)
def test_create_all_image_not_exist_error(
    mock_check_image_list,
    mock_db,
    post_service,
):
    req = PostsPostRequest(
        title="Test",
        content_md="test_md",
        content_html="test_html",
        thumbnail_url="test_thumb",
        status="PUBLISHED",
        tags=["python", "fastapi"],
        images=[1, 2],
    )

    with pytest.raises(ImageNotExistError):
        post_service.create_all(req, user_id=123)

    post_service.check_image_list.assert_called_once_with([1, 2])
