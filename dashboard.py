import os
import streamlit as st
from SSH import ClienteSSH
from parsers.ParserAtacadao import ParserAtacadaoXML
from models import Base
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SRV_IP = os.getenv("SRV_IP")
SRV_RELATORIO_PASTA = os.getenv("SRV_RELATORIO_PASTA")
SSH_PWD = os.getenv("SSH_PWD")
SSH_LOGIN = os.getenv("SSH_LOGIN")

#input_data_inicio = st.date_input("Data de início", value=hoje, format="DD/MM/YYYY")
#data_inicio = datetime.strptime(f"{input_data_inicio} 00:00:00", "%Y-%m-%d %H:%M:%S")

engine = create_engine('sqlite:///banco.sqlite3')
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
        #f"notice_{data_inicio.strftime('%d-%m-%Y')}",
        "notice_15-11-2023",
        login,
        senha
        )
    c.conectar_servidor()
    lista_relatorios = c.obter_nome_relatorio()
    for nome_relatorio in lista_relatorios:
        conteudo_relatorio_lst = c.obter_conteudo_relatorio(nome_relatorio)
        conteudo_relatorio = "".join(conteudo_relatorio_lst)
        p = ParserAtacadaoXML(sessao, conteudo_relatorio, nome_relatorio)
    sessao.commit()
data_inicio = datetime.now()
atualizar_relatorios(
        SRV_IP,
        SRV_RELATORIO_PASTA,
        data_inicio,
        SSH_LOGIN,
        SSH_PWD,
        session
)
