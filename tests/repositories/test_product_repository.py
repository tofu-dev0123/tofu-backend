from app.models.product import Product
from app.models.product_tag import ProductTag
from app.repositories.product_repository import ProductRepository
from app.repositories.product_tag_repository import ProductTagRepository


def _product(title: str, published: bool = True, sort_order: int = 0) -> Product:
    return Product(title=title, published=published, sort_order=sort_order)


def test_create_and_exists_by_id(db):
    repo = ProductRepository(db)

    product_id = repo.create(_product("a"))

    assert repo.exists_by_id(product_id) is True
    assert repo.exists_by_id(product_id + 1) is False


# sort_order 昇順 → product_id 昇順で並ぶ
def test_find_all_order(db):
    repo = ProductRepository(db)
    a = repo.create(_product("a", sort_order=1))
    b = repo.create(_product("b", sort_order=0))
    c = repo.create(_product("c", sort_order=0))

    assert [p.product_id for p in repo.find_all()] == [b, c, a]


# 公開中のみ返す
def test_find_published(db):
    repo = ProductRepository(db)
    published = repo.create(_product("a", published=True))
    repo.create(_product("b", published=False))

    assert [p.product_id for p in repo.find_published()] == [published]


# タグ付きで取得できる（ProductTagRepository で登録・削除）
def test_find_by_id_with_tags(db, make_tag):
    repo = ProductRepository(db)
    tag_repo = ProductTagRepository(db)
    product_id = repo.create(_product("a"))
    tag = make_tag("Python", "python")
    tag_repo.create(ProductTag(product_id=product_id, tag_id=tag.tag_id))
    db.flush()
    db.expire_all()

    product = repo.find_by_id(product_id)
    assert product is not None
    assert [t.slug for t in product.tags] == ["python"]

    tag_repo.delete_product_tags(product_id)
    db.expire_all()

    product = repo.find_by_id(product_id)
    assert product is not None
    assert product.tags == []
    assert repo.find_by_id(product_id + 1) is None


def test_update(db):
    repo = ProductRepository(db)
    product_id = repo.create(_product("a", published=False))

    repo.update(product_id, "b", "desc", "https://example.com", None, True, 2)
    db.expire_all()

    product = repo.find_by_id(product_id)
    assert product is not None
    assert product.title == "b"
    assert product.description == "desc"
    assert product.link_url == "https://example.com"
    assert product.github_url is None
    assert product.published is True
    assert product.sort_order == 2


def test_delete(db):
    repo = ProductRepository(db)
    product_id = repo.create(_product("a"))

    repo.delete(product_id)

    assert repo.exists_by_id(product_id) is False
