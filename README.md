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

Requisito: Python 3 instalado. A V1.0 e a V2.0 utilizam apenas a biblioteca padrão, sem dependências externas.

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

## V2.0 — Controle da corrida inteira

**Itens implementados:**

- [x] Cadastrar e consultar **múltiplos corredores** em uma mesma edição da corrida.
- [x] Armazenar e recuperar inscrições e resultados entre execuções.
- [x] Registrar tempos de chegada dos participantes.
- [x] Gerar **classificações e rankings** por distância e categoria.
- [x] Consolidar totais da corrida e relatórios de inscrições, arrecadação e resultados.
- [x] Permitir consulta da classificação geral da prova.

### Menu atual

| Opção | Ação |
| --- | --- |
| `1` | Cadastrar um corredor e salvar sua inscrição |
| `2` | Calcular um resultado individual e salvá-lo no histórico |
| `3` | Listar os inscritos e consultar uma inscrição pelo número |
| `4` | Exibir o histórico de resultados calculados |
| `5` | Registrar o tempo de chegada de um participante inscrito |
| `6` | Consultar a classificação por distância e categoria |
| `7` | Exibir totais e relatórios de inscrições, arrecadação e resultados |
| `8` | Exibir a classificação geral dos 5 km e dos 10 km |
| `0` | Exibir o resumo da sessão e encerrar |

Na opção `3`, digite `0` para voltar depois de ver a lista de inscritos. Nomes e códigos abreviados podem se repetir, mas cada inscrição recebe um número diferente. A numeração continua após o maior número de inscrição recuperado do arquivo.

Os resultados da opção `2` são **cálculos avulsos**, sem associação a um corredor cadastrado. A opção `4` exibe os cálculos salvos, incluindo os recuperados de execuções anteriores. Esses cálculos continuam aceitando `00:00:00`, conforme o comportamento da V1.0.

### Registro de tempos de chegada

Na opção `5`, escolha o participante pelo número da inscrição exibido na lista; digite `0` para voltar. Informe o **tempo de prova** no formato `HH:MM:SS`, entre `00:00:01` e `99:59:59`. Minutos e segundos devem estar entre `00` e `59`. Entradas inválidas são solicitadas novamente.

Cada inscrição tem um tempo de chegada. Se já houver um tempo registrado, responda `s` para confirmar sua substituição ou `n` para manter o anterior. O programa confirma o registro após salvá-lo no arquivo de dados.

A opção `3` mostra o tempo de chegada do participante ou indica **pendente**. Novos cadastros começam pendentes, assim como inscrições antigas sem esse campo. O tempo fica associado à inscrição e é recuperado ao reiniciar o programa; ele não é adicionado ao histórico de cálculos avulsos da opção `4`.

A opção `0` preserva o resumo da V1.0: considera somente a quantidade de inscrições aceitas e o valor arrecadado **durante a execução atual**. As inscrições recuperadas continuam disponíveis para consulta, mas não entram novamente nos totais da sessão.

### Classificações por distância e categoria

Na opção `6`, escolha 5 km ou 10 km (`0` para voltar) e uma categoria, ou `0` para todas as categorias daquela distância. O ranking inclui somente inscritos com tempo de chegada registrado, em ordem do menor para o maior tempo, identificados por número de inscrição, nome, categoria e tempo.

Tempos iguais recebem a mesma posição, e a posição seguinte considera o total de participantes anteriores (por exemplo: 1º, 1º, 3º). Empatados aparecem por número de inscrição crescente. Cada filtro recalcula suas posições; distâncias diferentes nunca são misturadas. Se não houver chegadas no filtro, o programa informa isso.

A consulta usa os tempos recuperados do arquivo e reflete substituições de tempo. Não altera inscrições nem grava dados. Cálculos avulsos não participam dos rankings.

### Classificação geral da prova

Na opção `8`, o sistema exibe diretamente a classificação geral dos 5 km e, em seguida, a dos 10 km, reunindo todas as categorias de cada distância. As posições são independentes por distância e seguem o menor tempo de chegada. Cada linha identifica posição, número da inscrição, nome, categoria e tempo.

