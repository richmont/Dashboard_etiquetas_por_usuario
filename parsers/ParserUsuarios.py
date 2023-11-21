import io
import pandas as pd
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Dashboard_etiquetas_por_usuario.models import Usuario, Relatorio, Base

logger = logging.getLogger(__name__)

class ParserUsuarios():
    def __init__(self, arquivo: io.StringIO) -> None:
        self.carregar_arquivo(arquivo)
    
    def carregar_arquivo(self, arquivo:io.StringIO):
        self.df = pd.read_csv(
            arquivo, 
            sep=";", 
            usecols=["Nome", "Username", "Código"],
            encoding='cp1252'
            )
        # elimina linhas sem código ou sem nome
        self.df = self.df.dropna()
        
if __name__ == "__main__":
    with open("usuarios.csv", "r", encoding="cp1252") as arquivo:
        
        p = ParserUsuarios(arquivo)
        engine = create_engine('sqlite:///banco.sqlite3')
        Session = sessionmaker(bind=engine)
        session = Session()
        Base.metadata.create_all(engine)    
        Usuario.gravar_banco(session, p.df)
        