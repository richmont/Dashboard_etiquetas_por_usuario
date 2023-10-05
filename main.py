from SSH import ClienteSSH
from parsers.ParserAtacadao import ParserAtacadaoXML
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

c = ClienteSSH("srvsave238","/fs1/rub/notice/processado","notice_05-10-2023","", "")
lista_nomes_relatorios = c.obter_nome_relatorio()


engine = create_engine('sqlite:///banco.sqlite3', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
for nome_relatorio in lista_nomes_relatorios:
    conteudo_relatorio_lst = c.obter_conteudo_relatorio(nome_relatorio)
    conteudo_relatorio = "".join(conteudo_relatorio_lst)
    p = ParserAtacadaoXML(session, conteudo_relatorio, nome_relatorio)
session.commit()
session.close() 