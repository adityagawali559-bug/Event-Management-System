from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database.database import get_db
from app.models.category import Category
from app.models.event import Event
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.dependencies.auth import require_admin, require_organizer

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all event categories along with event counts."""
    categories = db.query(Category).order_by(Category.name.asc()).all()
    res = []
    for cat in categories:
        count = db.query(func.count(Event.id)).filter(Event.category_id == cat.id).scalar() or 0
        cat_resp = CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            created_at=cat.created_at,
            event_count=count,
        )
        res.append(cat_resp)
    return res


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    """Retrieve a single category by its ID."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found.",
        )
    count = db.query(func.count(Event.id)).filter(Event.category_id == cat.id).scalar() or 0
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        created_at=cat.created_at,
        event_count=count,
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_organizer),
):
    """Create a new category (Organizer or Admin). Returns existing category if already present."""
    name_clean = cat_in.name.strip()
    existing = db.query(Category).filter(func.lower(Category.name) == name_clean.lower()).first()
    if existing:
        count = db.query(func.count(Event.id)).filter(Event.category_id == existing.id).scalar() or 0
        return CategoryResponse(
            id=existing.id,
            name=existing.name,
            description=existing.description,
            created_at=existing.created_at,
            event_count=count,
        )
    cat = Category(name=name_clean, description=cat_in.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        created_at=cat.created_at,
        event_count=0,
    )


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Update a category (Admin only)."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    if cat_in.name is not None:
        conflict = (
            db.query(Category)
            .filter(func.lower(Category.name) == cat_in.name.lower().strip(), Category.id != category_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another category with this name already exists.",
            )
        cat.name = cat_in.name.strip()
    if cat_in.description is not None:
        cat.description = cat_in.description

    db.commit()
    db.refresh(cat)
    count = db.query(func.count(Event.id)).filter(Event.category_id == cat.id).scalar() or 0
    return CategoryResponse(
        id=cat.id,
        name=cat.name,
        description=cat.description,
        created_at=cat.created_at,
        event_count=count,
    )


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Delete a category (Admin only)."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")

    db.delete(cat)
    db.commit()
    return {"message": "Category deleted successfully."}
