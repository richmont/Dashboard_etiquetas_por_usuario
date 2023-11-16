import xml.etree.ElementTree as ET
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from Dashboard_etiquetas_por_usuario.models import Usuario, Relatorio
import logging
#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParserAtacadaoXML():

    def obter_matricula(self):
        return self._raiz.find("notificacao").find("produto").get("usuario")
    
    def obter_formato(self):
        return self._raiz.find("notificacao").find("produto").get("tipo_etiqueta")
    
    def obter_tipo(self):
        return self._raiz.find("notificacao").get("tipo")
        
    def obter_quantidade(self):
        return self._raiz.find("notificacao").find("produto").get("quantidade")
    
    def obter_data(self) -> datetime:
        data_string = self._raiz.get("data_hora")
        return datetime.strptime(data_string, "%d/%m/%Y %H:%M:%S")
    
    def obter_cod_produto(self) -> int:
        return self._raiz.find("notificacao").find("produto").get("sku")
    
    def __init__(self, session, conteudo_arquivo:list, nome_arquivo:str) -> None:
        self._session = session
        self._conteudo_arquivo = conteudo_arquivo
        resultado = self._session.query(Relatorio).filter(Relatorio.nome_arquivo == nome_arquivo).first()
        if resultado:
            logger.info(f"Relatório de nome {nome_arquivo} já existe no banco, ignorando")
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
                    f"Relatório tipo {tipo} detectado, pronto para gravar: Matrícula {matricula}, data {data}, nome do arquivo {nome_arquivo}"
                    )
                self._relatorio_final = Relatorio(
                    matricula = matricula,
                    tipo = tipo,
                    data = data,
                    quantidade = quantidade,
                    nome_arquivo=nome_arquivo,
                    cod_produto=cod_produto,
                )
                
                # grava no banco usando a sessão informada
                self.gravar_relatorio()

            # caso seja etiqueta, obtém o formato e guarda
            elif tipo == "etiqueta":
                matricula = self.obter_matricula()
                data = self.obter_data()
                quantidade = self.obter_quantidade()
                cod_produto = self.obter_cod_produto()
                formato = self.obter_formato()
                
                # gera um objeto para uso do sqlalchemy
                logger.debug(
                    f"Relatório tipo {formato} detectado, pronto para gravar: Matrícula {matricula}, data {data}, nome do arquivo {nome_arquivo}"
                    )
                self._relatorio_final = Relatorio(
                    matricula = matricula,
                    # o tipo obviamente será etiqueta, então armazena se é X ou C no banco
                    tipo = formato,
                    data = data,
                    quantidade = quantidade,
                    nome_arquivo=nome_arquivo,
                    cod_produto=cod_produto,
                )
                
                # grava no banco usando a sessão informada
                self.gravar_relatorio()
            
    def carregar_arquivo(self) -> None:
        self._raiz = ET.fromstring(self._conteudo_arquivo)

    def gravar_relatorio(self):
        logger.debug("Gravando relatório no banco")
        self._session.add(self._relatorio_final)
        # commit por transação desabilitado
        #self._session.commit()

if __name__ == "__main__":
    engine = create_engine('sqlite:///banco.sqlite3')
    Session = sessionmaker(bind=engine)
    session = Session()
    with open("exemplo.xml", "r") as arquivo:
        a = arquivo.readlines()
        conteudo_arquivo = ' '.join(a)
        p = ParserAtacadaoXML(session, conteudo_arquivo, "exemplo.xml")
        session.commit()
        session.close()

        
        
        
    
    
    
    