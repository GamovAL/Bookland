from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase
import datetime


class Association(SqlAlchemyBase):
    __tablename__ = 'association'
    order_id = Column(Integer, ForeignKey('order.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    count = Column(Integer)
    book = relationship("Book", back_populates="orders")
    order = relationship("Order", back_populates="books")


class Order(SqlAlchemyBase):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(200), nullable=True)
    telephone = Column(String(200), nullable=True)
    address = Column(String(200), nullable=True)
    time_order = Column(DateTime, default=datetime.datetime.now)
    time_delivery = Column(DateTime, nullable=True)
    books = relationship("Association", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order> {self.user_name}'
