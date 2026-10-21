def cadastrar_corredor():
    """Cadastra os dados de um corredor."""
    nome = input("Digite o nome do corredor: ")
    idade = int(input("Digite a idade do corredor: "))
     

    while idade < 16:
        print("Erro: o corredor precisa ter pelo menos 16 anos.")
        idade = int(input("Digite a idade novamente: "))
    distancia = int(input("Digite a distância da corrida (5 ou 10 km): "))
    lote = int(input("Digite o lote de inscrição (1 ou 2): "))

    valor_inscricao = calcular_valor_inscricao(idade, distancia, lote)
    categoria = determinar_categoria(idade)
    codigo_corredor = gerar_codigo_corredor(nome, idade)

    print("\nResumo da Inscrição:")
    print(f"Nome: {nome}")
    print(f"Idade: {idade}")
    print(f"Distância: {distancia} km")
    print(f"Lote: {lote}")
    print(f"Valor da Inscrição: R$ {valor_inscricao:.2f}")
    print(f"Categoria: {categoria}")
    print(f"Código do Corredor: {codigo_corredor}")
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

def main():
    """Executa o programa principal da corrida."""
    print("====================================")
    print(" CORRIDA NOTURNA DA PONTE ESTAIADA")
    print("====================================")
    print("Versão 0.1 - Estrutura inicial")
    valor = calcular_valor_inscricao(25, 10, 1)
    print(valor)
    categoria = determinar_categoria(25)
    print(categoria)
    codigo = gerar_codigo_corredor("João Silva", 25)
    print(codigo)

if __name__ == "__main__":
    cadastrar_corredor()
