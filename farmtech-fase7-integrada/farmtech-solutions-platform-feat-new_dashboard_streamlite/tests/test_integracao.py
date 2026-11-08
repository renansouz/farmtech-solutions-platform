"""Testes OFFLINE: não publicam AWS, não acessam Oracle e não fingem treino YOLO."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from src.fase3_database.ingestao_oracle import (
    CSV_PADRAO, importar_leituras, ler_leituras_csv, main as main_oracle,
)
from src.fase6_vision.detector import (
    analisar_imagem, configuracao_modelo, interpretar_labels,
)
from src.fase7_alerts.mensageria_aws import (
    chave_alerta, enviar_alerta_aws, formatar_mensagem_alerta, processar_leitura,
    ultima_leitura_oracle,
)
from src.fase7_alerts.regras_alerta import avaliar_leitura, ultima_leitura_csv


class CursorFalso:
    def __init__(self):
        self.sql = ""
        self.dados = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def executemany(self, sql, dados):
        self.sql, self.dados = sql, dados


class ConexaoFalsa:
    def __init__(self):
        self.cursor_falso = CursorFalso()
        self.commit_calls = 0
        self.rollback_calls = 0

    def cursor(self):
        return self.cursor_falso

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1


class TestIntegracao(unittest.TestCase):
    def test_csv_leitura_real_e_unica(self):
        registros = ler_leituras_csv(CSV_PADRAO)
        self.assertEqual(len(registros), 6)
        self.assertEqual(registros[0]["umidade"], 58.2)
        self.assertEqual(len({r["ts_leitura"] for r in registros}), 6)

    def test_oracle_validacao_sem_gravacao(self):
        self.assertEqual(main_oracle(["--validar"]), 0)

    def test_oracle_merge_usa_commit(self):
        conexao = ConexaoFalsa()
        registros = ler_leituras_csv()[:2]
        total = importar_leituras(conexao, registros)
        self.assertEqual(total, 2)
        self.assertIn("MERGE INTO SENSORES_FARMTECH_IOT", conexao.cursor_falso.sql)
        self.assertEqual(conexao.cursor_falso.dados, registros)
        self.assertEqual(conexao.commit_calls, 1)
        self.assertEqual(conexao.rollback_calls, 0)

    def test_alertas_dependem_de_sensor_e_nao_de_texto_fixo(self):
        leitura = ultima_leitura_csv()
        self.assertEqual(leitura["timestamp"], "2025-01-02 16:00:00")
        eventos = avaliar_leitura(leitura)
        codigos = {e["codigo"] for e in eventos}
        self.assertIn("umidade_alta", codigos)
        self.assertIn("npk_baixo", codigos)
        self.assertNotIn("umidade_baixa", codigos)
        leitura.update(umidade=65, ph=6.5, nitrogenio=100,
                       fosforo=40, potassio=120, chuva=0)
        self.assertEqual(avaliar_leitura(leitura), [])

    def test_previa_aws_nao_publica(self):
        assunto, corpo, sms = formatar_mensagem_alerta(
            "Sensores", "Crítico", "Umidade 42%", "Inspecionar bomba",
        )
        self.assertIn("Umidade 42%", corpo)
        self.assertIn("Inspecionar bomba", corpo)
        self.assertTrue(len(assunto) <= 100)
        self.assertTrue(len(sms) <= 160)
        with patch.dict(os.environ, {"AWS_SNS_TOPIC_ARN": ""}):
            resultado = enviar_alerta_aws("Sensores", "Atenção", "Teste", "Ação")
        self.assertFalse(resultado["publicado"])

    def test_alerta_nao_duplicado_em_envios_reais_mockados(self):
        leitura = ultima_leitura_csv()
        with tempfile.TemporaryDirectory() as pasta:
            historico = Path(pasta) / "historico.json"
            seq = iter([{"publicado": True, "message_id": "a"},
                        {"publicado": True, "message_id": "b"}])
            with patch("src.fase7_alerts.mensageria_aws.enviar_alerta_aws",
                       side_effect=lambda *args, **kwargs: next(seq)) as mock_send:
                primeiro = processar_leitura(leitura, enviar=True, historico_path=historico)
                segundo = processar_leitura(leitura, enviar=True, historico_path=historico)
                self.assertEqual(mock_send.call_count, len(primeiro))
                self.assertTrue(all(x["status"] == "já publicado" for x in segundo))
                self.assertTrue(historico.exists())
        self.assertEqual(chave_alerta(primeiro[0]["evento"]), primeiro[0]["chave"])

    def test_oracle_como_fonte_dos_alertas(self):
        class ConexaoStub:
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
        registro = {
            "ts_leitura": datetime(2026, 11, 8, 12, 0),
            "umidade": 42, "ph": 6.1, "nitrogenio": 91,
            "fosforo": 35, "potassio": 121, "chuva": 0, "irrigacao": 1,
        }
        with patch("src.fase3_database.conexao.conectar_oracle", return_value=ConexaoStub()), \
             patch("src.fase3_database.ingestao_oracle.listar_ultimas_leituras", return_value=[registro]):
            leitura = ultima_leitura_oracle()
        self.assertEqual(leitura["timestamp"], "2026-11-08 12:00:00")
        self.assertEqual([e["codigo"] for e in avaliar_leitura(leitura)], ["umidade_baixa"])

    def test_publicacao_sns_mockada_exige_message_id(self):
        with patch.dict(os.environ, {
            "AWS_REGION": "us-east-1",
            "AWS_SNS_TOPIC_ARN": "arn:aws:sns:us-east-1:999999999999:FarmTechAlertas",
            "AWS_ACCESS_KEY_ID": "AKIA_TESTE",
            "AWS_SECRET_ACCESS_KEY": "segredo_teste",
            "AWS_SESSION_TOKEN": "",
        }), patch("boto3.Session") as mock_sessao:
            mock_sessao.return_value.client.return_value.publish.return_value = {
                "MessageId": "id_teste_001",
            }
            status = enviar_alerta_aws("IoT", "Crítico", "Umidade baixa", "Inspecionar", publicar=True)
        self.assertTrue(status["publicado"])
        self.assertEqual(status["message_id"], "id_teste_001")
        parametros = mock_sessao.return_value.client.return_value.publish.call_args.kwargs
        self.assertIn("TopicArn", parametros)
        self.assertIn("AÇÃO CORRETIVA", parametros["Message"])

    def test_yolo_necessita_best_pt(self):
        with tempfile.TemporaryDirectory() as pasta:
            with self.assertRaisesRegex(FileNotFoundError, "Checkpoint YOLO não encontrado"):
                configuracao_modelo(pesos=Path(pasta) / "nao_existe.pt")

    def test_yolo_labels_para_coordenadas(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "entrada.txt"
            arquivo.write_text("0 0.5 0.5 0.4 0.6 0.88\n1 0.2 0.2 0.1 0.1 0.91\n")
            deteccoes = interpretar_labels(arquivo, 100, 200)
            self.assertEqual(len(deteccoes), 2)
            self.assertEqual(deteccoes[0]["classe"], "garrafa")
            self.assertEqual(deteccoes[0]["box"], [30, 40, 70, 160])
            self.assertAlmostEqual(deteccoes[1]["confianca"], 0.91)

    def test_yolo_pipeline_com_subprocesso_mockado(self):
        """Verifica o adaptador de arquivos; NÃO substitui o teste com modelo real."""
        with tempfile.TemporaryDirectory() as pasta:
            raiz = Path(pasta)
            foto, pesos = raiz / "foto.png", raiz / "best.pt"
            repo = raiz / "yolov5"
            repo.mkdir()
            (repo / "detect.py").write_text("# mock")
            pesos.write_bytes(b"dummy")
            Image.new("RGB", (100, 200)).save(foto)

            def subprocesso_falso(cmd, **_):
                destino = Path(cmd[cmd.index("--project") + 1]) / "inferencia"
                (destino / "labels").mkdir(parents=True)
                (destino / "labels" / "entrada.txt").write_text("0 0.5 0.5 0.4 0.6 0.88\n")
                Image.new("RGB", (100, 200)).save(destino / "entrada.png")
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with patch("src.fase6_vision.detector.subprocess.run", side_effect=subprocesso_falso):
                saida = analisar_imagem(foto, pesos=pesos, repositorio=repo)
            self.assertEqual(saida["deteccoes"][0]["classe"], "garrafa")
            self.assertTrue(saida["imagem_anotada"].startswith(b"\x89PNG"))


if __name__ == "__main__":
    unittest.main()
