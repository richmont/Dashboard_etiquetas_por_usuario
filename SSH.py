from typing import Type
import paramiko
import logging
class ClienteSSH():
    def __init__(self, 
                 servidor: str, 
                 caminho_arquivo: str, 
                 prefixo_arquivo: str, 
                 usuario:str, 
                 senha:str
                 ):
        self._servidor = servidor
        self._caminho_arquivo = caminho_arquivo
        self._prefixo_arquivo = prefixo_arquivo
        self._usuario = usuario
        self._senha = senha
        self._cliente = paramiko.SSHClient()
        self._cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conectar_servidor()

    def conectar_servidor(self) -> None:
        """Realiza a conexão SSH com o servidor

        Raises:
            SSHErros.LoginFalhouSSH: Verifique login e senha no arquivo env

        """
        try:
            self._cliente.connect(hostname=self._servidor,username=self._usuario,password=self._senha)
        except paramiko.ssh_exception.AuthenticationException:
            raise SSHErros.LoginFalhouSSH("Verifique o login e senha no arquivo env (conf/.env)")
        

    def obter_conteudo_relatorio(self, nome_relatorio:str) -> list:
        """Abre um cliente SFTP com o servidor e obtém o conteúdo do arquivo de relatório

        Args:
            caminho_arquivo (str): caminho onde fica o arquivo a ser obtido

        Raises:
            SSHErros.ArquivoNaoEncontrado

        Returns:
            list: lista de strings com o texto do arquivo
        """
        conteudo_relatorio = list()
        try:
            with self._cliente.open_sftp() as sftp:
                logging.info(f"Trabalhando com o arquivo {nome_relatorio}")
                with sftp.open(f"{nome_relatorio}",'r') as relatorio: # abre o arquivo via sftp
                    for x in relatorio.readlines(): # armazena cada linha do arquivo aberto em uma lista
                        conteudo_relatorio.append(x.strip("\n"))
            return conteudo_relatorio
        except FileNotFoundError:
            raise SSHErros.ArquivoNaoEncontrado(f"Arquivo de relatório não encontrado: {nome_relatorio} no caminho {caminho_arquivo}")

    def obter_nome_relatorio(self) -> str:
        """Lista os arquivos no diretório de relatórios ordenando pelo mais antigo para o mais novo, filtra o prefixo do relatório
        incluir exceções caso o arquivo não seja localizado
        Returns:
            str: nome do arquivo do relatório
        """
        stdin,stdout,stderr=self._cliente.exec_command(f'ls -tr {self._caminho_arquivo} | grep {self._prefixo_arquivo}')
        logging.error(stderr.readlines())
        """
        Método original retornava apenas a primeira linha
        agora é necessário retornar todas as correspondências
        return str(stdout.readlines()[0].strip("\n")) # retorna o primeiro elemento da lista, elimina quebras de linha
        """
        lista_nomes_relatorio = stdout.readlines()
        # remove caracteres de fim de linha \n usando um lambda na lista
        # aplica o caminho completo do arquivo diretamente no nome
        lista_sem_quebra_linha = list(map(lambda x: x.strip("\n"), lista_nomes_relatorio))
        return list(map(lambda x: f"{self._caminho_arquivo}/{x}", lista_sem_quebra_linha))
class SSHErros():
    
    class LoginFalhouSSH(Exception):
        pass
    class ArquivoNaoEncontrado(Exception):
        pass

if __name__ == '__main__':
    pass
    