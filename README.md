# Corrida Noturna da Ponte Estaiada

Sistema de terminal desenvolvido em **Python** para apoiar as inscrições e a apuração individual de resultados da **Corrida Noturna da Ponte Estaiada**, organizada pela Assessoria Passo Certo, em Teresina (PI).

## Objetivo

Reduzir erros de cobrança e de enquadramento em categorias, além de automatizar cálculos de tempo, ritmo e premiação. Na **versão 1.0**, o sistema atende um corredor por vez e mantém o resumo das inscrições apenas durante a sessão de execução.

## Funcionalidades da V1.0

- **Menu interativo:** fazer inscrição, calcular resultado ou sair.
- **Inscrição:** registrar nome, idade, distância (5 km ou 10 km) e lote; recusar inscrições de menores de 16 anos; exibir comprovante.
- **Valor da inscrição:** 1º lote a R$ 80,00 e 2º lote a R$ 100,00; acréscimo de R$ 20,00 para 10 km; desconto de 50% para pessoas com 60 anos ou mais.
- **Categorias por idade:** Juvenil (16 a 19 anos), Adulto (20 a 39), Master (40 a 59) e Veterano (60 ou mais).
- **Código do corredor:** três primeiras letras do primeiro nome + três primeiras letras do último sobrenome + idade, em maiúsculas. Exemplo: `MARSOU34`.
- **Resultado individual:** converter tempo no formato `HH:MM:SS` em segundos, calcular o pace médio por quilômetro e verificar a premiação conforme o limite da categoria e da distância.
- **Validações:** repetir entradas de menu, idade, distância e lote até receber valores válidos; rejeitar formatos inválidos de tempo.
- **Resumo da sessão:** exibir a quantidade de inscrições aceitas e o total arrecadado ao sair.

### Limites de tempo para premiação

O corredor é premiado quando seu tempo é **menor ou igual** ao limite da categoria.

| Categoria | Idade | 5 km | 10 km |
| --- | --- | --- | --- |
| Juvenil | 16 a 19 | 00:25:00 | 00:52:00 |
| Adulto | 20 a 39 | 00:22:00 | 00:46:00 |
| Master | 40 a 59 | 00:25:00 | 00:52:00 |
| Veterano | 60 ou mais | 00:30:00 | 01:03:00 |

## Como executar

Requisito: Python 3 instalado. A V1.0 utiliza apenas a biblioteca padrão, sem dependências externas.

1. Clone o repositório ou abra sua pasta no terminal.
2. Execute:

```powershell
py -3 main.py
```

Em ambientes onde o comando `py` não estiver disponível, utilize `python3 main.py` (ou `python main.py`, se esse comando apontar para Python 3).

3. Escolha uma opção do menu e siga as instruções exibidas.

## Histórico de versões

### V0.1 — Estrutura inicial

- Configuração do projeto em Python, Git e GitHub.
- Criação do arquivo principal, documentação inicial e `.gitignore`.

### V1.0 — Inscrição e resultado individual

- Cálculo do valor da inscrição, categoria e código do corredor.
- Conversão do tempo e cálculo do pace.
- Verificação da premiação por categoria e distância.
- Menu interativo, validação de entradas e resumo da sessão.

## Planejamento para a V2.0 — Controle da corrida inteira

**Funcionalidades previstas para desenvolvimento futuro; não fazem parte da V1.0:**

- Cadastrar e consultar **múltiplos corredores** em uma mesma edição da corrida.
- Armazenar e recuperar inscrições e resultados entre execuções.
- Registrar tempos de chegada dos participantes.
- Gerar **classificações e rankings** por distância e categoria.
- Consolidar totais da corrida e relatórios de inscrições, arrecadação e resultados.
- Permitir consulta da classificação geral da prova.

O escopo detalhado e o formato de armazenamento da V2.0 serão definidos na segunda etapa do projeto.

## Tecnologias

- Python 3
- Git e GitHub
- Visual Studio Code

A V2.0 está planejada para evoluir do atendimento individual para o controle da corrida inteira, incluindo múltiplos corredores, armazenamento de dados, classificações e relatórios.
