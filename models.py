from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, select, between, column, table
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = 'usuario'
    id: Mapped[int] = mapped_column(primary_key = True)
    matricula:Mapped[int] = mapped_column(Integer, unique=True)
    nome:Mapped[str] = mapped_column(String(100))
    
    relatorio:Mapped[List["Relatorio"]] = relationship(back_populates="usuario")

class Relatorio(Base):
    __tablename__ = 'relatorio'

    id: Mapped[int] = mapped_column(primary_key = True)
    tipo:Mapped[str] = mapped_column(String(10))
    quantidade:Mapped[int] = mapped_column(Integer)
    nome_arquivo:Mapped[str] = mapped_column(String(70), unique=True)
    data = mapped_column(DateTime, nullable=False)
    
    cod_produto:Mapped[int] = mapped_column(ForeignKey("produto.cod_produto"))
    matricula:Mapped[int] = mapped_column(ForeignKey("usuario.matricula"))
    
    usuario:Mapped["Usuario"] = relationship(back_populates="relatorio")
    produto:Mapped["Produto"] = relationship(back_populates="relatorio")

class Produto(Base):
    __tablename__ = 'produto'

    id:Mapped[int] = mapped_column(primary_key = True)
    cod_produto:Mapped[int] = mapped_column(Integer)
    descricao_produto:Mapped[str] = mapped_column(String(70), unique=True)

    relatorio:Mapped[List["Relatorio"]] = relationship(back_populates="produto")
    

if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3')  # Substitua 'seubanco.db' pelo nome do seu banco de dados SQLite
    Base.metadata.create_all(engine)    
