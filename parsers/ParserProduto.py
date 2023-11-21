import io
import pandas as pd
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Dashboard_etiquetas_por_usuario.models import Usuario, Relatorio, Produto, Base
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ParserProduto():
    def __init__(self, arquivo: io.StringIO) -> None:
        self.carregar_arquivo(arquivo)
    
    def carregar_arquivo(self, arquivo:io.StringIO):
        self.df = pd.read_csv(
            arquivo, 
            sep=";", 
            usecols=["Código", "Nome"],
            encoding='cp1252'
            )
        # elimina linhas sem código ou sem nome
        self.df = self.df.dropna()
        
if __name__ == "__main__":
    with open("produtos.csv", "r", encoding="cp1252") as arquivo:
        
        p = ParserProduto(arquivo)
        engine = create_engine('sqlite:///banco.sqlite3')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)
        Produto.gravar_banco(session, p.df)