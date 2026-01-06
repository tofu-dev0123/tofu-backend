import pytest
from app.schemas.post import PostsPostRequest, PostGetResponse, PostsPutRequest
from app.models.post import PostStatus
from app.core.exceptions.image_exceptions import ImageNotExistError
from app.core.exceptions.s3_exceptions import S3FileDeleteError
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage
from tests.mock_data.post_detail import DummyPostDetail
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError


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


# 記事詳細取得正常系
def test_get_post_detail(post_service):
    mock_post = DummyPostDetail()
    post_service.query_repo = MagicMock()
    post_service.query_repo.find_by_post_id.return_value = mock_post
    
    # サムネイル画像のモック
    mock_thumbnail = Mock()
    mock_thumbnail.image_id = 1
    mock_thumbnail.alt_text = "thumbnail alt text"
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_url.return_value = mock_thumbnail

    post_id = 1

    result = post_service.get_post_detail(post_id)

    assert isinstance(result, PostGetResponse)
    assert result.post_id == 1
    assert result.title == "テストタイトル"
    assert result.slug == "test-slug"
    assert result.content_md == "markdown"
    assert result.content_html == "<p>html</p>"
    assert result.thumbnail_url == "https://example.com/thumb.png"
    assert result.status == PostStatus.PUBLISHED
    assert len(result.images) == 2
    assert result.images[0].image_id == 1
    assert result.images[0].url == "https://example.com/img1.png"
    assert result.images[0].alt_text == "alt1"
    assert len(result.tags) == 2
    assert result.tags[0].tag_id == 10
    assert result.tags[0].name == "Python"
    assert result.tags[0].slug == "python"
    post_service.query_repo.find_by_post_id.assert_called_once_with(1)


# 記事詳細取得正常系
def test_get_post_detail_no_images_no_tags(post_service):
    mock_post = DummyPostDetail()
    mock_post.images = None
    mock_post.tags = None
    post_service.query_repo = MagicMock()
    post_service.query_repo.find_by_post_id.return_value = mock_post
    
    # サムネイル画像のモック
    mock_thumbnail = Mock()
    mock_thumbnail.image_id = 1
    mock_thumbnail.alt_text = "thumbnail alt text"
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_url.return_value = mock_thumbnail

    post_id = 1

    result = post_service.get_post_detail(post_id)

    assert result.images == []
    assert result.tags == []


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

    result = post_service.check_status_and_setting_date(PostStatus.PUBLISHED)

    assert result == fixed_time


# 公開ステータスがDRAFT→None
def test_check_status_and_setting_date_with_DRAFT(post_service):
    result = post_service.check_status_and_setting_date(PostStatus.DRAFT)

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
    post_service.check_status_and_setting_date.assert_called_once_with(
        PostStatus.PUBLISHED
    )
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
        thumbnail_url="test_thumb",
        status="PUBLISHED",
        tags=["python", "fastapi"],
        images=[1, 2],
    )

    with pytest.raises(ImageNotExistError):
        post_service.create_all(req, user_id=123)

    post_service.check_image_list.assert_called_once_with([1, 2])


# set_published_at_from_status: DRAFT → PUBLISHED（初公開）
@patch("app.services.post_service.datetime")
def test_set_published_at_from_status_draft_to_published(mock_datetime, post_service):
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time

    mock_post = Mock()
    mock_post.status = PostStatus.DRAFT
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_by_post_id.return_value = mock_post

    result = post_service.set_published_at_from_status(1, PostStatus.PUBLISHED)

    assert result == fixed_time
    post_service.post_repo.find_by_post_id.assert_called_once_with(1)


# set_published_at_from_status: PUBLISHED → DRAFT（公開解除）
def test_set_published_at_from_status_published_to_draft(post_service):
    mock_post = Mock()
    mock_post.status = PostStatus.PUBLISHED
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_by_post_id.return_value = mock_post

    result = post_service.set_published_at_from_status(1, PostStatus.DRAFT)

    assert result is None
    post_service.post_repo.find_by_post_id.assert_called_once_with(1)


