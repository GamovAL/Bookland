import sqlalchemy
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase):
    __tablename__ = 'book'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pages = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pdf = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    orders = relationship("Association", back_populates="book")

    def __repr__(self):
        return f'<Book> {self.title}'
