import json
import os
import tempfile
from pathlib import Path


ARQUIVO_DADOS = Path(__file__).resolve().parent / "dados" / "corrida.json"


def solicitar_inteiro(mensagem, minimo=None, opcoes=None):
    """Solicita um número inteiro até que ele atenda às regras informadas."""
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")
            continue

        if minimo is not None and valor < minimo:
            print(f"Erro: o valor mínimo permitido é {minimo}.")
            continue
        if opcoes is not None and valor not in opcoes:
            opcoes_texto = " ou ".join(str(opcao) for opcao in opcoes)
            print(f"Opção inválida. Escolha {opcoes_texto}.")
            continue
        return valor


def cadastrar_corredor(corredores):
    """Adiciona um corredor à lista de inscrições da corrida."""
    nome = input("Digite o nome do corredor: ").strip()
    while not nome:
        print("O nome não pode ficar vazio.")
        nome = input("Digite o nome do corredor: ").strip()

    idade = solicitar_inteiro(
        "Digite a idade do corredor: ", minimo=16
    )
    distancia = solicitar_inteiro(
        "Digite a distância da corrida (5 ou 10 km): ", opcoes=(5, 10)
    )
    lote = solicitar_inteiro(
        "Digite o lote de inscrição (1 ou 2): ", opcoes=(1, 2)
    )

    valor_inscricao = calcular_valor_inscricao(idade, distancia, lote)
    categoria = determinar_categoria(idade)
    codigo_corredor = gerar_codigo_corredor(nome, idade)
    corredor = {
        "numero": max((item["numero"] for item in corredores), default=0) + 1,
        "nome": nome,
        "idade": idade,
        "distancia": distancia,
        "lote": lote,
        "valor_inscricao": valor_inscricao,
        "categoria": categoria,
        "codigo": codigo_corredor,
        "tempo_chegada": None,
    }
    corredores.append(corredor)

    print("\nResumo da Inscrição:")
    print(f"Número da inscrição: {corredor['numero']}")
    print(f"Nome: {nome}")
    print(f"Idade: {idade}")
    print(f"Distância: {distancia} km")
    print(f"Lote: {lote}")
    print(f"Valor da Inscrição: R$ {valor_inscricao:.2f}")
    print(f"Categoria: {categoria}")
    print(f"Código do Corredor: {codigo_corredor}")
    return corredor


def consultar_corredor(corredores):
    """Lista os inscritos e consulta os dados de uma inscrição pelo número."""
    if not corredores:
        print("Nenhum corredor cadastrado nesta corrida.")
        return None

    print("\nCorredores cadastrados:")
    for corredor in corredores:
        print(f"{corredor['numero']} - {corredor['nome']} | {corredor['distancia']} km")
    numero = solicitar_inteiro("Número da inscrição para consultar (0 para voltar): ", minimo=0)
    if numero == 0:
        return None
    corredor = next((item for item in corredores if item["numero"] == numero), None)
    if corredor is None:
        print("Inscrição não encontrada.")
        return None

    print("\nDados do corredor:")
    print(f"Número da inscrição: {corredor['numero']}")
    print(f"Nome: {corredor['nome']}")
    print(f"Idade: {corredor['idade']}")
    print(f"Distância: {corredor['distancia']} km")
    print(f"Lote: {corredor['lote']}")
    print(f"Valor da Inscrição: R$ {corredor['valor_inscricao']:.2f}")
    print(f"Categoria: {corredor['categoria']}")
    print(f"Código do Corredor: {corredor['codigo']}")
    print(f"Tempo de chegada: {corredor.get('tempo_chegada') or 'pendente'}")
    return corredor


def registrar_tempo_chegada(corredores, numero_inscricao, tempo, substituir=False):
    """Registra o tempo de prova na inscrição selecionada pelo número."""
    if type(numero_inscricao) is not int or numero_inscricao < 1:
        raise ValueError("O número da inscrição deve ser um inteiro positivo.")
    corredor = next((item for item in corredores if item["numero"] == numero_inscricao), None)
    if corredor is None:
        raise ValueError("Inscrição não encontrada.")
    if corredor.get("tempo_chegada") is not None and not substituir:
        raise ValueError("Já existe um tempo de chegada. Confirme a substituição.")
    if not isinstance(tempo, str):
        raise ValueError("Informe o tempo no formato HH:MM:SS.")
    segundos = converter_tempo_segundos(tempo.strip())
    if segundos <= 0:
        raise ValueError("O tempo de chegada deve ser maior que zero.")
    horas, restante = divmod(segundos, 3600)
    minutos, segundos = divmod(restante, 60)
    corredor["tempo_chegada"] = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    return corredor


