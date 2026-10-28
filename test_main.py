import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main


def inscricao_exemplo(**alteracoes):
    inscricao = {
        "numero": 1,
        "nome": "Maria Souza",
        "idade": 30,
        "distancia": 5,
        "lote": 1,
        "valor_inscricao": 80,
        "categoria": "Adulto",
        "codigo": "MARSOU30",
    }
    inscricao.update(alteracoes)
    return inscricao


def resultado_exemplo(**alteracoes):
    resultado = {
        "idade": 30,
        "distancia": 5,
        "tempo": "00:22:00",
        "tempo_segundos": 1320,
        "categoria": "Adulto",
        "pace": "4'24\"/km",
        "premiado": True,
    }
    resultado.update(alteracoes)
    return resultado


def dados_exemplo():
    return {"versao": 1, "corredores": [inscricao_exemplo()], "resultados": [resultado_exemplo()]}


class TestCadastroEConsulta(unittest.TestCase):
    def cadastrar(self, corredores, nome="Maria Souza", idade="30", distancia="5", lote="1"):
        with patch("builtins.input", side_effect=[nome, idade, distancia, lote]), redirect_stdout(io.StringIO()):
            return main.cadastrar_corredor(corredores)

    def test_cadastra_varios_corredores_sem_sobrescrever_os_anteriores(self):
        corredores = []
        primeiro = self.cadastrar(corredores)
        segundo = self.cadastrar(corredores, "João Silva", "65", "10", "2")
        self.assertEqual([c["numero"] for c in corredores], [1, 2])
        self.assertIs(corredores[0], primeiro)
        self.assertIs(corredores[1], segundo)
        self.assertEqual(primeiro["valor_inscricao"], 80)
        self.assertEqual(segundo["valor_inscricao"], 60)
        self.assertEqual(segundo["categoria"], "Veterano")
        self.assertIsNone(primeiro["tempo_chegada"])
        self.assertIsNone(segundo["tempo_chegada"])

    def test_homonimos_com_codigos_iguais_tem_inscricoes_distintas(self):
        corredores = []
        primeiro = self.cadastrar(corredores)
        segundo = self.cadastrar(corredores)
        self.assertEqual(primeiro["codigo"], segundo["codigo"])
        self.assertNotEqual(primeiro["numero"], segundo["numero"])
        with patch("builtins.input", return_value="2"), redirect_stdout(io.StringIO()):
            self.assertIs(main.consultar_corredor(corredores), segundo)

    def test_consulta_cada_corredor_pelo_numero(self):
        corredores = []
        self.cadastrar(corredores)
        self.cadastrar(corredores, "João Silva", "65", "10", "2")
        for indice in (0, 1):
            saida = io.StringIO()
            with self.subTest(indice=indice), \
                    patch("builtins.input", return_value=str(indice + 1)), redirect_stdout(saida):
                resultado = main.consultar_corredor(corredores)
            self.assertIs(resultado, corredores[indice])
            detalhes = saida.getvalue().split("Dados do corredor:")[1]
            self.assertIn(f"Nome: {corredores[indice]['nome']}", detalhes)
        self.assertEqual(len(corredores), 2)

    def test_consulta_lista_vazia_sem_solicitar_numero(self):
        with patch("builtins.input", side_effect=AssertionError("Não deveria pedir entrada")), redirect_stdout(io.StringIO()):
            self.assertIsNone(main.consultar_corredor([]))

    def test_numero_inexistente_e_voltar_nao_alteram_cadastros(self):
        corredores = []
        self.cadastrar(corredores)
        anterior = [dict(c) for c in corredores]
        for numero in ("9", "0"):
            with self.subTest(numero=numero), patch("builtins.input", return_value=numero), redirect_stdout(io.StringIO()):
                self.assertIsNone(main.consultar_corredor(corredores))
            self.assertEqual(corredores, anterior)

    def test_entradas_invalidas_sao_corrigidas_antes_de_adicionar(self):
        corredores = []
        with patch("builtins.input", side_effect=["", "Maria Souza", "abc", "15", "30", "7", "5", "3", "1"]), redirect_stdout(io.StringIO()):
            main.cadastrar_corredor(corredores)
        self.assertEqual(len(corredores), 1)
        self.assertEqual(corredores[0]["numero"], 1)
        self.assertEqual(corredores[0]["idade"], 30)

    def test_numero_continua_apos_o_maior_registro_recuperado(self):
        corredores = [inscricao_exemplo(numero=7)]
        novo = self.cadastrar(corredores)
        self.assertEqual(novo["numero"], 8)
        self.assertEqual([c["numero"] for c in corredores], [7, 8])


