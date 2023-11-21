from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, select, between, column, table, desc, case
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
import pandas as pd

import sqlalchemy
from sqlalchemy.sql.expression import func
import logging
from datetime import datetime
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
        result = session.execute(select(tabela_usuarios.c.id).where(tabela_usuarios.c.matricula == matricula)).first()
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
                if not Produto.existe(session, cod_produto):
                    raise Relatorio.exc.ProdutoNaoExiste(f"Produto {cod_produto} não existe no banco, peça ao CPD para atualizar a lista de produtos")
                elif not Usuario.existe(session, matricula):
                    raise Relatorio.exc.UsuarioNaoExiste(f"Usuário de matrícula {matricula} não existe no banco de dados, peça ao CPD para atualizar a lista de usuários")
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

    def ranking_geral_etiquetas_periodo(
        session:sqlalchemy.orm.session.Session, 
        data_inicio:datetime, data_fim:datetime
        ):
        """Consulta ao banco contando quantas etiquetas foram impressas por cada usuário
        Consulta SQL:
            select count(*) as quantidade, usuario.nome 
            from relatorio 
            inner join usuario on usuario.matricula = relatorio.matricula 
            where relatorio.data between data_inicio and data_fim
            group by usuario.nome order by quantidade 
            desc

        Args:
            session (sqlalchemy.orm.session.Session): Sessão conectada ao banco
            data_inicio (datetime): Data de referência do início do período
            data_fim (datetime): Data de referência de fim do período
        """
        tabela_relatorio = Relatorio.__table__
        tabela_usuario = Usuario.__table__
        consulta = select(
            func.count().label("quantidade"), tabela_usuario.c.nome 
        ).join(
            tabela_relatorio, tabela_relatorio.c.matricula == tabela_usuario.c.matricula
        ).where(
            between(Relatorio.data, data_inicio, data_fim)
        ).group_by(
            tabela_usuario.c.nome
        ).order_by(desc("quantidade"))

        r = session.execute(consulta)
        if r:
            df = pd.DataFrame(r, columns=["quantidade", "usuario"])
            return df

    def ranking_tipos_etiquetas_periodo(
        session:sqlalchemy.orm.session.Session, 
        data_inicio:datetime, data_fim:datetime
        ):
        """Consulta ao banco contando quantas etiquetas foram impressas por cada usuário
        Consulta SQL:
            select 
            count(CASE WHEN relatorio.tipo = "C" THEN 1 ELSE NULL end) as quantidade_etiqueta_c, 
            count(CASE WHEN relatorio.tipo = "X" THEN 1 ELSE NULL end) as quantidade_etiqueta_x, 
            count(*) as total_etiquetas,
            usuario.nome 
            from relatorio 
            inner join usuario on usuario.matricula = relatorio.matricula 
            group by usuario.nome order by total_etiquetas 
            desc

        Args:
            session (sqlalchemy.orm.session.Session): Sessão conectada ao banco
            data_inicio (datetime): Data de referência do início do período
            data_fim (datetime): Data de referência de fim do período
        """
        tabela_relatorio = Relatorio.__table__
        tabela_usuario = Usuario.__table__

        consulta = select(
            func.count().label("total_etiquetas"), 
            func.count(case({"C": 1}, value=tabela_relatorio.c.tipo), else_=None).label("etiquetas_c"),
            func.count(case({"X": 1}, value=tabela_relatorio.c.tipo), else_=None).label("etiquetas_x"),
            func.count(case({"papeleta": 1}, value=tabela_relatorio.c.tipo), else_=None).label("papeletas"),
            tabela_usuario.c.nome 
        ).join(
            tabela_relatorio, tabela_relatorio.c.matricula == tabela_usuario.c.matricula
        ).where(
            between(Relatorio.data, data_inicio, data_fim)
        ).group_by(
            tabela_usuario.c.nome
        ).order_by(desc("total_etiquetas"))

        r = session.execute(consulta)
        resultado = r.all()
        if len(resultado) > 0:
            df = pd.DataFrame(resultado)
            return df

    
    def ranking_etiqueta_X_periodo(
        session:sqlalchemy.orm.session.Session, 
        data_inicio:datetime, data_fim:datetime
        ):
        """Consulta ao banco contando quantas etiquetas do tipo X foram impressas por cada usuário
        Args:
            session (sqlalchemy.orm.session.Session): Sessão conectada ao banco
            data_inicio (datetime): Data de referência do início do período
            data_fim (datetime): Data de referência de fim do período
        """
        tabela_relatorio = Relatorio.__table__
        tabela_usuario = Usuario.__table__
        consulta = select(
            func.count().label("quantidade"), tabela_usuario.c.nome 
        ).join(
            tabela_relatorio, tabela_relatorio.c.matricula == tabela_usuario.c.matricula
        ).where(
            between(Relatorio.data, data_inicio, data_fim) 
        ).where(
            tabela_relatorio.c.tipo == "X"    
        ).group_by(
            tabela_usuario.c.nome
        ).order_by(desc("quantidade"))

        r = session.execute(consulta)
        if r:
            df = pd.DataFrame(r, columns=["quantidade_etiquetas_x", "usuario"])
            return df
    
    def ranking_etiqueta_C_periodo(
        session:sqlalchemy.orm.session.Session, 
        data_inicio:datetime, data_fim:datetime
        ):
        """Consulta ao banco contando quantas etiquetas do tipo C foram impressas por cada usuário
        Args:
            session (sqlalchemy.orm.session.Session): Sessão conectada ao banco
            data_inicio (datetime): Data de referência do início do período
            data_fim (datetime): Data de referência de fim do período
        """
        tabela_relatorio = Relatorio.__table__
        tabela_usuario = Usuario.__table__
        consulta = select(
            func.count().label("quantidade"), tabela_usuario.c.nome 
        ).join(
            tabela_relatorio, tabela_relatorio.c.matricula == tabela_usuario.c.matricula
        ).where(
            between(Relatorio.data, data_inicio, data_fim) 
        ).where(
            tabela_relatorio.c.tipo == "C"    
        ).group_by(
            tabela_usuario.c.nome
        ).order_by(desc("quantidade"))

        r = session.execute(consulta)
        if r:
            df = pd.DataFrame(r, columns=["quantidade_etiquetas_c", "usuario"])
            return df
    
    def ranking_papeleta_periodo(
        session:sqlalchemy.orm.session.Session, 
        data_inicio:datetime, data_fim:datetime
        ):
        """Consulta ao banco contando quantas etiquetas do tipo papeleta foram impressas por cada usuário
        Args:
            session (sqlalchemy.orm.session.Session): Sessão conectada ao banco
            data_inicio (datetime): Data de referência do início do período
            data_fim (datetime): Data de referência de fim do período
        """
        tabela_relatorio = Relatorio.__table__
        tabela_usuario = Usuario.__table__
        consulta = select(
            func.count().label("quantidade"), tabela_usuario.c.nome 
        ).join(
            tabela_relatorio, tabela_relatorio.c.matricula == tabela_usuario.c.matricula
        ).where(
            between(Relatorio.data, data_inicio, data_fim) 
        ).where(
            tabela_relatorio.c.tipo == "papeleta"    
        ).group_by(
            tabela_usuario.c.nome
        ).order_by(desc("quantidade"))

        r = session.execute(consulta)
        if r:
            df = pd.DataFrame(r.all(), columns=["quantidade_papeleta", "usuario"])
            return df
        
    class exc():
        class ProdutoNaoExiste(Exception):
            pass
        class UsuarioNaoExiste(Exception):
            pass