def calcular_valor_inscricao(idade, distancia, lote):
    """Calcula o valor da inscrição."""
    if lote == 1:
        valor = 80
    else:
        valor = 100

    if distancia == 10:
        valor += 20

    if idade >= 60:
        valor = valor / 2

    return valor
def determinar_categoria(idade):
    """Determina a categoria do corredor."""
    if idade <= 19:
        return "Juvenil"
    elif idade <= 39:
        return "Adulto"
    elif idade <= 59:
        return "Master"
    else:
        return "Veterano"
def gerar_codigo_corredor(nome, idade):
    """Gera o código de identificação do corredor."""
    partes_nome = nome.strip().split()

    primeiro_nome = partes_nome[0]
    ultimo_sobrenome = partes_nome[-1]

    codigo = primeiro_nome[:3] + ultimo_sobrenome[:3] + str(idade)

    return codigo.upper()

def converter_tempo_segundos(tempo):
    """Converte um tempo no formato HH:MM:SS para segundos."""
    if len(tempo) != 8 or tempo[2] != ":" or tempo[5] != ":":
        raise ValueError("Formato inválido. Use HH:MM:SS.")
    horas = tempo[:2]
    minutos = tempo[3:5]
    segundos = tempo[6:8]
    if not (horas.isdigit() and minutos.isdigit() and segundos.isdigit()):
        raise ValueError("O tempo deve conter apenas números e dois-pontos.")
    horas = int(horas)
    minutos = int(minutos)
    segundos = int(segundos)
    if minutos > 59 or segundos > 59:
        raise ValueError("Minutos e segundos devem estar entre 00 e 59.")
    return horas * 3600 + minutos * 60 + segundos

def calcular_pace(tempo_segundos, distancia):
    """Calcula o pace médio por quilômetro."""
    if distancia not in (5, 10):
        raise ValueError("A distância deve ser 5 ou 10 km.")
    if tempo_segundos < 0:
        raise ValueError("O tempo não pode ser negativo.")
    pace_segundos = tempo_segundos // distancia
    minutos = pace_segundos // 60
    segundos = pace_segundos % 60
    return f"{minutos}'{segundos:02d}\"/km"

def verificar_premiacao(idade, distancia, tempo_segundos):
    """Verifica se o corredor foi premiado conforme sua categoria."""
    if idade < 16:
        raise ValueError("O corredor deve ter pelo menos 16 anos.")
    if distancia not in (5, 10):
        raise ValueError("A distância deve ser 5 ou 10 km.")
    if tempo_segundos < 0:
        raise ValueError("O tempo não pode ser negativo.")
    categoria = determinar_categoria(idade)
    if categoria == "Juvenil" or categoria == "Master":
        limite_5km = 25 * 60
        limite_10km = 52 * 60
    elif categoria == "Adulto":
        limite_5km = 22 * 60
        limite_10km = 46 * 60
    else:
        limite_5km = 30 * 60
        limite_10km = 63 * 60
    if distancia == 5:
        limite = limite_5km
    else:
        limite = limite_10km
    return tempo_segundos <= limite


def consultar_resultado():
    """Solicita os dados de uma prova e exibe o resultado individual."""
    idade = solicitar_inteiro(
        "Digite a idade do corredor: ", minimo=16
    )
    distancia = solicitar_inteiro(
        "Digite a distância da corrida (5 ou 10 km): ", opcoes=(5, 10)
    )

    while True:
        tempo = input("Digite o tempo no formato HH:MM:SS: ").strip()
        try:
            tempo_segundos = converter_tempo_segundos(tempo)
        except ValueError as erro:
            print(f"Tempo inválido: {erro}")
            continue
        break

    pace = calcular_pace(tempo_segundos, distancia)
    premiado = verificar_premiacao(idade, distancia, tempo_segundos)
    categoria = determinar_categoria(idade)
    print("\nResultado do Corredor:")
    print(f"Categoria: {categoria}")
    print(f"Distância: {distancia} km")
    print(f"Tempo: {tempo}")
    print(f"Pace médio: {pace}")
    print(f"Premiado: {'Sim' if premiado else 'Não'}")
    return {
        "idade": idade,
        "distancia": distancia,
        "tempo": tempo,
        "tempo_segundos": tempo_segundos,
        "categoria": categoria,
        "pace": pace,
        "premiado": premiado,
    }


