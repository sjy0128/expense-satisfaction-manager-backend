from sqlalchemy.orm import Session

from model.category_model import Category


def insert(db: Session,
    category_name: str,
    category_description: str | None = None,
    category_color: str = "000000"
) -> Category:
    category = Category(
        category_name=category_name,
        category_description=category_description,
        category_color=category_color
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def find_all(db: Session) -> list[Category]:
    return db.query(Category).all()


def find_by_keyword(db: Session, keyword: str) -> list[Category]:
    return db.query(Category).filter(Category.category_name.like(f"%{keyword}%")).all()


def find_by_id(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.category_id == category_id).first()


def update(db: Session, category: Category, **kwargs):
    for key, value in kwargs.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()