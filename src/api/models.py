from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy import DateTime
from datetime import datetime
from typing import List

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    image: Mapped[str] = mapped_column(String(200), nullable=True)

    comics: Mapped[List["MyComics"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "last_name": self.last_name,
            "image": self.image
            # do not serialize the password, its a security breach
        }


class Libro(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    pages: Mapped[int] = mapped_column(nullable=False)
    isbn: Mapped[int] = mapped_column(nullable=False)
    img: Mapped[str] = mapped_column(String(240), nullable = False)
    
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id"), nullable=False)
    editorial_id: Mapped[int] = mapped_column(ForeignKey("editorial.id"), nullable=False)

    author_rel: Mapped["Author"] = relationship(back_populates="libros")
    editorial_rel: Mapped["Editorial"] = relationship(back_populates="libros")
    users: Mapped[List["MyComics"]] = relationship(back_populates="libro")

    
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "pages": self.pages,
            "isbn": self.isbn,
            "img": self.img,
            "author": self.author_rel.name,
            "editorial": self.editorial_rel.name
        }


class Editorial(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    libros: Mapped[List["Libro"]] = relationship(back_populates="editorial_rel")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Author(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    libros: Mapped[List["Libro"]] = relationship(back_populates="author_rel")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }
    
    
class MyComics(db.Model):
    id:Mapped[int]= mapped_column(primary_key= True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libro.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    libro: Mapped["Libro"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="comics")

    def serialize(self):
        return {
            "id": self.id,
            "libro_id": self.libro_id,
            "user_id": self.user_id
        }
