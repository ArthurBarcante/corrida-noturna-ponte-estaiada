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

    def test_sair_sem_operacoes_nao_cria_arquivo(self):
        resultado = self.executar(["0"])
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertIn("Inscrições aceitas: 0", resultado.stdout)
        self.assertFalse(self.arquivo.exists())


if __name__ == "__main__":
    unittest.main()
