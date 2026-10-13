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

def main():
    """Executa o programa principal da corrida."""
    print("====================================")
    print(" CORRIDA NOTURNA DA PONTE ESTAIADA")
    print("====================================")
    print("Versão 0.1 - Estrutura inicial")
    valor = calcular_valor_inscricao(25, 10, 1)
    print(valor)

if __name__ == "__main__":
    main()