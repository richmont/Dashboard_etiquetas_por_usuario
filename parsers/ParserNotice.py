import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Dashboard_etiquetas_por_usuario.models import Usuario, Relatorio
import logging
import pandas as pd
#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParserNoticeXML():
    class exc():
        class ElementoAusente(Exception):
            pass

    def obter_matricula(self):
        _ = self._raiz.find("notificacao").find("produto").get("usuario")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Matricula ausente")
    
    def obter_formato(self):
        _ = self._raiz.find("notificacao").find("produto").get("tipo_etiqueta")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Formato ausente")
    
    def obter_tipo(self):
        _ = self._raiz.find("notificacao").get("tipo")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Tipo ausente")
        
    def obter_quantidade(self):
        _ = self._raiz.find("notificacao").find("produto").get("quantidade")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Quantidade ausente")
    
    def obter_data(self) -> datetime:
        data_string = self._raiz.get("data_hora")
        _ = datetime.strptime(data_string, "%d/%m/%Y %H:%M:%S")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Data ausente")
    
    def obter_cod_produto(self) -> int:
        _ = self._raiz.find("notificacao").find("produto").get("sku")
        if _ is not None:
            return _
        else:
            raise ParserNoticeXML.exc.ElementoAusente("Código do produto ausente")
            
    
    def interpretar_relatorio(self):
        resultado = Relatorio.existe(self._session, self._nome_arquivo)
        if resultado:
            logger.info(f"Relatório de nome {self._nome_arquivo} já existe no banco, ignorando")
        else:
            self.carregar_arquivo()
            # Obtém os dados do relatório
            tipo = self.obter_tipo()
            
            # caso seja papeleta, omite o formato
            if tipo == "papeleta":
                matricula = self.obter_matricula()
                data = self.obter_data()
                quantidade = self.obter_quantidade()
                cod_produto = self.obter_cod_produto()

                # gera um objeto para uso do sqlalchemy
                logger.debug(
                    f"Relatório tipo {tipo} detectado, pronto para gravar: Matrícula {matricula}, data {data}, nome do arquivo {self._nome_arquivo}"
                    )
                dict_relatorio = {
                    "matricula": matricula,
                    "tipo": tipo,
                    "data": data,
                    "quantidade":quantidade,
                    "nome_arquivo": self._nome_arquivo,
                    "cod_produto":cod_produto
                }
                return dict_relatorio
                

            # caso seja etiqueta, obtém o formato e guarda
            elif tipo == "etiqueta":
                matricula = self.obter_matricula()
                data = self.obter_data()
                quantidade = self.obter_quantidade()
                cod_produto = self.obter_cod_produto()
                formato = self.obter_formato()
                
                # gera um objeto para uso do sqlalchemy
                logger.debug(
                    f"Relatório tipo {formato} detectado, pronto para gravar: Matrícula {matricula}, data {data}, nome do arquivo {self._nome_arquivo}"
                    )
                dict_relatorio = {
                    "matricula": matricula,
                    "tipo": formato,
                    "data": data,
                    "quantidade":quantidade,
                    "nome_arquivo": self._nome_arquivo,
                    "cod_produto":cod_produto
                }
                return dict_relatorio
    
    def __init__(self, session, conteudo_arquivo:list, nome_arquivo:str) -> None:
        self._session = session
        self._conteudo_arquivo = conteudo_arquivo
        self._nome_arquivo = nome_arquivo
        
            
    def carregar_arquivo(self) -> None:
        self._raiz = ET.fromstring(self._conteudo_arquivo)

    

if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3')
    Session = sessionmaker(bind=engine)
    session = Session()
    with open("exemplo.xml", "r") as arquivo:
        a = arquivo.readlines()
        conteudo_arquivo = ' '.join(a)
        p = ParserNoticeXML(session, conteudo_arquivo, "exemplo.xml")
        dict_relatorio = p.interpretar_relatorio()
        print(dict_relatorio)
        
        session.close()

        
        
        
    
    
    
    