class TestPersistencia(unittest.TestCase):
    def test_arquivo_ausente_retorna_listas_vazias_sem_criar_arquivo(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados" / "corrida.json"
            self.assertEqual(main.carregar_dados(caminho), {
                "versao": 1, "corredores": [], "resultados": [],
            })
            self.assertFalse(caminho.exists())

    def test_grava_e_recupera_inscricoes_acentuadas_e_resultados(self):
        dados = dados_exemplo()
        dados["corredores"].append(inscricao_exemplo(
            numero=2, nome="João Silva", codigo="JOÃSIL30",
        ))
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "dados" / "corrida.json"
            main.salvar_dados(dados, caminho)
            self.assertEqual(main.carregar_dados(caminho), dados)
            self.assertIn("João Silva", caminho.read_text(encoding="utf-8"))
            self.assertEqual([p.name for p in caminho.parent.iterdir()], ["corrida.json"])

    def test_json_corrompido_ou_inconsistente_e_preservado(self):
        casos = [
            "{invalido",
            json.dumps({"versao": 99, "corredores": [], "resultados": []}),
            json.dumps({"versao": 1, "corredores": {}, "resultados": []}),
            json.dumps({"versao": 1, "corredores": [inscricao_exemplo(), inscricao_exemplo()], "resultados": []}),
            json.dumps({"versao": 1, "corredores": [inscricao_exemplo(idade=15)], "resultados": []}),
            json.dumps({"versao": 1, "corredores": [inscricao_exemplo(valor_inscricao=float("nan"))], "resultados": []}),
            json.dumps({"versao": 1, "corredores": [], "resultados": [resultado_exemplo(tempo_segundos=1)]}),
        ]
        for conteudo in casos:
            with self.subTest(conteudo=conteudo), tempfile.TemporaryDirectory() as diretorio:
                caminho = Path(diretorio) / "corrida.json"
                caminho.write_text(conteudo, encoding="utf-8")
                with self.assertRaises(ValueError):
                    main.carregar_dados(caminho)
                self.assertEqual(caminho.read_text(encoding="utf-8"), conteudo)

    def test_erro_na_substituicao_preserva_dados_e_remove_temporario(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados_exemplo(), caminho)
            anterior = caminho.read_bytes()
            with patch("main.os.replace", side_effect=OSError("Falha de disco")):
                with self.assertRaises(OSError):
                    main.salvar_dados({"versao": 1, "corredores": [], "resultados": []}, caminho)
            self.assertEqual(caminho.read_bytes(), anterior)
            self.assertEqual([p.name for p in caminho.parent.iterdir()], ["corrida.json"])

    def test_dados_invalidos_nao_sobrescrevem_arquivo(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados_exemplo(), caminho)
            anterior = caminho.read_bytes()
            with self.assertRaises(ValueError):
                main.salvar_dados({"versao": 1, "corredores": [inscricao_exemplo(numero=0)], "resultados": []}, caminho)
            self.assertEqual(caminho.read_bytes(), anterior)


class TestRegistroDeChegada(unittest.TestCase):
    def test_registra_somente_no_numero_escolhido_entre_homonimos(self):
        corredores = [inscricao_exemplo(), inscricao_exemplo(numero=2)]
        anterior = [dict(c) for c in corredores]
        resultado = main.registrar_tempo_chegada(corredores, 2, " 00:22:00 ")
        self.assertIs(resultado, corredores[1])
        self.assertEqual(corredores[0], anterior[0])
        self.assertEqual(corredores[1], dict(anterior[1], tempo_chegada="00:22:00"))

    def test_numero_invalido_ou_inexistente_nao_altera_os_cadastros(self):
        for numero in (0, -1, True, "1", 9):
            corredores = [inscricao_exemplo()]
            anterior = [dict(c) for c in corredores]
            with self.subTest(numero=numero), self.assertRaises(ValueError):
                main.registrar_tempo_chegada(corredores, numero, "00:22:00")
            self.assertEqual(corredores, anterior)

    def test_tempo_invalido_nao_altera_o_registro(self):
        for tempo in (None, 1320, "", "00:00:00", "00:60:00", "00:22:60", "100:00:00", "-1:00:00"):
            corredores = [inscricao_exemplo(tempo_chegada=None)]
            anterior = [dict(c) for c in corredores]
            with self.subTest(tempo=tempo), self.assertRaises(ValueError):
                main.registrar_tempo_chegada(corredores, 1, tempo)
            self.assertEqual(corredores, anterior)

    def test_substituicao_exige_autorizacao_explicita(self):
        corredores = [inscricao_exemplo(tempo_chegada="00:22:00")]
        with self.assertRaises(ValueError):
            main.registrar_tempo_chegada(corredores, 1, "00:21:00")
        self.assertEqual(corredores[0]["tempo_chegada"], "00:22:00")
        resultado = main.registrar_tempo_chegada(corredores, 1, "00:21:00", substituir=True)
        self.assertIs(resultado, corredores[0])
        self.assertEqual(resultado["tempo_chegada"], "00:21:00")

    def test_arquivo_legado_e_recuperado_sem_ser_modificado(self):
        dados = dados_exemplo()
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            anterior = caminho.read_bytes()
            recuperados = main.carregar_dados(caminho)
            self.assertEqual(recuperados, dados)
            self.assertNotIn("tempo_chegada", recuperados["corredores"][0])
            self.assertEqual(caminho.read_bytes(), anterior)

    def test_campo_opcional_pendente_ou_valido_e_persistido(self):
        for tempo in (None, "00:00:01", "99:59:59"):
            dados = dados_exemplo()
            dados["corredores"][0]["tempo_chegada"] = tempo
            with self.subTest(tempo=tempo), tempfile.TemporaryDirectory() as diretorio:
                caminho = Path(diretorio) / "corrida.json"
                main.salvar_dados(dados, caminho)
                self.assertEqual(main.carregar_dados(caminho), dados)

    def test_arquivo_com_chegada_invalida_e_preservado(self):
        for tempo in (0, True, [], "", "00:00:00", "00:60:00", "100:00:00"):
            dados = dados_exemplo()
            dados["corredores"][0]["tempo_chegada"] = tempo
            with self.subTest(tempo=tempo), tempfile.TemporaryDirectory() as diretorio:
                caminho = Path(diretorio) / "corrida.json"
                caminho.write_text(json.dumps(dados), encoding="utf-8")
                anterior = caminho.read_bytes()
                with self.assertRaises(ValueError):
                    main.carregar_dados(caminho)
                self.assertEqual(caminho.read_bytes(), anterior)

    def test_consulta_mostra_pendente_ou_tempo_sem_modificar_registro(self):
        for dados_corredor, texto in (
            (inscricao_exemplo(), "Tempo de chegada: pendente"),
            (inscricao_exemplo(tempo_chegada=None), "Tempo de chegada: pendente"),
            (inscricao_exemplo(tempo_chegada="00:22:00"), "Tempo de chegada: 00:22:00"),
        ):
            anterior = dict(dados_corredor)
            saida = io.StringIO()
            with self.subTest(texto=texto), patch("builtins.input", return_value="1"), redirect_stdout(saida):
                self.assertIs(main.consultar_corredor([dados_corredor]), dados_corredor)
            self.assertIn(texto, saida.getvalue())
            self.assertEqual(dados_corredor, anterior)


class TestClassificacao(unittest.TestCase):
    def test_ordena_filtra_empates_e_preserva_inscricoes(self):
        corredores = [
            inscricao_exemplo(numero=4, tempo_chegada="00:23:00"),
            inscricao_exemplo(numero=3, tempo_chegada="00:22:00"),
            inscricao_exemplo(numero=2, tempo_chegada="00:22:00"),
            inscricao_exemplo(numero=5, idade=18, categoria="Juvenil", tempo_chegada="00:21:00"),
            inscricao_exemplo(numero=6, distancia=10, tempo_chegada="00:01:00"),
            inscricao_exemplo(numero=7),
            inscricao_exemplo(numero=8, tempo_chegada=None),
        ]
        anterior = [dict(c) for c in corredores]
        ranking = main.gerar_classificacao(corredores, 5)
        self.assertEqual([c["numero"] for c in ranking], [5, 2, 3, 4])
        self.assertEqual([c["posicao"] for c in ranking], [1, 2, 2, 4])
        adultos = main.gerar_classificacao(corredores, 5, "Adulto")
        self.assertEqual([c["numero"] for c in adultos], [2, 3, 4])
        self.assertEqual([c["posicao"] for c in adultos], [1, 1, 3])
        self.assertEqual(main.gerar_classificacao(corredores, 10)[0]["numero"], 6)
        self.assertEqual(corredores, anterior)
        ranking[0]["nome"] = "Outro"
        self.assertEqual(corredores, anterior)

    def test_filtros_vazios_e_invalidos(self):
        self.assertEqual(main.gerar_classificacao([], 5), [])
        self.assertEqual(main.gerar_classificacao([inscricao_exemplo()], 5), [])
        self.assertEqual(main.gerar_classificacao([
            inscricao_exemplo(tempo_chegada="00:22:00"),
        ], 5, "Master"), [])
        for distancia, categoria in ((3, None), (5, "Inexistente")):
            with self.subTest(distancia=distancia, categoria=categoria), self.assertRaises(ValueError):
                main.gerar_classificacao([], distancia, categoria)

    def test_menu_recupera_chegadas_sem_gravar_e_reflete_substituicao(self):
        dados = dados_exemplo()
        dados["corredores"] = [
            inscricao_exemplo(tempo_chegada="00:22:00"),
            inscricao_exemplo(numero=2, tempo_chegada="00:21:00"),
        ]
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados, caminho)
            anterior = caminho.read_bytes()
            saida = io.StringIO()
            with patch.object(main, "ARQUIVO_DADOS", caminho), \
                    patch("main.salvar_dados", wraps=main.salvar_dados) as salvar, \
                    patch("builtins.input", side_effect=["6", "3", "5", "9", "2", "6", "10", "0", "6", "0", "0"]), \
                    redirect_stdout(saida):
                self.assertEqual(main.main(), 0)
            salvar.assert_not_called()
            self.assertEqual(caminho.read_bytes(), anterior)
            texto = saida.getvalue()
            self.assertLess(texto.index("1º | Inscrição 2"), texto.index("2º | Inscrição 1"))
            self.assertIn("Nenhum participante com tempo de chegada neste filtro.", texto)
            main.registrar_tempo_chegada(dados["corredores"], 1, "00:20:00", substituir=True)
            main.salvar_dados(dados, caminho)
            recuperados = main.carregar_dados(caminho)
            self.assertEqual(main.gerar_classificacao(recuperados["corredores"], 5)[0]["numero"], 1)


