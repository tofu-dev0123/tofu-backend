from sqlalchemy.orm import Session
from app.repositories.tag_repository import TagRepository
from app.utils.slug_utils import generate_slug, increment_slug_suffix


class TagService:

    def __init__(self, db: Session):
        self.db = db
        self.tag_repo = TagRepository(db)

    """
    タグ名リストから既存タグIDを取得し、無ければスラグを生成して作成しIDを返す
    """

    def get_or_create_tag_ids(self, tags: list[str]) -> list[int]:
        id_list = []

        if not tags:
            return id_list

        for tag_name in tags:
            id = self.tag_repo.find_id_by_name(tag_name)

            # DBからidを取得できたらそのidを使う
            if id:
                id_list.append(id)
                continue

            # ベーススラグの生成
            base_slug = generate_slug(tag_name)

            existing_slugs = self.tag_repo.find_slugs_starting_with(base_slug)

            # 同じものがなければそのまま登録
            if base_slug not in existing_slugs:
                new_id = self.tag_repo.create(tag_name, base_slug)
                id_list.append(new_id)
                continue

            tag_slug = increment_slug_suffix(base_slug, existing_slugs)

            new_id = self.tag_repo.create(tag_name, tag_slug)

            id_list.append(new_id)

        return id_list
