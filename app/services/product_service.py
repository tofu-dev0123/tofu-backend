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
from app.schemas.tag import Tag
from app.core.exceptions.handlers import ApplicationError
from app.common.errorcode import ErrorCode
from app.common.message import ErrorMessage


class ProductService:

    def __init__(self, db: Session):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.product_tag_repo = ProductTagRepository(db)
        self.tag_service = TagService(db)

    """
    プロダクトモデルをスキーマに変換する
    """

    def _to_schema(self, product: ProductModel) -> Product:
        tags = [
            Tag(tag_id=tag.tag_id, name=tag.name, slug=tag.slug)
            for tag in product.tags
        ]
        return Product(
            product_id=product.product_id,
            title=product.title,
            description=product.description,
            link_url=product.link_url,
            published=product.published,
            sort_order=product.sort_order,
            tags=tags,
        )

    """
    プロダクト一覧を取得する
    """

    def get_products(self) -> ProductListResponse:
        products = self.product_repo.find_all()
        return ProductListResponse(products=[self._to_schema(p) for p in products])

    """
    プロダクト詳細を取得する
    """

    def get_product(self, product_id: int) -> Product:
        product = self.product_repo.find_by_id(product_id)

        if product is None:
            raise ApplicationError(
                message=ErrorMessage.PRODUCT_NOT_EXIST, code=ErrorCode.NOT_EXIST
            )

        return self._to_schema(product)

    """
    中間テーブルにタグを登録する
    """

    def create_product_tag(self, tag_id_list: list[int], product_id: int):
        for tag_id in tag_id_list:
            self.product_tag_repo.create(
                ProductTag(product_id=product_id, tag_id=tag_id)
            )

    """
    プロダクトを作成する
    """

    def create_product(self, request: ProductPostRequest) -> int:
        try:
            tag_id_list = self.tag_service.get_or_create_tag_ids(request.tags)

            product = ProductModel(
                title=request.title,
                description=request.description,
                link_url=request.link_url,
                published=request.published,
                sort_order=request.sort_order,
            )

            product_id = self.product_repo.create(product)

            self.create_product_tag(tag_id_list, product_id)

            self.db.commit()

            return product_id

        except:
            self.db.rollback()
            raise

    """
    プロダクトを更新する
    """

    def update_product(self, product_id: int, request: ProductPutRequest) -> None:
        try:
            if not self.product_repo.exist_check(product_id):
                raise ApplicationError(
                    message=ErrorMessage.PRODUCT_NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            self.product_repo.update(
                product_id,
                request.title,
                request.description,
                request.link_url,
                request.published,
                request.sort_order,
            )

            # タグの更新（一旦削除して再登録）
            tag_id_list = self.tag_service.get_or_create_tag_ids(request.tags)
            self.product_tag_repo.delete_product_tags(product_id)
            self.create_product_tag(tag_id_list, product_id)

            self.db.commit()

        except:
            self.db.rollback()
            raise

    """
    プロダクトを削除する
    """

    def delete_product(self, product_id: int) -> None:
        try:
            if not self.product_repo.exist_check(product_id):
                raise ApplicationError(
                    message=ErrorMessage.PRODUCT_NOT_EXIST, code=ErrorCode.NOT_EXIST
                )

            self.product_tag_repo.delete_product_tags(product_id)
            self.product_repo.delete(product_id)

            self.db.commit()

        except:
            self.db.rollback()
            raise