def validar_dados(dados):
    """Verifica cadastros, tempos de chegada e cálculos avulsos salvos."""
    if not isinstance(dados, dict) or set(dados) != {"versao", "corredores", "resultados"}:
        raise ValueError("O arquivo deve conter versao, corredores e resultados.")
    if type(dados["versao"]) is not int or dados["versao"] != 1:
        raise ValueError("Formato de armazenamento não suportado.")
    if not isinstance(dados["corredores"], list) or not isinstance(dados["resultados"], list):
        raise ValueError("Inscrições e resultados devem ser listas.")

    campos_corredor = {
        "numero", "nome", "idade", "distancia", "lote",
        "valor_inscricao", "categoria", "codigo",
    }
    numeros = set()
    for corredor in dados["corredores"]:
        if not isinstance(corredor, dict) or set(corredor) - {"tempo_chegada"} != campos_corredor:
            raise ValueError("Há uma inscrição com campos inválidos.")
        numero = corredor["numero"]
        if type(numero) is not int or numero < 1 or numero in numeros:
            raise ValueError("Os números de inscrição devem ser positivos e únicos.")
        numeros.add(numero)
        if not isinstance(corredor["nome"], str) or not corredor["nome"].strip():
            raise ValueError("Há uma inscrição sem nome válido.")
        if type(corredor["idade"]) is not int or corredor["idade"] < 16:
            raise ValueError("A idade mínima é 16 anos.")
        if type(corredor["distancia"]) is not int or corredor["distancia"] not in (5, 10):
            raise ValueError("A distância deve ser 5 ou 10 km.")
        if type(corredor["lote"]) is not int or corredor["lote"] not in (1, 2):
            raise ValueError("O lote deve ser 1 ou 2.")
        if corredor["categoria"] != determinar_categoria(corredor["idade"]):
            raise ValueError("A categoria da inscrição é inconsistente.")
        if corredor["codigo"] != gerar_codigo_corredor(corredor["nome"], corredor["idade"]):
            raise ValueError("O código da inscrição é inconsistente.")
        valor = corredor["valor_inscricao"]
        if type(valor) not in (int, float) or valor != calcular_valor_inscricao(
            corredor["idade"], corredor["distancia"], corredor["lote"],
        ):
            raise ValueError("O valor da inscrição é inconsistente.")
        tempo = corredor.get("tempo_chegada")
        if tempo is not None:
            if not isinstance(tempo, str) or converter_tempo_segundos(tempo) <= 0:
                raise ValueError("O tempo de chegada deve usar HH:MM:SS e ser maior que zero.")

    campos_resultado = {
        "idade", "distancia", "tempo", "tempo_segundos", "categoria", "pace", "premiado",
    }
    for resultado in dados["resultados"]:
        if not isinstance(resultado, dict) or set(resultado) != campos_resultado:
            raise ValueError("Há um resultado com campos inválidos.")
        if type(resultado["idade"]) is not int or resultado["idade"] < 16:
            raise ValueError("A idade do cálculo deve ser de pelo menos 16 anos.")
        if type(resultado["distancia"]) is not int or resultado["distancia"] not in (5, 10):
            raise ValueError("A distância do cálculo deve ser 5 ou 10 km.")
        if not isinstance(resultado["tempo"], str):
            raise ValueError("O tempo do cálculo deve usar HH:MM:SS.")
        segundos = converter_tempo_segundos(resultado["tempo"])
        if type(resultado["tempo_segundos"]) is not int or resultado["tempo_segundos"] != segundos:
            raise ValueError("O tempo do cálculo é inconsistente.")
        if resultado["categoria"] != determinar_categoria(resultado["idade"]):
            raise ValueError("A categoria do cálculo é inconsistente.")
        if resultado["pace"] != calcular_pace(segundos, resultado["distancia"]):
            raise ValueError("O pace do cálculo é inconsistente.")
        premiado = verificar_premiacao(resultado["idade"], resultado["distancia"], segundos)
        if type(resultado["premiado"]) is not bool or resultado["premiado"] != premiado:
            raise ValueError("A premiação do cálculo é inconsistente.")


