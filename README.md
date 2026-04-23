# TCC — Sistema de Validação de Pedidos de Entrega

Sistema que processa pedidos de entrega a partir de um arquivo CSV, realizando validações de endereço, datas e condições climáticas, e armazenando os resultados em um banco de dados MySQL.

## Funcionalidades

- **Validação de CEP**: Normaliza o CEP de destino e busca dados do endereço via [ViaCEP](https://viacep.com.br/)
- **Mapeamento de município**: Obtém o código IBGE do município para definir zona de atendimento/SLA
- **Validação de data**: Se a data de entrega cair em feriado, avança automaticamente para o próximo dia útil
- **Verificação climática**: Consulta o INPE para identificar risco de chuva intensa na data de entrega

## Pré-requisitos

- Python 3.8 ou superior
- MySQL Server rodando localmente

## Instalação

### 1. Clone o repositório

```bash
git clone <url-do-repositorio>
cd TCC
```

### 2. (Opcional) Crie e ative um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com os valores corretos:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=app
```

> O arquivo `.env` está listado no `.gitignore` e nunca deve ser versionado.

## Configuração do banco de dados

### 1. Instale o MySQL

Baixe e instale o [MySQL Community Server](https://dev.mysql.com/downloads/mysql/). Durante a instalação, defina uma senha para o usuário `root`.

### 2. Acesse o MySQL pelo terminal

```bash
mysql -u root -p
```

Digite a senha quando solicitado. Você verá o prompt `mysql>`.

### 3. Crie o banco de dados e selecione-o

```sql
CREATE DATABASE app;
USE app;
```

### 4. Crie as tabelas

Execute os comandos abaixo em sequência:

```sql
CREATE TABLE orders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    cep             VARCHAR(10),
    requested_date  DATE,
    delivery_date   DATE,
    logradouro      VARCHAR(255),
    bairro          VARCHAR(255),
    localidade      VARCHAR(255),
    uf              VARCHAR(2),
    ibge_code       VARCHAR(10),
    ddd             VARCHAR(3),
    weather_tag     VARCHAR(255),
    order_status    VARCHAR(50)
);

CREATE TABLE errors (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    order_id       INT,
    error_details  TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE city_inpe_code (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    city       VARCHAR(255),
    uf         VARCHAR(2),
    inpe_code  VARCHAR(20)
);

CREATE TABLE weather_code (
    id                        INT AUTO_INCREMENT PRIMARY KEY,
    weather_code              VARCHAR(10),
    weather_code_description  VARCHAR(255)
);
```

### 5. Verifique as tabelas criadas

```sql
SHOW TABLES;
```

Você deve ver as quatro tabelas: `orders`, `errors`, `city_inpe_code` e `weather_code`.

### 6. Saia do MySQL

```sql
EXIT;
```

### Variáveis de ambiente

As credenciais são lidas do arquivo `.env` na raiz do projeto. As variáveis disponíveis são:

| Variável      | Descrição              |
|---------------|------------------------|
| `DB_HOST`     | Endereço do servidor   |
| `DB_USER`     | Usuário do banco       |
| `DB_PASSWORD` | Senha do banco         |
| `DB_NAME`     | Nome do banco de dados |

> Altere os valores no `.env` conforme a senha definida na instalação do MySQL.

## Arquivo de entrada

Coloque o arquivo CSV com os pedidos na pasta `input/` com o nome `test.csv`. Um arquivo de exemplo já está disponível nessa pasta.

## Executando o projeto

A partir da raiz do projeto, execute um dos comandos abaixo dependendo da versão desejada:

**Versão monolítica:**
```bash
python -m monolith_version.app
```

**Versão com classes (refatorada):**
```bash
python -m monolith_with_classes_version.app
```

## Serviços externos utilizados

| Serviço | Finalidade | Autenticação |
|---------|-----------|--------------|
| [ViaCEP](https://viacep.com.br/) | Validação de CEP e dados de endereço | Não necessária |
| [BrasilAPI](https://brasilapi.com.br/) | Consulta de feriados nacionais | Não necessária |
| INPE | Previsão do tempo por município | Não necessária |
