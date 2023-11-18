from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, select, between, column, table
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import pandas as pd
import sqlalchemy
import logging
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = 'usuario'
    id: Mapped[int] = mapped_column(primary_key = True)
    matricula:Mapped[int] = mapped_column(Integer, unique=True)
    nome:Mapped[str] = mapped_column(String(100))
    
    relatorio:Mapped[List["Relatorio"]] = relationship(back_populates="usuario")
    
    def __repr__(self) -> str:
        return f"Usuário - Matrícula: {self.matricula}, Nome: {self.nome}"

    def todos(session:sqlalchemy.orm.session.Session) -> list:
        r = session.execute(select(Usuario)).scalars().all()
        return r
    
    def usuario_por_codigo(session:sqlalchemy.orm.session.Session, matricula:int):
        r = session.execute(select(Usuario).where(Usuario.matricula == matricula)).first()
        if r:
            return r[0]
    
    def existe(session:sqlalchemy.orm.session.Session, matricula:int) -> bool:
        tabela_usuarios = Usuario.__table__
        result = session.execute(select(tabela_usuarios.c.id).where(tabela_usuario.c.matricula == matricula)).first()
        if result:
            return True
        else:
            return False
    
    def gravar_banco(session:sqlalchemy.orm.session.Session, df:pd.DataFrame):
        for ind in df.index:
            matricula = int(df['Código'][ind])
            nome = df['Nome'][ind]

            if Usuario.existe(session, matricula):
                logger.info("Usuário %s já existe no banco", nome)
            else:
                model_usuario = Usuario(
                matricula=matricula,
                nome=nome
            )
                session.add(model_usuario)
                logger.info("Gravando usuario %s no banco", nome)
                del model_usuario
        session.commit()
    
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

    def __repr__(self) -> str:
        return f"Relatório - Tipo: {self.tipo}, Data: {self.data}, Código de produto: {self.cod_produto}, Matrícula: {self.matricula}"
    
    def todos(session:sqlalchemy.orm.session.Session) -> list:
        tabela_relatorio = Relatorio.__table__
        r = session.execute(select(tabela_relatorio.c)).scalars().all()
        return r
    
    def existe(session, nome_arquivo:str) -> bool:
        tabela_relatorio = Relatorio.__table__
        result = session.execute(select(tabela_relatorio.c.id).where(tabela_relatorio.c.nome_arquivo == nome_arquivo)).first()
        if result:
            return True
        else:
            return False
    
    def gravar_banco(session:sqlalchemy.orm.session.Session, df:pd.DataFrame):
        for ind in df.index:
            matricula = int(df['matricula'][ind])
            tipo = df['tipo'][ind]
            data = df['data'][ind]
            quantidade = int(df['quantidade'][ind])
            nome_arquivo = df['nome_arquivo'][ind]
            cod_produto = int(df['cod_produto'][ind])

            if Relatorio.existe(session, nome_arquivo):
                logger.info("Relatório %s já existe no banco", nome_arquivo)
            else:
                model_relatorio = Relatorio(
                    matricula = matricula,
                    tipo = tipo,
                    data = data,
                    quantidade = quantidade,
                    nome_arquivo = nome_arquivo,
                    cod_produto = cod_produto
                )
                session.add(model_relatorio)
                logger.info("Gravando relatorio %s no banco", nome_arquivo)
                del model_relatorio
        session.commit()

    
class Produto(Base):
    __tablename__ = 'produto'

    id:Mapped[int] = mapped_column(primary_key = True)
    cod_produto:Mapped[int] = mapped_column(Integer)
    descricao_produto:Mapped[str] = mapped_column(String(70), unique=True)

    relatorio:Mapped[List["Relatorio"]] = relationship(back_populates="produto")
    
    def __repr__(self) -> str:
        return f"Produto - Código de produto: {self.cod_produto}, Descrição: {self.descricao_produto}"

    @classmethod
    def todos(session:sqlalchemy.orm.session.Session) -> list:
        r = session.execute(select(Produto)).scalars().all()
        return r
    
    @classmethod
    def produto_por_codigo(session:sqlalchemy.orm.session.Session, cod_produto:int):
        r = session.execute(select(Produto).where(Produto.cod_produto == cod_produto)).first()
        if r:
            return r[0]
    
if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3')  # Substitua 'seubanco.db' pelo nome do seu banco de dados SQLite
    Base.metadata.create_all(engine)    
