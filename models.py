from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine('sqlite:///banco.sqlite3', echo=True)  # Substitua 'seubanco.db' pelo nome do seu banco de dados SQLite


Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String)
    matricula = Column(Integer)
    relatorios = relationship("Relatorio", back_populates="usuario")

class Relatorio(Base):
    __tablename__ = 'relatorios'

    id = Column(Integer, primary_key=True)
    matricula = Column(Integer, ForeignKey("usuarios.matricula"))
    tipo = Column(String)
    quantidade = Column(Integer)
    nome_arquivo = Column(String, unique=True)
    data = Column(DateTime)
    cod_produto = Column(String, ForeignKey("produto.cod_produto"))
    
    produto = relationship("Produto", back_populates="relatorios")
    usuario = relationship("Usuario", back_populates="relatorios")

class Produto(Base):
    __tablename__ = 'produto'

    id = Column(Integer, primary_key=True)
    cod_produto = Column(String)
    descricao_produto = Column(String)
    
    relatorios = relationship("Relatorio", back_populates="produto")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
