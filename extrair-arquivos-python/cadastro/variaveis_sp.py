import json
import re

def carregar_configuracao(nome_arquivo="cadastro_sp.json"):
    with open(nome_arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def separar_cadastros(dados):
    blocos = re.split(r'\n_{10,}\n', dados)
    return [bloco.strip() for bloco in blocos if bloco.strip()]

def extrair_dados_cadastro(bloco):
    dados = {}
    for linha in bloco.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if ':' in linha:
            chave, valor = linha.split(':', 1)
            chave = chave.strip().lower()
            valor = valor.strip()
            
            if chave in ["cpf", "cnpj"]:
                valor = re.sub(r"[^\d]", "", valor)
                chave = "cpf_cnpj"

            elif chave == "inscrição estadual":
                dados["inscricao_estadual"] = valor

            elif chave == "valor unitario":
                chave = "valor"

            dados[chave] = valor
    return dados

def extrair_rua_numero(endereco):
    endereco = endereco.strip()

    if "-" in endereco:
        rua = endereco.strip()

        # Encontra todos os números antes do hífen
        numeros = re.findall(r'(\d+)(?=\s*-)', endereco)
        
        if numeros:
            # Pega o último número encontrado antes do hífen
            numero = numeros[-1]
        else:
            numero = "SN"

        return rua, numero

    # Caso não haja hífen, usa a lógica padrão
    tokens = endereco.split()
    if tokens:
        last_token = tokens[-1].rstrip(",;:.")
    else:
        last_token = ""

    # Se o último token for "SN", consideramos como o número
    if tokens and last_token.upper() == "SN":
        rua = " ".join(tokens[:-1]).strip()
        return rua if rua else None, "SN"

    # Procura o último token que seja apenas dígitos
    for i in range(len(tokens) - 1, -1, -1):
        if tokens[i].isdigit():
            rua = " ".join(tokens[:i]).strip()
            return rua if rua else None, tokens[i]

    return endereco, "SN"

def limpar_valor(valor):
    if valor:
        valor = re.sub(r'[^\d,]', '', valor)
    return valor

def limpar_cnpj(cnpj):
    if cnpj:
        cnpj = re.sub(r'[^\d]', '', cnpj)
    return cnpj

def montar_cadastro(dados_cadastro, username, password):
    nome = dados_cadastro.get("nome")
    cpf_cnpj = dados_cadastro.get("cpf_cnpj")
    inscricao_estadual = dados_cadastro.get("inscricao_estadual", '')
    endereco_raw = dados_cadastro.get("endereço")
    cep = dados_cadastro.get("cep")
    estado = dados_cadastro.get("estado")
    cidade = dados_cadastro.get("cidade")
    uf = dados_cadastro.get("uf")
    produto = dados_cadastro.get("produto")
    quantidade = dados_cadastro.get("quantidade", "1")
    valor = limpar_valor(dados_cadastro.get("valor"))
    ncm = dados_cadastro.get("ncm")
    un = dados_cadastro.get("un")
    bairro = dados_cadastro.get("bairro", "null")

    rua, numero = (None, "SN")
    if endereco_raw:
        rua, numero = extrair_rua_numero(endereco_raw)


    cadastro_final = {
        "username": username,
        "password": password,
        "nome": nome,
        "cpf_cnpj": cpf_cnpj,
        "inscricao_estadual": inscricao_estadual if inscricao_estadual else None,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "uf": uf,
        "bairro": bairro if bairro else None,
        "rua": rua,
        "numero": numero,
        "produto": produto,
        "un": un if un else None,
        "quantidade": quantidade,
        "valor": valor,
        "ncm": ncm
    }
    return cadastro_final

def get_variables():
    # Carrega a configuração e os dados do arquivo JSON
    config = carregar_configuracao("cadastro/cadastro_sp.json")
    username = config.get("username", "")
    password = config.get("password", "")
    dados_completos = config.get("cadastro", "")

    # Separa e processa os cadastros
    blocos_cadastro = separar_cadastros(dados_completos)
    cadastros = {}
    for i, bloco in enumerate(blocos_cadastro, start=1):
        dados_cadastro = extrair_dados_cadastro(bloco)
        cadastro = montar_cadastro(dados_cadastro, username, password)
        cadastros[f"Cadastro_{i}"] = cadastro

    return {
        "USERNAME": username,
        "PASSWORD": password,
        "dicionario_cadastros": cadastros,
        "CADASTROS_NUMBER": len(blocos_cadastro)
    }

if __name__ == "__main__":
    # Executa para teste local e imprime as variáveis
    variables = get_variables()
    print(json.dumps(variables, indent=4, ensure_ascii=False))
