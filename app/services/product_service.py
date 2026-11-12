import logging
from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.repositories.product_tag_repository import ProductTagRepository
from app.services.tag_service import TagService
from app.models.product import Product as ProductModel
from app.models.product_tag import ProductTag
from app.schemas.product import (
    Product,
    ProductListResponse,
    ProductPostRequest,
    ProductPutRequest,
)
from app.common.message import ErrorMessage
from app.services.transaction import transaction
from app.services.guards import ensure_exists
from app.services.mappers import to_product

logger = logging.getLogger(__name__)


class ProductService:

    def __init__(
        self,
        db: Session,
        product_repo: ProductRepository | None = None,
        product_tag_repo: ProductTagRepository | None = None,
        tag_service: TagService | None = None,
    ) -> None:
        self.db = db
        self.product_repo = product_repo or ProductRepository(db)
        self.product_tag_repo = product_tag_repo or ProductTagRepository(db)
        self.tag_service = tag_service or TagService(db)

    """
    プロダクト一覧を取得する
    """

    def get_products(self) -> ProductListResponse:
        products = self.product_repo.find_all()
        return ProductListResponse(products=[to_product(p) for p in products])

    """
    プロダクト詳細を取得する
    """

    def get_product(self, product_id: int) -> Product:
        product = ensure_exists(
            self.product_repo.find_by_id(product_id),
            ErrorMessage.PRODUCT_NOT_EXIST,
        )

        return to_product(product)

    """
    中間テーブルにタグを登録する
    """

    def create_product_tag(self, tag_id_list: list[int], product_id: int) -> None:
        for tag_id in tag_id_list:
            self.product_tag_repo.create(
                ProductTag(product_id=product_id, tag_id=tag_id)
            )

    """
    プロダクトを作成する
    """

    def create_product(self, request: ProductPostRequest) -> int:
        with transaction(self.db):
            tag_id_list = self.tag_service.get_or_create_tag_ids(request.tags)

            product = ProductModel(
                title=request.title,
                description=request.description,
                link_url=request.link_url,
                github_url=request.github_url,
                published=request.published,
                sort_order=request.sort_order,
            )

            product_id = self.product_repo.create(product)

            self.create_product_tag(tag_id_list, product_id)

        logger.info("product created", extra={"product_id": product_id})

        return product_id

    """
    プロダクトを更新する
    """

    def update_product(self, product_id: int, request: ProductPutRequest) -> None:
        with transaction(self.db):
            ensure_exists(
                self.product_repo.exists_by_id(product_id),
                ErrorMessage.PRODUCT_NOT_EXIST,
            )

            self.product_repo.update(
                product_id,
                request.title,
                request.description,
                request.link_url,
                request.github_url,
                request.published,
                request.sort_order,
            )

            # タグの更新（一旦削除して再登録）
            tag_id_list = self.tag_service.get_or_create_tag_ids(request.tags)
            self.product_tag_repo.delete_product_tags(product_id)
            self.create_product_tag(tag_id_list, product_id)

        logger.info("product updated", extra={"product_id": product_id})

    """
    プロダクトを削除する
    """

    def delete_product(self, product_id: int) -> None:
        with transaction(self.db):
            ensure_exists(
                self.product_repo.exists_by_id(product_id),
                ErrorMessage.PRODUCT_NOT_EXIST,
            )

            self.product_tag_repo.delete_product_tags(product_id)
            self.product_repo.delete(product_id)

        logger.info("product deleted", extra={"product_id": product_id})