class TestResultadosAvulsos(unittest.TestCase):
    def test_calculo_retorna_resultado_sem_vinculo_com_inscricao(self):
        with patch("builtins.input", side_effect=["30", "5", "00:22:00"]), redirect_stdout(io.StringIO()):
            resultado = main.consultar_resultado()
        self.assertEqual(resultado, resultado_exemplo())

    def test_tempo_zero_continua_valido_e_pode_ser_persistido(self):
        with patch("builtins.input", side_effect=["30", "5", "00:00:00"]), redirect_stdout(io.StringIO()):
            resultado = main.consultar_resultado()
        self.assertEqual(resultado["tempo_segundos"], 0)
        self.assertEqual(resultado["pace"], "0'00\"/km")
        dados = {"versao": 1, "corredores": [], "resultados": [resultado]}
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados, caminho)
            self.assertEqual(main.carregar_dados(caminho), dados)

    def test_historico_exibe_calculos_sem_pedir_inscricao(self):
        resultados = [resultado_exemplo(), resultado_exemplo(
            tempo="00:00:00", tempo_segundos=0, pace="0'00\"/km",
        )]
        anterior = [dict(r) for r in resultados]
        saida = io.StringIO()
        with patch("builtins.input", side_effect=AssertionError("Histórico não deve solicitar vínculo")), redirect_stdout(saida):
            main.consultar_historico_resultados(resultados)
        self.assertIn("00:22:00", saida.getvalue())
        self.assertIn("00:00:00", saida.getvalue())
        self.assertEqual(resultados, anterior)


