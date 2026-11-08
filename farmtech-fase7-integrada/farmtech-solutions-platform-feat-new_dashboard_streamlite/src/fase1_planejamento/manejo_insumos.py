import math
import csv
import os
from pathlib import Path

# Garante que o caminho funcione de qualquer pasta
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ARQUIVO_CSV = BASE_DIR / "data" / "dados_fazenda.csv"

culturas = []
areas = []
insumos_totais = []


def carregar_dados():
    """Carrega dados do arquivo CSV para as listas."""
    culturas.clear()
    areas.clear()
    insumos_totais.clear()

    if ARQUIVO_CSV.exists():
        with open(ARQUIVO_CSV, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                culturas.append(row["Cultura"])
                areas.append(float(row["Area_m2"]))
                insumos_totais.append(float(row["Insumo_L"]))


def salvar_dados():
    """Salva os dados atuais das listas no arquivo CSV."""
    with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
        fieldnames = ["Cultura", "Area_m2", "Insumo_L"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(len(culturas)):
            writer.writerow({
                "Cultura": culturas[i],
                "Area_m2": areas[i],
                "Insumo_L": insumos_totais[i],
            })


def calcular_area_cafe(comprimento, largura):
    return comprimento * largura


def calcular_area_soja(raio):
    return math.pi * (raio ** 2)


def menu():
    print("\n" + "=" * 40)
    print("   FARMTECH SOLUTIONS — MANEJO AGRÍCOLA")
    print("=" * 40)
    print("1. Entrada de Dados (Nova Cultura)")
    print("2. Saída de Dados (Relatório)")
    print("3. Atualização de Dados")
    print("4. Deleção de Dados")
    print("5. Sair do Programa")
    print("=" * 40)
    return input("Escolha uma opção: ")


def entrada_dados():
    print("\n--- Cadastro de Nova Cultura ---")
    print("1. Café (Geometria: Retângulo)")
    print("2. Soja (Geometria: Círculo/Pivô)")
    tipo = input("Escolha o tipo de cultura (1 ou 2): ")

    if tipo == "1":
        nome = "Café"
        comp = float(input("Comprimento da área (m): "))
        larg = float(input("Largura da área (m): "))
        area = calcular_area_cafe(comp, larg)

        ruas = int(input("Quantidade de ruas na lavoura: "))
        dosagem = float(input("Dosagem de Fosfato (mL por metro de rua): "))
        insumo = (comp * ruas * dosagem) / 1000

        culturas.append(nome)
        areas.append(area)
        insumos_totais.append(insumo)
        salvar_dados()
        print(f"✅ Dados de {nome} salvos com sucesso!")

    elif tipo == "2":
        nome = "Soja"
        raio = float(input("Raio do pivô central (m): "))
        area = calcular_area_soja(raio)

        dosagem_m2 = float(input("Dosagem de Defensivo (mL por m²): "))
        insumo = (area * dosagem_m2) / 1000

        culturas.append(nome)
        areas.append(area)
        insumos_totais.append(insumo)
        salvar_dados()
        print(f"✅ Dados de {nome} salvos com sucesso!")
    else:
        print("Opção inválida!")


def saida_dados():
    carregar_dados()
    if not culturas:
        print("\nNenhum dado cadastrado.")
        return

    print("\n--- Relatório de Produção ---")
    print(f"{'ID':<4} | {'Cultura':<10} | {'Área (m²)':<12} | {'Insumo (L)':<12}")
    print("-" * 45)
    for i in range(len(culturas)):
        print(f"{i:<4} | {culturas[i]:<10} | {areas[i]:<12.2f} | {insumos_totais[i]:<12.2f}")


def atualizar_dados():
    saida_dados()
    if not culturas:
        return

    try:
        idx = int(input("\nDigite o ID que deseja atualizar: "))
        if 0 <= idx < len(culturas):
            print(f"Atualizando: {culturas[idx]}")
            nova_area = float(input("Nova Área (m²): "))
            novo_insumo = float(input("Novo Insumo Total (L): "))

            areas[idx] = nova_area
            insumos_totais[idx] = novo_insumo
            salvar_dados()
            print("✅ Dados atualizados com sucesso!")
        else:
            print("ID inválido!")
    except ValueError:
        print("Entrada inválida. Digite um número.")


def deletar_dados():
    saida_dados()
    if not culturas:
        return

    try:
        idx = int(input("\nDigite o ID que deseja deletar: "))
        if 0 <= idx < len(culturas):
            removido = culturas.pop(idx)
            areas.pop(idx)
            insumos_totais.pop(idx)
            salvar_dados()
            print(f"✅ Registro de {removido} removido!")
        else:
            print("ID inválido!")
    except ValueError:
        print("Entrada inválida. Digite um número.")


def main():
    carregar_dados()
    while True:
        opcao = menu()
        if opcao == "1":
            entrada_dados()
        elif opcao == "2":
            saida_dados()
        elif opcao == "3":
            atualizar_dados()
        elif opcao == "4":
            deletar_dados()
        elif opcao == "5":
            print("Encerrando módulo de manejo agrícola.")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()