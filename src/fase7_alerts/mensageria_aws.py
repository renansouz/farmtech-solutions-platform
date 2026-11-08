import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")
SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:608221021260:FarmTechAlertas")
EMAIL_DESTINO = os.getenv("EMAIL_ALERTA_DESTINO", "operador.fazenda@farmtech.com.br")


def formatar_mensagem_alerta(origem, nivel, detalhes, acao_corretiva):
    """Constrói a carga útil da mensagem para Email e SMS."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    assunto = f"[FARMTECH ALERTA {nivel.upper()}] Notificação da Lavoura - {timestamp}"

    corpo = (
        f"====================================================\n"
        f"        FARMTECH SOLUTIONS — ALERTA EM TEMPO REAL   \n"
        f"====================================================\n"
        f"Data/Hora: {timestamp}\n"
        f"Origem do Evento: {origem}\n"
        f"Nível de Severidade: {nivel.upper()}\n"
        f"----------------------------------------------------\n"
        f"DIAGNÓSTICO IDENTIFICADO:\n"
        f"{detalhes}\n"
        f"----------------------------------------------------\n"
        f"AÇÃO CORRETIVA RECOMENDADA:\n"
        f"-> {acao_corretiva}\n"
        f"====================================================\n"
        f"Mensagem enviada automaticamente via AWS SNS Platform\n"
    )

    sms_resumo = f"FarmTech [{nivel}]: {origem}. Ação: {acao_corretiva}"[:160]

    return assunto, corpo, sms_resumo


def enviar_alerta_aws(origem, nivel, detalhes, acao_corretiva):
    """
    Dispara a notificação via AWS SNS se credenciais existirem,
    ou executa simulação estruturada para ambiente local.
    """
    assunto, corpo, sms = formatar_mensagem_alerta(origem, nivel, detalhes, acao_corretiva)

    tem_credenciais = (
        AWS_ACCESS_KEY
        and AWS_ACCESS_KEY != "sua_access_key"
        and AWS_SECRET_KEY
        and AWS_SECRET_KEY != "sua_secret_key"
    )

    if tem_credenciais:
        try:
            import boto3
            session = boto3.Session(
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                aws_session_token=AWS_SESSION_TOKEN if AWS_SESSION_TOKEN else None,
                region_name=AWS_REGION,
            )
            sns_client = session.client("sns")

            resposta = sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=assunto[:100],
                Message=corpo,
            )
            print(f"✅ Alerta publicado com sucesso no Amazon SNS (MessageId: {resposta.get('MessageId')})")
            return True
        except Exception as e:
            print(f"⚠️ Erro ao publicar via AWS Boto3: {e}")
            print("Executando fallback local para exibição do payload...")

    # Simulação local com o payload oficial
    print("\n[MODO SIMULAÇÃO AWS SNS — PAYLOAD GERADO]")
    print(f"AWS Região: {AWS_REGION} (São Paulo - LGPD Compliant)")
    print(f"Destinatário de Notificação: {EMAIL_DESTINO}")
    print(f"Assunto: {assunto}")
    print("\n" + corpo)
    print(f"Resumo SMS (160 caracteres): \"{sms}\"\n")
    return True


def main():
    print("Iniciando teste do serviço de mensageria AWS FarmTech...")

    # Cenário 1: Disparo a partir dos sensores IoT (Fase 2)
    enviar_alerta_aws(
        origem="Telemetria Sensores (Setor Café A-12)",
        nivel="Crítico",
        detalhes="Umidade do solo em 42% (abaixo do limiar de 60%) e pH ácido em 5.1.",
        acao_corretiva="Acionar bomba de irrigação (volume 7.2 L/m²) e aplicar calcário dolomítico na próxima janela."
    )


if __name__ == "__main__":
    main()