import os
import streamlit as st
from SSH import ClienteSSH
from parsers import ParserNotice, ParserUsuarios, ParserProduto
from models import Base, Relatorio, Usuario, Produto
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import pandas as pd
import io
import logging
from datetime import datetime
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SRV_IP = os.getenv("SRV_IP")
SRV_RELATORIO_PASTA = os.getenv("SRV_RELATORIO_PASTA")
SSH_PWD = os.getenv("SSH_PWD")
SSH_LOGIN = os.getenv("SSH_LOGIN")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
session = Session()
Base.metadata.create_all(engine)

def atualizar_relatorios(
    ip:str, 
    caminho_pasta:str, 
    data_inicio:datetime, 
    login:str, 
    senha:str, 
    sessao:sqlalchemy.orm.session.Session
    ):
    c = ClienteSSH(
        ip,
        caminho_pasta,
        f"notice_{data_inicio.strftime('%d-%m-%Y')}",
        login,
        senha
        )
    c.conectar_servidor()
    lista_nomes_relatorios = c.obter_nome_relatorio()
    lista_relatorios_dict = []
    for nome_relatorio in lista_nomes_relatorios:
        conteudo_relatorio_lst = c.obter_conteudo_relatorio(nome_relatorio)
        conteudo_relatorio = "".join(conteudo_relatorio_lst)
        p = ParserNotice.ParserNoticeXML(sessao, conteudo_relatorio, nome_relatorio)
        d = p.interpretar_relatorio()
        if d: # se o relatório possui conteúdo, grava, senão, ignora, já está gravado
            lista_relatorios_dict.append(d)
    if len(lista_relatorios_dict) > 0:
        df = pd.DataFrame(lista_relatorios_dict)
        Relatorio.gravar_banco(session, df)

def atualizar_operadores(
    session:sqlalchemy.orm.session.Session, 
    csv_operadores:io.StringIO
    ):
    p = ParserUsuarios.ParserUsuarios(arquivo)
    Usuario.gravar_banco(session, p.df)

def atualizar_produtos(
    session:sqlalchemy.orm.session.Session, 
    csv_produtos:io.StringIO
):
    p = ParserProduto.ParserProduto(arquivo)
    Produto.gravar_banco(session, p.df)

hoje = datetime.now()
st.set_page_config(layout="wide")
col1, col2 = st.columns(2)
with col1:
    input_data_inicio = st.date_input("Data de início", value=hoje, format="DD/MM/YYYY")
    data_inicio = datetime.strptime(f"{input_data_inicio} 00:00:00", "%Y-%m-%d %H:%M:%S")
with col2:
    input_data_fim = st.date_input("Data de fim", value=hoje, format="DD/MM/YYYY")
    data_fim = datetime.strptime(f"{input_data_fim} 23:59:59", "%Y-%m-%d %H:%M:%S")

df_ranking_tipos = Relatorio.ranking_tipos_etiquetas_periodo(
    session, 
    data_inicio=data_inicio, 
    data_fim=data_fim
)
st.title("Geral de etiquetas")
if df_ranking_tipos is None:
    "Período sem dados das etiquetas, atualize e tente novamente"
else:
    st.dataframe(
        df_ranking_tipos,
        use_container_width=True, 
        hide_index=True,
        height=1000
        )