# set_published_at_from_status: PUBLISHED → PUBLISHED（published_atが設定済み）
def test_set_published_at_from_status_published_to_published(post_service):
    existing_published_at = datetime(2025, 1, 1, 12, 0, 0)
    mock_post = Mock()
    mock_post.status = PostStatus.PUBLISHED
    mock_post.published_at = existing_published_at
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_by_post_id.return_value = mock_post

    result = post_service.set_published_at_from_status(1, PostStatus.PUBLISHED)

    assert result == existing_published_at
    post_service.post_repo.find_by_post_id.assert_called_once_with(1)


# set_published_at_from_status: PUBLISHED → PUBLISHED（published_atがNoneの場合）
@patch("app.services.post_service.datetime")
def test_set_published_at_from_status_published_to_published_with_none(
    mock_datetime, post_service
):
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = fixed_time

    mock_post = Mock()
    mock_post.status = PostStatus.PUBLISHED
    mock_post.published_at = None
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_by_post_id.return_value = mock_post

    result = post_service.set_published_at_from_status(1, PostStatus.PUBLISHED)

    assert result == fixed_time
    post_service.post_repo.find_by_post_id.assert_called_once_with(1)


# set_published_at_from_status: DRAFT → DRAFT
def test_set_published_at_from_status_draft_to_draft(post_service):
    mock_post = Mock()
    mock_post.status = PostStatus.DRAFT
    mock_post.published_at = None
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_by_post_id.return_value = mock_post

    result = post_service.set_published_at_from_status(1, PostStatus.DRAFT)

    assert result is None
    post_service.post_repo.find_by_post_id.assert_called_once_with(1)


# delete_image_from_s3: 正常系
def test_delete_image_from_s3_success(post_service):
    post_service.s3 = MagicMock()
    post_service.s3.extract_key_from_url.return_value = "test-key"
    post_service.s3.delete_object.return_value = None

    url = "https://example.com/image.png"

    result = post_service.delete_image_from_s3(url)

    assert result is None
    post_service.s3.extract_key_from_url.assert_called_once_with(url)
    post_service.s3.delete_object.assert_called_once_with("test-key")


# delete_image_from_s3: ClientError発生
def test_delete_image_from_s3_client_error(post_service):
    post_service.s3 = MagicMock()
    post_service.s3.extract_key_from_url.return_value = "test-key"
    post_service.s3.delete_object.side_effect = ClientError({}, "DeleteObject")

    url = "https://example.com/image.png"

    with pytest.raises(S3FileDeleteError):
        post_service.delete_image_from_s3(url)


# delete_image_from_s3: BotoCoreError発生
def test_delete_image_from_s3_boto_core_error(post_service):
    post_service.s3 = MagicMock()
    post_service.s3.extract_key_from_url.return_value = "test-key"
    post_service.s3.delete_object.side_effect = BotoCoreError()

    url = "https://example.com/image.png"

    with pytest.raises(S3FileDeleteError):
        post_service.delete_image_from_s3(url)


