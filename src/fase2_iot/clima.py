import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
CIDADE = os.getenv("CIDADE_MONITORADA", "São Paulo")
UNIDADE = "metric"


def buscar_clima():
    """Busca dados da API OpenWeather ou retorna simulação se não houver chave."""
    if not API_KEY or API_KEY == "sua_chave_aqui":
        print("[MODO LOCAL/SIMULADO] Sem chave configurada no .env. Gerando dados de teste:")
        return {
            "name": CIDADE,
            "main": {"temp": 22.5, "humidity": 65},
            "weather": [{"main": "Clear", "description": "céu limpo"}],
        }

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CIDADE}&appid={API_KEY}&units={UNIDADE}&lang=pt_br"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
        print(f"[AVISO] Resposta da API: {res.status_code}")
        return None
    except Exception as e:
        print(f"[ERRO] Falha de conexão com a API de clima: {e}")
        return None


def analisar_irrigacao(dados):
    if not dados:
        print("[ERRO] Não foi possível obter dados climáticos.")
        return 0

    cidade = dados["name"]
    temp = dados["main"]["temp"]
    umidade = dados["main"]["humidity"]
    descricao = dados["weather"][0]["description"]
    tem_chuva = "rain" in dados["weather"][0]["main"].lower() or "chuva" in descricao.lower()

    print("\n" + "=" * 45)
    print(f" FARMTECH SOLUTIONS — ANÁLISE METEOROLÓGICA")
    print("=" * 45)
    print(f" Cidade: {cidade}")
    print(f" Temperatura: {temp}°C | Umidade do Ar: {umidade}%")
    print(f" Condição: {descricao.capitalize()}")
    print("-" * 45)

    if tem_chuva:
        print(" 🌧️  Chuva detectada na região.")
        print(" ❌ Recomendação: SUSPENDER irrigação.")
        codigo = 1
    elif umidade > 80:
        print(" 🌥️  Umidade relativa alta.")
        print(" ⚠️  Recomendação: Irrigação em nível reduzido.")
        codigo = 0
    else:
        print(" ☀️  Sem previsão de chuva imediata.")
        print(" ✅ Recomendação: Irrigação liberada.")
        codigo = 0

    print("=" * 45)
    print(f"Código para Serial do ESP32: {codigo}\n")
    return codigo


def main():
    dados = buscar_clima()
    analisar_irrigacao(dados)


if __name__ == "__main__":
    main()