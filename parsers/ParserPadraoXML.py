import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from Dashboard_etiquetas_por_usuario.models import Usuario, Relatorio

class ParserPadraoXML():
        
    def obter_matricula(self):
        return self._raiz.find("matricula").text
        
    def obter_tipo(self):
        return self._raiz.find("tipo").text
        
    def obter_quantidade(self):
        return self._raiz.find("quantidade").text
    
    def obter_data(self)-> datetime:
        data_string = self._raiz.find("data-geracao").text
        return datetime.strptime(data_string, "%d/%m/%Y %H:%M:%S")
        
    def __init__(self, session, conteudo_arquivo:list, nome_arquivo:str) -> None:
        self._session = session
        self._conteudo_arquivo = conteudo_arquivo
        
        self.carregar_arquivo()
        
        # Obtém os dados do relatório
        matricula = self.obter_matricula()
        tipo = self.obter_tipo()
        data = self.obter_data()
        quantidade = self.obter_quantidade()
        
        # gera um objeto para uso do sqlalchemy
        self._relatorio_final = Relatorio(
            matricula = matricula,
            tipo = tipo,
            data = data,
            quantidade = quantidade,
            nome_arquivo=nome_arquivo
        )
        # grava no banco usando a sessão informada
        self.gravar_relatorio()
        
    
    def carregar_arquivo(self) -> None:
        self._raiz = ET.fromstring(self._conteudo_arquivo)
        
        
    def gravar_relatorio(self):
        self._session.add(self._relatorio_final)
        self._session.commit()

if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    with open("exemplo_relatorio.xml", "r") as arquivo:
        a = arquivo.readlines()
        conteudo_arquivo = ' '.join(a)
        p = ParserPadraoXML(session, conteudo_arquivo, "exemplo_relatorio.xml")
        session.close()
        
        
        
        
    
    
    
    