Os empates seguem a mesma regra da opção `6`: tempos iguais recebem a mesma posição (por exemplo: 1º, 1º, 3º), com os empatados exibidos por número de inscrição crescente. Participantes sem tempo de chegada registrado ficam fora da classificação; quando uma distância não tem chegadas, o programa informa isso.

A consulta inclui inscrições recuperadas e tempos registrados na sessão atual, e reflete substituições de tempo na próxima consulta. Não solicita filtros nem grava dados. Cálculos avulsos não participam da classificação geral.

### Totais e relatórios da corrida

Na opção `7`, o sistema reúne todas as inscrições da edição, incluindo as recuperadas de execuções anteriores e as cadastradas na sessão atual. O relatório apresenta:

- Quantidade total de inscrições, arrecadação, chegadas registradas e pendentes e participantes premiados pelo limite de tempo da categoria e distância.
- Esses mesmos totais separados por distância (5 km e 10 km), categoria e lote, incluindo grupos vazios com valores zerados.
- Relação das inscrições com número, nome, distância, categoria, lote e valor cobrado, considerando os acréscimos e descontos da inscrição.
- Resultados dos inscritos com tempo de chegada, pace e premiação; participantes sem tempo registrado aparecem como pendentes.

As relações seguem o número de inscrição crescente. Cada inscrição é contada uma única vez, mesmo quando nomes se repetem. Substituir um tempo atualiza os resultados e a premiação no próximo relatório. Os cálculos avulsos das opções `2` e `4` permanecem no histórico e não entram nos totais ou nos resultados dos inscritos.

A consulta não altera nem grava dados. Sem inscrições, exibe totais zerados e informa que não há participantes. O resumo exibido ao sair continua considerando somente as inscrições e a arrecadação da sessão atual.

### Armazenamento e recuperação

As inscrições, seus tempos de chegada e o histórico de resultados são salvos em **`dados/corrida.json`**, em UTF-8. O caminho é relativo à pasta de `main.py`, independentemente da pasta de trabalho do terminal.

- Se o arquivo não existir, o programa inicia sem inscrições e sem resultados anteriores.
- A pasta e o arquivo são criados automaticamente na primeira gravação após um cadastro, cálculo ou registro de tempo.
- O tempo de chegada usa o campo opcional `tempo_chegada` de cada inscrição. Arquivos antigos sem esse campo continuam válidos, e essas inscrições são apresentadas como pendentes.
- Ao iniciar novamente, o programa recupera as inscrições, os tempos de chegada e o histórico de resultados salvos.
- Cada gravação usa um arquivo temporário e substitui o arquivo anterior somente após concluir a escrita.
- Um arquivo inválido impede a inicialização e tem seu conteúdo preservado. Corrija os dados ou restaure uma cópia válida antes de executar novamente.
- A pasta `dados/` é ignorada pelo Git; os dados locais não fazem parte do repositório.

Todos os itens previstos para a V2.0 estão implementados.

## Testes

Execute os testes de cadastro, consulta, armazenamento, recuperação, registro de tempos, classificação e relatórios com:

```powershell
py -3 -m unittest -v
```

Os testes incluem a recuperação dos dados após reiniciar o programa, a leitura de inscrições antigas sem tempo de chegada, a identificação de homônimos pelo número da inscrição, a validação e a substituição de tempos, além da preservação dos dados anteriores em caso de arquivo inválido ou falha de gravação.

Os testes de relatórios conferem os totais e agrupamentos, os descontos, o pace e a premiação dos inscritos, a atualização após substituir um tempo, o relatório vazio e a consulta sem gravação. Também verificam a separação dos cálculos avulsos e do resumo da sessão.

Os testes da classificação geral verificam a separação por distância, a inclusão das diferentes categorias, os empates, a exclusão de chegadas pendentes e cálculos avulsos e a atualização após substituir um tempo. Também conferem a consulta sem gravação e as distâncias sem resultados.

## Tecnologias

- Python 3
- Git e GitHub
- Visual Studio Code

A V2.0 permite acompanhar inscrições, arrecadação, chegadas e classificações de toda a corrida.
