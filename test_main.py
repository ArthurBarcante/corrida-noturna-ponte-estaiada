import io
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


class TestFluxoDaSessao(unittest.TestCase):
    def test_menu_consulta_varios_e_nova_execucao_inicia_vazia(self):
        with tempfile.TemporaryDirectory() as diretorio:
            programa = Path(diretorio) / "main.py"
            shutil.copyfile(main.__file__, programa)
            entradas = [
                "1", "Maria Souza", "30", "5", "1",
                "1", "João Silva", "65", "10", "2",
                "3", "1", "3", "2",
                "2", "30", "5", "00:22:00", "0",
            ]
            primeira = subprocess.run(
                [sys.executable, str(programa)], input="\n".join(entradas) + "\n",
                capture_output=True, text=True, encoding="utf-8", timeout=10,
                cwd=diretorio, env=dict(os.environ, PYTHONUTF8="1"),
            )
            self.assertEqual(primeira.returncode, 0, primeira.stderr)
            self.assertEqual(primeira.stdout.count("Dados do corredor:"), 2)
            self.assertIn("Inscrições aceitas: 2", primeira.stdout)
            self.assertIn("Total arrecadado: R$ 140.00", primeira.stdout)
            self.assertIn("Pace médio: 4'24\"/km", primeira.stdout)
            self.assertIn("Premiado: Sim", primeira.stdout)
            segunda = subprocess.run(
                [sys.executable, str(programa)], input="3\n0\n",
                capture_output=True, text=True, encoding="utf-8", timeout=10,
                cwd=diretorio, env=dict(os.environ, PYTHONUTF8="1"),
            )
            self.assertEqual(segunda.returncode, 0, segunda.stderr)
            self.assertIn("Nenhum corredor cadastrado", segunda.stdout)
            self.assertIn("Inscrições aceitas: 0", segunda.stdout)
            self.assertEqual([p.name for p in Path(diretorio).iterdir()], ["main.py"])


if __name__ == "__main__":
    unittest.main()