class TestFalhasNoMenu(unittest.TestCase):
    def test_falha_ao_salvar_inscricao_nao_a_confirma_nem_mantem_em_memoria(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            dados = {"versao": 1, "corredores": [inscricao_exemplo(numero=4)], "resultados": []}
            main.salvar_dados(dados, caminho)
            anterior = caminho.read_bytes()
            saida = io.StringIO()
            with patch.object(main, "ARQUIVO_DADOS", caminho), \
                    patch("main.os.replace", side_effect=OSError("Falha de disco")), \
                    patch("builtins.input", side_effect=["1", "João Silva", "65", "10", "2", "3", "5", "0"]), \
                    redirect_stdout(saida):
                self.assertEqual(main.main(), 0)
            self.assertEqual(caminho.read_bytes(), anterior)
            self.assertIn("Não foi possível salvar", saida.getvalue())
            self.assertIn("Inscrição não encontrada", saida.getvalue())
            self.assertIn("Inscrições aceitas: 0", saida.getvalue())
            self.assertIn("Total arrecadado: R$ 0.00", saida.getvalue())
            self.assertNotIn("Inscrição salva com sucesso.", saida.getvalue())

    def test_falha_ao_salvar_resultado_nao_altera_historico_em_memoria(self):
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados({"versao": 1, "corredores": [], "resultados": []}, caminho)
            anterior = caminho.read_bytes()
            saida = io.StringIO()
            with patch.object(main, "ARQUIVO_DADOS", caminho), \
                    patch("main.os.replace", side_effect=OSError("Falha de disco")), \
                    patch("main.consultar_historico_resultados", wraps=main.consultar_historico_resultados) as historico, \
                    patch("builtins.input", side_effect=["2", "30", "5", "00:22:00", "4", "0"]), \
                    redirect_stdout(saida):
                self.assertEqual(main.main(), 0)
            self.assertEqual(caminho.read_bytes(), anterior)
            self.assertEqual(historico.call_args.args[0], [])
            self.assertIn("Não foi possível salvar", saida.getvalue())
            self.assertNotIn("Resultado salvo com sucesso.", saida.getvalue())


class TestMenuDeChegada(unittest.TestCase):
    def test_falha_ao_salvar_preserva_tempo_anterior_em_memoria_e_arquivo(self):
        dados = dados_exemplo()
        dados["corredores"][0]["tempo_chegada"] = "00:22:00"
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados, caminho)
            anterior = caminho.read_bytes()
            saida = io.StringIO()
            with patch.object(main, "ARQUIVO_DADOS", caminho), \
                    patch("main.os.replace", side_effect=OSError("Falha de disco")), \
                    patch("builtins.input", side_effect=["5", "1", "s", "00:21:00", "3", "1", "0"]), \
                    redirect_stdout(saida):
                self.assertEqual(main.main(), 0)
            self.assertEqual(caminho.read_bytes(), anterior)
            self.assertEqual(main.carregar_dados(caminho), dados)
            self.assertIn("Não foi possível salvar", saida.getvalue())
            depois_da_falha = saida.getvalue().split("Não foi possível salvar", 1)[1]
            self.assertIn("Tempo de chegada: 00:22:00", depois_da_falha)
            self.assertNotIn("Tempo de chegada: 00:21:00", depois_da_falha)
            self.assertNotIn("Tempo de chegada salvo com sucesso.", saida.getvalue())
            self.assertIn("Inscrições aceitas: 0", saida.getvalue())

    def test_cancelar_substituicao_nao_grava(self):
        dados = dados_exemplo()
        dados["corredores"][0]["tempo_chegada"] = "00:22:00"
        with tempfile.TemporaryDirectory() as diretorio:
            caminho = Path(diretorio) / "corrida.json"
            main.salvar_dados(dados, caminho)
            anterior = caminho.read_bytes()
            saida = io.StringIO()
            with patch.object(main, "ARQUIVO_DADOS", caminho), \
                    patch("main.salvar_dados", wraps=main.salvar_dados) as salvar, \
                    patch("builtins.input", side_effect=["5", "1", "talvez", "n", "0"]), \
                    redirect_stdout(saida):
                self.assertEqual(main.main(), 0)
            salvar.assert_not_called()
            self.assertEqual(caminho.read_bytes(), anterior)
            self.assertNotIn("Tempo de chegada salvo com sucesso.", saida.getvalue())

    def test_voltar_ou_numero_ausente_ou_lista_vazia_nao_gravam(self):
        for corredores, entradas in (
            ([inscricao_exemplo()], ["5", "0", "0"]),
            ([inscricao_exemplo()], ["5", "9", "0"]),
            ([], ["5", "0"]),
        ):
            dados = {"versao": 1, "corredores": corredores, "resultados": []}
            with self.subTest(entradas=entradas), tempfile.TemporaryDirectory() as diretorio:
                caminho = Path(diretorio) / "corrida.json"
                main.salvar_dados(dados, caminho)
                anterior = caminho.read_bytes()
                with patch.object(main, "ARQUIVO_DADOS", caminho), \
                        patch("main.salvar_dados", wraps=main.salvar_dados) as salvar, \
                        patch("builtins.input", side_effect=entradas), redirect_stdout(io.StringIO()):
                    self.assertEqual(main.main(), 0)
                salvar.assert_not_called()
                self.assertEqual(caminho.read_bytes(), anterior)