# update_thumbnail: flag=true & url=None → 削除
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_update_thumbnail_delete_flag_true_with_old_url(mock_delete, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = (
        "https://example.com/old.png"
    )

    result = post_service.update_thumbnail(1, None, True)

    assert result is None
    post_service.post_repo.find_thumbnail_url_by_post_id.assert_called_once_with(1)
    mock_delete.assert_called_once_with("https://example.com/old.png")


# update_thumbnail: flag=true & url=None & old_url=None → 削除なし
def test_update_thumbnail_delete_flag_true_without_old_url(post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = None

    result = post_service.update_thumbnail(1, None, True)

    assert result is None
    post_service.post_repo.find_thumbnail_url_by_post_id.assert_called_once_with(1)


# update_thumbnail: flag=true & url!=None → ApplicationError
def test_update_thumbnail_delete_flag_true_with_url_error(post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = None

    with pytest.raises(ApplicationError) as exc_info:
        post_service.update_thumbnail(1, "https://example.com/new.png", True)

    assert exc_info.value.message == ErrorMessage.BAD_REQUEST_OF_THUMBNAIL
    assert exc_info.value.code == ErrorCode.BAD_REQUEST_OF_THUMBNAIL


# update_thumbnail: flag=false & url=None → 変更なし
def test_update_thumbnail_flag_false_url_none(post_service):
    old_url = "https://example.com/old.png"
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = old_url

    result = post_service.update_thumbnail(1, None, False)

    assert result == old_url
    post_service.post_repo.find_thumbnail_url_by_post_id.assert_called_once_with(1)


# update_thumbnail: flag=false & url="" → 削除
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_update_thumbnail_flag_false_empty_string(mock_delete, post_service):
    old_url = "https://example.com/old.png"
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = old_url

    result = post_service.update_thumbnail(1, "", False)

    assert result is None
    mock_delete.assert_called_once_with(old_url)


# update_thumbnail: flag=false & url="" & old_url=None → 削除なし
def test_update_thumbnail_flag_false_empty_string_no_old_url(post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = None

    result = post_service.update_thumbnail(1, "", False)

    assert result is None


# update_thumbnail: flag=false & url!=old_url → 差し替え
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_update_thumbnail_flag_false_replace(mock_delete, post_service):
    old_url = "https://example.com/old.png"
    new_url = "https://example.com/new.png"
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = old_url

    result = post_service.update_thumbnail(1, new_url, False)

    assert result == new_url
    mock_delete.assert_called_once_with(old_url)


# update_thumbnail: flag=false & url==old_url → 同一URL
def test_update_thumbnail_flag_false_same_url(post_service):
    url = "https://example.com/same.png"
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = url

    result = post_service.update_thumbnail(1, url, False)

    assert result == url


# update_thumbnail: flag=false & 新規設定
def test_update_thumbnail_flag_false_new_url(post_service):
    new_url = "https://example.com/new.png"
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = None

    result = post_service.update_thumbnail(1, new_url, False)

    assert result == new_url


# extract_delete_images: 正常系
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_extract_delete_images_success(mock_delete, post_service):
    mock_image1 = Mock()
    mock_image1.post_id = 1
    mock_image1.url = "https://example.com/img1.png"
    mock_image2 = Mock()
    mock_image2.post_id = 1
    mock_image2.url = "https://example.com/img2.png"

    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_image_id.side_effect = [mock_image1, mock_image2]

    result = post_service.extract_delete_images(1, [10, 20])

    assert result is None
    assert post_service.image_repo.find_by_image_id.call_count == 2
    assert post_service.image_repo.delete.call_count == 2
    assert mock_delete.call_count == 2


# extract_delete_images: 画像が存在しない
def test_extract_delete_images_not_exist(post_service):
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_image_id.return_value = None

    with pytest.raises(ImageNotExistError):
        post_service.extract_delete_images(1, [10])


# extract_delete_images: 画像の所有者が異なる
def test_extract_delete_images_invalid_owner(post_service):
    mock_image = Mock()
    mock_image.post_id = 999  # 異なるpost_id

    post_service.image_repo = MagicMock()
    post_service.image_repo.find_by_image_id.return_value = mock_image

    with pytest.raises(ApplicationError) as exc_info:
        post_service.extract_delete_images(1, [10])

    assert exc_info.value.message == ErrorMessage.INVALID_IMAGE_OWNER.format(
        image_id=10
    )
    assert exc_info.value.code == ErrorCode.INVALID_IMAGE_OWNER


# update_tags: 正常系
@patch("app.services.post_service.PostService.generate_slug_of_tag_and_get_id")
@patch("app.services.post_service.PostService.create_post_tag")
def test_update_tags_success(mock_create_post_tag, mock_generate_slug, post_service):
    post_service.post_tag_repo = MagicMock()
    mock_generate_slug.return_value = [10, 20]

    result = post_service.update_tags(["python", "fastapi"], 1)

    assert result is None
    mock_generate_slug.assert_called_once_with(["python", "fastapi"])
    post_service.post_tag_repo.delete_post_tags.assert_called_once_with(1)
    mock_create_post_tag.assert_called_once_with([10, 20], 1)


# update_all: 正常系（全項目更新）
@patch("app.services.post_service.PostService.db", create=True)
@patch("app.services.post_service.PostService.attach_post_id_to_image")
@patch("app.services.post_service.PostService.update_tags")
@patch("app.services.post_service.PostService.extract_delete_images")
@patch("app.services.post_service.PostService.update_thumbnail")
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_update_all_success_full_update(
    mock_set_published_at,
    mock_update_thumbnail,
    mock_extract_delete_images,
    mock_update_tags,
    mock_attach_image,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True

    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_set_published_at.return_value = fixed_time
    mock_update_thumbnail.return_value = "https://example.com/new-thumb.png"

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        thumbnail_url="https://example.com/new-thumb.png",
        thumbnail_delete_flag=False,
        status=PostStatus.PUBLISHED,
        delete_images=[1, 2],
        new_images=[3, 4],
        tags=["python", "django"],
    )

    result = post_service.update_all(req, post_id=999)

    assert result is None
    post_service.post_repo.exist_check_by_post_id.assert_called_once_with(999)
    mock_set_published_at.assert_called_once_with(999, PostStatus.PUBLISHED)
    mock_update_thumbnail.assert_called_once_with(
        999, "https://example.com/new-thumb.png", False
    )
    mock_extract_delete_images.assert_called_once_with(999, [1, 2])
    mock_update_tags.assert_called_once_with(["python", "django"], 999)
    # update_postの呼び出しを確認（content_htmlはMarkdownから変換されるため、実際の値は確認しない）
    post_service.post_repo.update_post.assert_called_once()
    call_args = post_service.post_repo.update_post.call_args
    assert call_args.kwargs["post_id"] == 999
    assert call_args.kwargs["title"] == "Updated Title"
    assert call_args.kwargs["content_md"] == "updated_md"
    assert "content_html" in call_args.kwargs  # content_htmlが生成されていることを確認
    assert call_args.kwargs["status"] == PostStatus.PUBLISHED
    assert call_args.kwargs["published_at"] == fixed_time
    assert call_args.kwargs["thumbnail_url"] == "https://example.com/new-thumb.png"
    mock_attach_image.assert_called_once_with([3, 4], 999)
    post_service.db.commit.assert_called_once()


# update_all: 正常系（最小限の更新）
@patch("app.services.post_service.PostService.db", create=True)
@patch("app.services.post_service.PostService.update_thumbnail")
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_update_all_success_minimal_update(
    mock_set_published_at,
    mock_update_thumbnail,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True

    mock_set_published_at.return_value = None
    mock_update_thumbnail.return_value = None

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        thumbnail_url=None,
        thumbnail_delete_flag=True,
        status=PostStatus.DRAFT,
        delete_images=[],
        new_images=[],
        tags=[],
    )

    result = post_service.update_all(req, post_id=999)

    assert result is None
    post_service.post_repo.update_post.assert_called_once()
    post_service.db.commit.assert_called_once()


# update_all: 記事が存在しない
@patch("app.services.post_service.PostService.db", create=True)
def test_update_all_post_not_exist(mock_db, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = False

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        thumbnail_url=None,
        thumbnail_delete_flag=False,
        status=PostStatus.DRAFT,
        delete_images=[],
        new_images=[],
        tags=[],
    )

    with pytest.raises(ApplicationError) as exc_info:
        post_service.update_all(req, post_id=999)

    assert exc_info.value.message == ErrorMessage.NOT_EXIST
    assert exc_info.value.code == ErrorCode.NOT_EXIST
    post_service.db.rollback.assert_called_once()


# update_all: 画像削除でImageNotExistError
@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.extract_delete_images",
    side_effect=ImageNotExistError(),
)
@patch("app.services.post_service.PostService.update_thumbnail")
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_update_all_image_not_exist_error(
    mock_set_published_at,
    mock_update_thumbnail,
    mock_extract_delete_images,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True
    mock_set_published_at.return_value = None
    mock_update_thumbnail.return_value = None

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        content_html="updated_html",
        thumbnail_url=None,
        thumbnail_delete_flag=False,
        status=PostStatus.DRAFT,
        delete_images=[999],
        new_images=[],
        tags=[],
    )

    with pytest.raises(ImageNotExistError):
        post_service.update_all(req, post_id=1)

    post_service.db.rollback.assert_called_once()


# update_all: 画像削除でINVALID_IMAGE_OWNER
@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.extract_delete_images",
    side_effect=ApplicationError(
        message=ErrorMessage.INVALID_IMAGE_OWNER.format(image_id=999),
        code=ErrorCode.INVALID_IMAGE_OWNER,
    ),
)
@patch("app.services.post_service.PostService.update_thumbnail")
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_update_all_invalid_image_owner(
    mock_set_published_at,
    mock_update_thumbnail,
    mock_extract_delete_images,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True
    mock_set_published_at.return_value = None
    mock_update_thumbnail.return_value = None

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        content_html="updated_html",
        thumbnail_url=None,
        thumbnail_delete_flag=False,
        status=PostStatus.DRAFT,
        delete_images=[999],
        new_images=[],
        tags=[],
    )

    with pytest.raises(ApplicationError) as exc_info:
        post_service.update_all(req, post_id=1)

    assert exc_info.value.code == ErrorCode.INVALID_IMAGE_OWNER
    post_service.db.rollback.assert_called_once()


# update_all: サムネイル更新でBAD_REQUEST_OF_THUMBNAIL
@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.update_thumbnail",
    side_effect=ApplicationError(
        message=ErrorMessage.BAD_REQUEST_OF_THUMBNAIL,
        code=ErrorCode.BAD_REQUEST_OF_THUMBNAIL,
    ),
)
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_update_all_bad_request_of_thumbnail(
    mock_set_published_at,
    mock_update_thumbnail,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True
    mock_set_published_at.return_value = None

    req = PostsPutRequest(
        title="Updated Title",
        content_md="updated_md",
        content_html="updated_html",
        thumbnail_url="https://example.com/new.png",
        thumbnail_delete_flag=True,
        status=PostStatus.DRAFT,
        delete_images=[],
        new_images=[],
        tags=[],
    )

    with pytest.raises(ApplicationError) as exc_info:
        post_service.update_all(req, post_id=1)

    assert exc_info.value.code == ErrorCode.BAD_REQUEST_OF_THUMBNAIL
    post_service.db.rollback.assert_called_once()


# delete_thumbnail: 正常系（サムネイルが存在する場合）
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_delete_thumbnail_success(mock_delete, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = (
        "https://example.com/thumbnail.png"
    )

    result = post_service.delete_thumbnail(1)

    assert result is None
    post_service.post_repo.find_thumbnail_url_by_post_id.assert_called_once_with(1)
    mock_delete.assert_called_once_with("https://example.com/thumbnail.png")


# delete_thumbnail: 正常系（サムネイルが存在しない場合）
def test_delete_thumbnail_no_thumbnail(post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.find_thumbnail_url_by_post_id.return_value = None

    result = post_service.delete_thumbnail(1)

    assert result is None
    post_service.post_repo.find_thumbnail_url_by_post_id.assert_called_once_with(1)


# delete_image_from_post_id: 正常系（画像URLが複数ある場合）
@patch("app.services.post_service.PostService.delete_image_from_s3")
def test_delete_image_from_post_id_success(mock_delete, post_service):
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_url_by_post_id.return_value = [
        "https://example.com/img1.png",
        "https://example.com/img2.png",
        "https://example.com/img3.png",
    ]

    result = post_service.delete_image_from_post_id(1)

    assert result is None
    post_service.image_repo.find_url_by_post_id.assert_called_once_with(1)
    assert mock_delete.call_count == 3
    mock_delete.assert_any_call("https://example.com/img1.png")
    mock_delete.assert_any_call("https://example.com/img2.png")
    mock_delete.assert_any_call("https://example.com/img3.png")


# delete_image_from_post_id: 正常系（画像URLが空の場合）
def test_delete_image_from_post_id_empty_list(post_service):
    post_service.image_repo = MagicMock()
    post_service.image_repo.find_url_by_post_id.return_value = []

    result = post_service.delete_image_from_post_id(1)

    assert result is None
    post_service.image_repo.find_url_by_post_id.assert_called_once_with(1)


# delete_all: 正常系
@patch("app.services.post_service.PostService.db", create=True)
@patch("app.services.post_service.PostService.delete_image_from_post_id")
@patch("app.services.post_service.PostService.delete_thumbnail")
def test_delete_all_success(
    mock_delete_thumbnail,
    mock_delete_image_from_post_id,
    mock_db,
    post_service,
):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True
    post_service.post_tag_repo = MagicMock()
    post_service.image_repo = MagicMock()

    result = post_service.delete_all(1)

    assert result is None
    post_service.post_repo.exist_check_by_post_id.assert_called_once_with(1)
    mock_delete_thumbnail.assert_called_once_with(1)
    post_service.post_tag_repo.delete_post_tags.assert_called_once_with(1)
    mock_delete_image_from_post_id.assert_called_once_with(1)
    post_service.image_repo.delete_from_post_id.assert_called_once_with(1)
    post_service.post_repo.delete.assert_called_once_with(1)
    post_service.db.commit.assert_called_once()


# delete_all: 記事が存在しない場合
@patch("app.services.post_service.PostService.db", create=True)
def test_delete_all_post_not_exist(mock_db, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = False

    with pytest.raises(ApplicationError) as exc_info:
        post_service.delete_all(1)

    assert exc_info.value.message == ErrorMessage.NOT_EXIST
    assert exc_info.value.code == ErrorCode.NOT_EXIST
    post_service.post_repo.exist_check_by_post_id.assert_called_once_with(1)
    post_service.db.rollback.assert_called_once()


# delete_all: 例外発生時にrollbackが呼ばれる
@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.delete_thumbnail",
    side_effect=Exception("Error"),
)
def test_delete_all_exception_rollback(mock_delete_thumbnail, mock_db, post_service):
    post_service.post_repo = MagicMock()
    post_service.post_repo.exist_check_by_post_id.return_value = True

    with pytest.raises(Exception):
        post_service.delete_all(1)

    post_service.post_repo.exist_check_by_post_id.assert_called_once_with(1)
    mock_delete_thumbnail.assert_called_once_with(1)
    post_service.db.rollback.assert_called_once()


# patch_status: 正常系
@patch("app.services.post_service.PostService.db", create=True)
@patch("app.services.post_service.PostService.set_published_at_from_status")
def test_patch_status_success(mock_set_published_at, mock_db, post_service):
    post_service.post_repo = MagicMock()
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    mock_set_published_at.return_value = fixed_time

    result = post_service.patch_status(PostStatus.PUBLISHED, 1)

    assert result is None
    mock_set_published_at.assert_called_once_with(1, PostStatus.PUBLISHED)
    post_service.post_repo.update_status_and_published_at.assert_called_once_with(
        1, PostStatus.PUBLISHED, fixed_time
    )
    post_service.db.commit.assert_called_once()


# patch_status: 例外発生時にrollbackが呼ばれる
@patch("app.services.post_service.PostService.db", create=True)
@patch(
    "app.services.post_service.PostService.set_published_at_from_status",
    side_effect=Exception("Error"),
)
def test_patch_status_exception_rollback(mock_set_published_at, mock_db, post_service):
    post_service.post_repo = MagicMock()

    with pytest.raises(Exception):
        post_service.patch_status(PostStatus.PUBLISHED, 1)

    mock_set_published_at.assert_called_once_with(1, PostStatus.PUBLISHED)
    post_service.db.rollback.assert_called_once()
