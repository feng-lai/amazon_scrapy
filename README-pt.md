
[日本語](README-jp.md) | [العربية](README-ar.md) | [Português](README-pt.md) | [Español](README-es.md) | [English](README-en.md)

# Documentação do Projeto de Scraping da Amazon (Português)

## Visão Geral do Projeto

Este projeto foi desenvolvido para extrair informações de produtos do site da Amazon, processar os dados e enviá-los para um servidor específico. Ele utiliza o Selenium para automação de navegação e o BeautifulSoup para análise de HTML. O projeto é composto por diversos scripts Python que realizam tarefas como scraping de dados, processamento de imagens e upload de informações.

## Descrição dos Arquivos

### change.py

- **Objetivo**: Baixa imagens de URLs fornecidas, envia para o servidor e atualiza o arquivo JSON com os novos links.
- **Funções**:
  - Fazer download das imagens a partir de URLs.
  - Enviar as imagens ao servidor e obter novos links.
  - Atualizar o JSON com os novos links de imagem.
- **Dependências**: `requests`, `pandas`, `tqdm`, `BeautifulSoup`, `os`

### extract.py

- **Objetivo**: Extrai links de imagens de um arquivo JSON e os salva em um arquivo de texto.
- **Funções**:
  - Ler um arquivo JSON com informações de produtos.
  - Utilizar expressões regulares para extrair os URLs das imagens.
  - Filtrar links indesejados com base em palavras-chave.
  - Salvar os links válidos em um arquivo `.txt`.
- **Dependências**: `json`, `re`, `os`

### product_info.json & updated_product_info.json

- **Conteúdo**: Arquivos JSON com dados dos produtos, como preço, nome, imagens, descrição e atributos.
- **Estrutura**:
  - `price`: Preço do produto.
  - `itm_name`: Nome do produto.
  - `img1` a `img8`: URLs das imagens do produto.
  - `itm_dsc`: Descrição do produto em formato HTML.
  - `cat_id` & `s_id`: IDs de categoria e da loja.
  - `attr`: Atributos como cor, tamanho, etc.

### shop.py

- **Objetivo**: Faz scraping de informações da página de mais vendidos da Amazon.
- **Funções**:
  - Acessar a página de best sellers.
  - Extrair links dos produtos, preços e títulos.
  - Obter detalhes como vendedor, avaliação e descrição.
  - Salvar os dados coletados em arquivo CSV.
- **Dependências**: `selenium`, `webdriver_manager`, `pandas`, `time`, `os`

### upload.py

- **Objetivo**: Envia os dados de produtos para o servidor a partir de um arquivo JSON.
- **Funções**:
  - Ler o JSON com os dados.
  - Realizar requisições POST para o servidor.
  - Lidar com as respostas e eventuais erros.
- **Dependências**: `requests`, `json`, `time`

### Outros Scripts (size_and_color.py, amazon_item.py, etc.)

- **Objetivo**: Coletar dados de produtos em diferentes páginas da Amazon.
- **Funções**:
  - Extrair título, preço, imagens, descrição e atributos.
  - Suportar variações de cor e tamanho.
  - Armazenar os resultados em arquivos JSON.
- **Dependências**: `selenium`, `webdriver_manager`, `lxml`, `BeautifulSoup`, `time`, `os`, `json`, `tqdm`

## Instruções de Execução e Implantação

### Configuração do Ambiente

1. **Instalar o Python**: Verifique se você tem o Python 3.x instalado.
2. **Instalar os pacotes necessários**:
   ```bash
   pip install requests pandas tqdm beautifulsoup4 selenium lxml


3. **WebDriver**: Baixe o WebDriver compatível com seu navegador (por exemplo, EdgeDriver) e adicione ao PATH do sistema.

### Executando os Scripts

#### change.py

```bash
python change.py
```

#### extract.py

```bash
python extract.py
```

#### shop.py

```bash
python shop.py
```

#### upload.py

```bash
python upload.py
```

#### Outros scripts

```bash
python nome_do_script.py
```

## Observações

* Alguns scripts possuem URLs e XPaths definidos diretamente no código. Verifique se há mudanças no site da Amazon.
* Use os scripts de maneira ética e em conformidade com os termos de uso da Amazon e leis locais.
* Consulte e respeite o arquivo robots.txt da Amazon ao realizar scraping.