class TestFluxoDaSessao(unittest.TestCase):
    def setUp(self):
        temporario = tempfile.TemporaryDirectory()
        self.addCleanup(temporario.cleanup)
        self.projeto = Path(temporario.name) / "projeto"
        self.terminal = Path(temporario.name) / "terminal"
        self.projeto.mkdir()
        self.terminal.mkdir()
        self.programa = self.projeto / "main.py"
        shutil.copyfile(main.__file__, self.programa)
        self.arquivo = self.projeto / "dados" / "corrida.json"

    def executar(self, entradas):
        return subprocess.run(
            [sys.executable, str(self.programa)], input="\n".join(entradas) + "\n",
            capture_output=True, text=True, encoding="utf-8", timeout=10,
            cwd=self.terminal, env=dict(os.environ, PYTHONUTF8="1"),
        )

    def test_recupera_inscricoes_resultados_e_numeracao_em_outra_execucao(self):
        primeira = self.executar([
            "1", "Maria Souza", "30", "5", "1",
            "1", "João Silva", "65", "10", "2",
            "3", "1", "3", "2",
            "2", "30", "5", "00:22:00", "4", "0",
        ])
        self.assertEqual(primeira.returncode, 0, primeira.stderr)
        self.assertEqual(primeira.stdout.count("Dados do corredor:"), 2)
        self.assertIn("Inscrições aceitas: 2", primeira.stdout)
        self.assertIn("Total arrecadado: R$ 140.00", primeira.stdout)
        self.assertIn("Pace médio: 4'24\"/km", primeira.stdout)
        self.assertIn("Premiado: Sim", primeira.stdout)
        dados = main.carregar_dados(self.arquivo)
        self.assertEqual([c["numero"] for c in dados["corredores"]], [1, 2])
        self.assertEqual(dados["resultados"], [resultado_exemplo()])
        self.assertFalse((self.terminal / "dados").exists())

        segunda = self.executar([
            "3", "2", "4", "1", "Pedro Lima", "18", "5", "2", "0",
        ])
        self.assertEqual(segunda.returncode, 0, segunda.stderr)
        self.assertIn("Nome: João Silva", segunda.stdout)
        self.assertIn("00:22:00", segunda.stdout)
        self.assertIn("Inscrições aceitas: 1", segunda.stdout)
        self.assertIn("Total arrecadado: R$ 100.00", segunda.stdout)
        recuperados = main.carregar_dados(self.arquivo)
        self.assertEqual([c["numero"] for c in recuperados["corredores"]], [1, 2, 3])
        self.assertEqual(recuperados["resultados"], dados["resultados"])
        self.assertTrue(all("tempo_segundos" not in c for c in recuperados["corredores"]))

    def test_dados_invalidos_impedem_iniciar_sem_sobrescrever(self):
        self.arquivo.parent.mkdir()
        self.arquivo.write_text("{invalido", encoding="utf-8")
        resultado = self.executar(["1"])
        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(self.arquivo.read_text(encoding="utf-8"), "{invalido")

    def test_registra_chegada_e_recupera_na_consulta_apos_reiniciar(self):
        dados = dados_exemplo()
        main.salvar_dados(dados, self.arquivo)
        primeira = self.executar(["5", "1", "00:22:00", "0"])
        self.assertEqual(primeira.returncode, 0, primeira.stderr)
        self.assertIn("Tempo de chegada salvo com sucesso.", primeira.stdout)
        recuperados = main.carregar_dados(self.arquivo)
        self.assertEqual(recuperados["corredores"], [dict(dados["corredores"][0], tempo_chegada="00:22:00")])
        self.assertEqual(recuperados["resultados"], dados["resultados"])
        self.assertIn("Inscrições aceitas: 0", primeira.stdout)
        anterior = self.arquivo.read_bytes()
        segunda = self.executar(["3", "1", "4", "0"])
        self.assertEqual(segunda.returncode, 0, segunda.stderr)
        self.assertIn("Tempo de chegada: 00:22:00", segunda.stdout)
        self.assertEqual(self.arquivo.read_bytes(), anterior)

    def test_chegada_repete_tempo_invalido_e_confirma_atualizacao(self):
        dados = dados_exemplo()
        main.salvar_dados(dados, self.arquivo)
        resultado = self.executar([
            "5", "1", "00:00:00", "00:60:00", "00:21:00",
            "5", "1", "talvez", "s", "00:20:00", "0",
        ])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        recuperados = main.carregar_dados(self.arquivo)
        self.assertEqual(recuperados["corredores"], [dict(dados["corredores"][0], tempo_chegada="00:20:00")])
        self.assertEqual(recuperados["resultados"], dados["resultados"])
        self.assertEqual(resultado.stdout.count("Tempo de chegada salvo com sucesso."), 2)

    def test_sair_sem_operacoes_nao_cria_arquivo(self):
        resultado = self.executar(["0"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Inscrições aceitas: 0", resultado.stdout)
        self.assertFalse(self.arquivo.exists())


if __name__ == "__main__":
    unittest.main()
