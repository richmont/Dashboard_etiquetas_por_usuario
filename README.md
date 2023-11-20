# Dashboard_etiquetas_por_usuario
Software que analisa logs de emissão de etiquetas e gera uma dashboard com relatório de quantidade e tipo de etiqueta impressa por colaboradores.  

# Requisitos
- Python 3.9 ou superior
- MySQL/MariaDB 10.5 ou superior
- cliente Git
- Familiaridade com configuração de servidor de banco de dados e ambientes virtuais python

# Instalação

### Criando o ambiente virtual
No exemplo vamos guardar a instalação na pasta Documents dentro da pasta do usuário padrão

```cmd
cd Documents
python -m venv dashboard_etiquetas
cd dashboard_etiquetas
```
### Windows
```cmd
Scripts\activate
```
Você notará que o começo do terminal mudou:
(dashboard_etiquetas) C:\Users\Fulano

### Linux
```bash
source bin/activate
```
Você notará que o começo do terminal mudou:
(dashboard_etiquetas) usuario@maquina $

### Baixando o projeto e dependências
```cmd
git clone https://github.com/richmont/Dashboard_etiquetas_por_usuario
cd Dashboard_etiquetas_por_usuario
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```
Aguarde a instalação completar
### Definindo variáveis de ambiente para usar o sistema

### Windows
```cmd
set SRV_IP=192.168.0.1
```
IP ou hostname do servidor que guarda os logs de etiquetas
```cmd
set SRV_RELATORIO_PASTA=/var/log/xml
```
Diretório que guarda os XML de cada etiqueta gerada

```cmd
set SSH_LOGIN=usuario
```
Usuário para acesso SSH do servidor
```cmd
set SSH_PWD=senhadificil
```
Senha para acesso SSH do servidor

```cmd
set DATABASE_URL=mysql://loginbanco:senhabanco@127.0.0.1:3306/dashboard
```
URL de acesso ao banco de dados, segue o padrão:

```
mysql://<login para o banco de dados>:<senha do servidor do banco>@<Endereço do servidor>:<porta do servidor>/<nome do banco>
```
### Linux
Troque "set" por "export"

Você deve estar no diretório Dashboard_etiquetas_por_usuario com o ambiente virtual ativado.  

```cmd
streamlit run dashboard.py
```
A dashboard iniciará no seu endereço local, na porta 8501. Acesse do navegador:  
http://localhost:8501