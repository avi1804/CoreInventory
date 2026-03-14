from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def signup(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login(db: Session, user: UserLogin) -> User:
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        return None
    if not verify_password(user.password, db_user.password):
        return None
    return db_user