def carregar_dados(caminho=ARQUIVO_DADOS):
    """Recupera inscrições e histórico; não substitui arquivos inválidos."""
    caminho = Path(caminho)
    try:
        with caminho.open(encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return {"versao": 1, "corredores": [], "resultados": []}
    except (json.JSONDecodeError, UnicodeError) as erro:
        raise ValueError(f"Arquivo de dados inválido: {caminho}.") from erro
    validar_dados(dados)
    return dados


def salvar_dados(dados, caminho=ARQUIVO_DADOS):
    """Grava o estado completo antes de substituir o arquivo anterior."""
    validar_dados(dados)
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=caminho.parent,
            prefix=f".{caminho.name}.", suffix=".tmp", delete=False,
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(dados, arquivo, ensure_ascii=False, indent=2, allow_nan=False)
            arquivo.write("\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())
        os.replace(temporario, caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


def consultar_historico_resultados(resultados):
    """Exibe os cálculos avulsos recuperados, sem vinculá-los a inscritos."""
    if not resultados:
        print("Nenhum resultado salvo.")
        return
    print("\nHistórico dos cálculos avulsos:")
    for numero, resultado in enumerate(resultados, start=1):
        print(f"\nCálculo #{numero} | Idade: {resultado['idade']}")
        print(f"Categoria: {resultado['categoria']} | Distância: {resultado['distancia']} km")
        print(f"Tempo: {resultado['tempo']} | Pace médio: {resultado['pace']}")
        print(f"Premiado: {'Sim' if resultado['premiado'] else 'Não'}")


def main():
    """Recupera e salva inscrições e cálculos, mantendo o resumo da sessão."""
    try:
        dados = carregar_dados(ARQUIVO_DADOS)
    except (OSError, ValueError) as erro:
        print(f"Não foi possível carregar os dados: {erro}")
        print("O arquivo existente foi preservado. Corrija-o antes de continuar.")
        return 1
    print(f"Inscrições recuperadas: {len(dados['corredores'])}")
    print(f"Resultados recuperados: {len(dados['resultados'])}")
    quantidade_inscricoes = 0
    total_arrecadado = 0

    while True:
        print("\n====================================")
        print(" CORRIDA NOTURNA DA PONTE ESTAIADA")
        print("====================================")
        print("1 - Fazer inscrição")
        print("2 - Calcular resultado")
        print("3 - Consultar corredores cadastrados")
        print("4 - Consultar resultados salvos")
        print("5 - Registrar tempo de chegada")
        print("0 - Sair")
        try:
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                atualizados = {
                    "versao": 1,
                    "corredores": [dict(corredor) for corredor in dados["corredores"]],
                    "resultados": list(dados["resultados"]),
                }
                corredor = cadastrar_corredor(atualizados["corredores"])
                salvar_dados(atualizados, ARQUIVO_DADOS)
                dados = atualizados
                total_arrecadado += corredor["valor_inscricao"]
                quantidade_inscricoes += 1
                print("Inscrição salva com sucesso.")
            elif opcao == "2":
                resultado = consultar_resultado()
                atualizados = {
                    "versao": 1,
                    "corredores": list(dados["corredores"]),
                    "resultados": dados["resultados"] + [resultado],
                }
                salvar_dados(atualizados, ARQUIVO_DADOS)
                dados = atualizados
                print("Resultado salvo com sucesso.")
            elif opcao == "3":
                consultar_corredor(dados["corredores"])
            elif opcao == "4":
                consultar_historico_resultados(dados["resultados"])
            elif opcao == "5":
                corredor = consultar_corredor(dados["corredores"])
                if corredor is None:
                    continue
                substituir = corredor.get("tempo_chegada") is not None
                if substituir:
                    resposta = input("Já existe um tempo de chegada. Substituir? (s/n): ").strip().lower()
                    while resposta not in ("s", "n"):
                        resposta = input("Digite s para substituir ou n para manter: ").strip().lower()
                    if resposta == "n":
                        print("Tempo de chegada anterior mantido.")
                        continue
                atualizados = {
                    "versao": 1,
                    "corredores": [dict(item) for item in dados["corredores"]],
                    "resultados": list(dados["resultados"]),
                }
                while True:
                    tempo = input("Tempo de chegada (HH:MM:SS): ").strip()
                    try:
                        registrar_tempo_chegada(
                            atualizados["corredores"], corredor["numero"], tempo, substituir,
                        )
                    except ValueError as erro:
                        print(f"Tempo inválido: {erro}")
                        continue
                    break
                salvar_dados(atualizados, ARQUIVO_DADOS)
                dados = atualizados
                print("Tempo de chegada salvo com sucesso.")
            elif opcao == "0":
                print("\nResumo da sessão:")
                print(f"Inscrições aceitas: {quantidade_inscricoes}")
                print(f"Total arrecadado: R$ {total_arrecadado:.2f}")
                print("Encerrando o sistema.")
                return 0
            else:
                print("Opção inválida. Escolha 1, 2, 3, 4, 5 ou 0.")
        except (OSError, ValueError) as erro:
            print(f"Não foi possível salvar a operação: {erro}")
            print("Os dados anteriores foram mantidos. A operação não foi confirmada.")
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando o sistema. As operações confirmadas estão salvas.")
            return 0

if __name__ == "__main__":
    raise SystemExit(main())
