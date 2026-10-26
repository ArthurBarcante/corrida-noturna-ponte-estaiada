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
    """Adiciona um corredor à lista de inscritos da execução atual."""
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
        "numero": len(corredores) + 1,
        "nome": nome,
        "idade": idade,
        "distancia": distancia,
        "lote": lote,
        "valor_inscricao": valor_inscricao,
        "categoria": categoria,
        "codigo": codigo_corredor,
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


def main():
    """Mantém os inscritos da corrida em memória durante a sessão."""
    corredores = []
    quantidade_inscricoes = 0
    total_arrecadado = 0

    while True:
        print("\n====================================")
        print(" CORRIDA NOTURNA DA PONTE ESTAIADA")
        print("====================================")
        print("1 - Fazer inscrição")
        print("2 - Calcular resultado")
        print("3 - Consultar corredores cadastrados")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            corredor = cadastrar_corredor(corredores)
            total_arrecadado += corredor["valor_inscricao"]
            quantidade_inscricoes += 1
        elif opcao == "2":
            consultar_resultado()
        elif opcao == "3":
            consultar_corredor(corredores)
        elif opcao == "0":
            print("\nResumo da sessão:")
            print(f"Inscrições aceitas: {quantidade_inscricoes}")
            print(f"Total arrecadado: R$ {total_arrecadado:.2f}")
            print("Encerrando o sistema.")
            break
        else:
            print("Opção inválida. Escolha 1, 2, 3 ou 0.")

if __name__ == "__main__":
    main()
