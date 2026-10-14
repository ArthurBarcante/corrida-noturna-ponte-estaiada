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
    main()
