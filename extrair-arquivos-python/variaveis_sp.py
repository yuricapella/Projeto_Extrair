import json
import re

estados = {
    "Acre": "AC", "Alagoas": "AL", "Amapá": "AP", "Amazonas": "AM", "Bahia": "BA", 
    "Ceará": "CE", "Distrito Federal": "DF", "Espírito Santo": "ES", "Goiás": "GO",
    "Maranhão": "MA", "Mato Grosso": "MT", "Mato Grosso do Sul": "MS", "Minas Gerais": "MG",
    "Pará": "PA", "Paraíba": "PB", "Paraná": "PR", "Pernambuco": "PE", "Piauí": "PI",
    "Rio de Janeiro": "RJ", "Rio Grande do Norte": "RN", "Rio Grande do Sul": "RS",
    "Rondônia": "RO", "Roraima": "RR", "Santa Catarina": "SC", "São Paulo": "SP",
    "Sergipe": "SE", "Tocantins": "TO"
}

with open("cadastro_sp.json", "r") as f:
    config_data = json.load(f)

cadastro = config_data.get("cadastro", "")
cadastro_parts = cadastro.split('\n')

cadastros = cadastros = re.split(r'(?<=NF-e)\n\n', cadastro)


CADASTROS_NUMBER = len(cadastros)

USERNAME = config_data.get("username", "")
PASSWORD = config_data.get("password", "")

dicionario_cadastros = {}

  
for i, cadastro in enumerate(cadastros, start=1):
    
    cadastro_info = {}
    print(i)
    print(f"Processing Cadastro {i}:")
    # print(f"cadastro: {cadastro}")
    cadastro_parts = cadastro.strip().split('\n')
    print(f"cadastro_parts: {cadastro_parts}")
    match = re.search(r'^(.*?)-', cadastro_parts[1])
    if match:
        NOME = match.group(1)

    match = re.search(r'CPF (\d+)', cadastro_parts[1])
    if match:
        CPF_CNPJ = match.group(1)
    
    match = re.search(r'CEP:(.*?),', cadastro_parts[2])
    if match:
        CEP = match.group(1).strip()
    
    match = re.search(r',(.*?)- CEP:', cadastro_parts[2])
    if match:
        CIDADE = match.group(1).strip()
    
    match = re.search(r'- CEP:(.*?),(.*?)$', cadastro_parts[2])
    if match:
        ESTADO = match.group(2).strip()
        SIGLA_ESTADO = estados.get(ESTADO)
    
    match = re.search(r'^(.*?)(\d+)', cadastro_parts[2])
    if match:
        RUA = match.group(1).strip()
    
    print(NOME)
    print(CPF_CNPJ)
    print(CEP)
    print(CIDADE)
    print(SIGLA_ESTADO)
    print(RUA)
    print(NUMERO)
    print(COMPLEMENTO)
    print(PRODUTO)
    print(UN)
    print(QUANTIDADE)
    print(PRECOUNITARIO)
    print(NCM)
    BAIRRO = 'NULL'
    UN = 'UN'
    NCM = '85176262'
    
    

    cadastro_info = {
        "username": USERNAME,
        "password": PASSWORD,
        "nome": NOME,
        "cpf_cnpj": CPF_CNPJ,
        "cep": CEP,
        "cidade": CIDADE,
        "sigla_estado": SIGLA_ESTADO,
        "bairro": BAIRRO,
        "rua": RUA,
        "numero": NUMERO,
        "complemento": COMPLEMENTO,
        "produto": PRODUTO,
        "un": UN,
        "quantidade": QUANTIDADE,
        "preco_unitario": PRECOUNITARIO,
        "ncm": NCM
    }

    # dicionario_cadastros[f"Cadastro_{i}"] = cadastro_info
    
print("-------------------------") 
# print(json.dumps(dicionario_cadastros, indent=4, ensure_ascii=False))