class Produto(Base):
    __tablename__ = 'produto'

    id:Mapped[int] = mapped_column(primary_key = True)
    cod_produto:Mapped[int] = mapped_column(Integer, unique=True)
    descricao_produto:Mapped[str] = mapped_column(String(70))

    relatorio:Mapped[List["Relatorio"]] = relationship(back_populates="produto")
    
    def __repr__(self) -> str:
        return f"Produto - Código de produto: {self.cod_produto}, Descrição: {self.descricao_produto}"

    def todos(session:sqlalchemy.orm.session.Session) -> list:
        r = session.execute(select(Produto)).scalars().all()
        return r
    
    def existe(session:sqlalchemy.orm.session.Session, cod_produto:int):
        tabela_produto = Produto.__table__
        r = session.execute(select(tabela_produto.c.id).where(tabela_produto.c.cod_produto == cod_produto)).first()
        if r:
            return True
        else:
            return False
    
    def produto_por_codigo(session:sqlalchemy.orm.session.Session, cod_produto:int):
        tabela_produto = Produto.__table__
        r = session.execute(select(tabela_produto.c.descricao).where(tabela_produto.c.cod_produto == cod_produto)).first()
        if r:
            return r[0]
    
    def gravar_banco(session:sqlalchemy.orm.session.Session, df:pd.DataFrame):
        for ind in df.index:
            descricao = df['Nome'][ind]
            cod_produto = int(df['Código'][ind])
            if Produto.existe(session, cod_produto):
                logger.info("Produto %s já existe no banco", cod_produto)
            else:
                model_produto = Produto(
                    descricao_produto=descricao,
                    cod_produto = cod_produto
                )
                session.add(model_produto)
                logger.info("Gravando produto %s no banco", cod_produto)
                del model_produto
        session.commit()
    
if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3')  # Substitua 'seubanco.db' pelo nome do seu banco de dados SQLite
    Base.metadata.create_all(engine)    
