from flask import Flask , request , render_template
import csv
import json
import re

app = Flask (__name__)

def carregar_dietas():
    """Carrega as dietas do arquivo CSV."""
    dietas = {}
    with open("dietas.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            dieta = row["Dieta"]
            refeicao = row["Refeição"]
            alimento = row["Alimentos"]
            if dieta not in dietas:
                dietas[dieta] = {}
            if refeicao not in dietas[dieta]:
                dietas[dieta][refeicao] = []
            dietas[dieta][refeicao].append(alimento)
    return dietas

def calcular_tmb(idade, genero, altura, peso):
    """Calcula o Gasto Metabólico Basal (TMB) usando a fórmula de Mifflin-St Jeor."""
    if genero == "Masculino":
        return (10 * peso) + (6.25 * altura * 100) - (5 * idade) + 5
    return (10 * peso) + (6.25 * altura * 100) - (5 * idade) - 161

def ajustar_calorias(tmb, objetivo):
    """Ajusta as calorias totais com base no objetivo do usuário."""
    if objetivo == "Ganhar Massa":
        return tmb + 500
    elif objetivo == "Perder Gordura":
        return tmb - 500
    return tmb

def extrair_calorias(dieta):
    """Extrai o valor numérico das calorias a partir do nome da dieta."""
    match = re.search(r"(\d+)", dieta)
    return int(match.group(1)) if match else float('inf')

def encontrar_dieta(calorias_totais, dietas):
    """Encontra a dieta mais próxima das calorias totais recomendadas."""
    melhor_dieta = min(dietas.keys(), key=lambda x: abs(extrair_calorias(x) - calorias_totais))
    return dietas[melhor_dieta]

def salvar_dados(usuario, dados):
    """Salva os dados do usuário em um arquivo JSON."""
    try:
        with open("usuarios.json", "r") as file:
            usuarios = json.load(file)
    except FileNotFoundError:
        usuarios = {}
    usuarios[usuario] = dados
    with open("usuarios.json", "w") as file:
        json.dump(usuarios, file, indent=4)

def carregar_dados(usuario):
    """Carrega os dados do usuário se existirem."""
    try:
        with open("usuarios.json", "r") as file:
            usuarios = json.load(file)
            return usuarios.get(usuario, None)
    except FileNotFoundError:
        return None
'   '
def chatbot():
    print("🤖 Olá! Vou montar uma dieta personalizada para você.\n")
    dietas = carregar_dietas()
    nome = input("Qual o seu nome? ").strip()
    dados_antigos = carregar_dados(nome)
    
    if dados_antigos:
        print("🔄 Dados encontrados! Usando informações anteriores.")
        idade = int(input(f"Qual a sua idade? (Anterior: {dados_antigos['idade']}) ") or dados_antigos['idade'])
        genero = input(f"Qual seu gênero? (Anterior: {dados_antigos['genero']}) ") or dados_antigos['genero']
        altura = float(input(f"Qual sua altura (em metros)? (Anterior: {dados_antigos['altura']}) ") or dados_antigos['altura'])
        peso = float(input(f"Qual seu peso (em kg)? (Anterior: {dados_antigos['peso']}) ") or dados_antigos['peso'])
        objetivo = input(f"Qual seu objetivo? (Anterior: {dados_antigos['objetivo']}) ") or dados_antigos['objetivo']
    else:
        idade = int(input("Qual a sua idade? "))
        genero = input("Qual seu gênero? (Masculino/Feminino) ").strip().capitalize()
        altura = float(input("Qual sua altura (em metros)? "))
        peso = float(input("Qual seu peso (em kg)? "))
        objetivo = input("Qual seu objetivo? (Ganhar Massa / Perder Gordura / Manter Peso) ").strip().capitalize()
        atividade = input("Qual seu nível de atividade física? (Sedentário / Leve / Moderado / Intenso) ").strip().capitalize()
        restricoes = input("Você possui alguma restrição alimentar? (Se sim, descreva. Se não, digite 'Não') ").strip()
        refeicoes_por_dia = int(input("Quantas refeições você faz por dia? "))
        condicoes_medicas = input("Possui alguma condição médica relevante? ").strip()

    
    tmb = calcular_tmb(idade, genero, altura, peso)
    calorias_totais = ajustar_calorias(tmb, objetivo)
    
    print(f"\n🔥 Seu Gasto Metabólico Basal é de aproximadamente {tmb:.0f} kcal.")
    print(f"📌 Para atingir seu objetivo ({objetivo}), sua ingestão calórica recomendada é de {calorias_totais:.0f} kcal.\n")
    
    dieta_recomendada = encontrar_dieta(calorias_totais, dietas)
    
    print("🍽 Sua dieta personalizada:")
    for refeicao, alimentos in dieta_recomendada.items():
        print(f"\n{refeicao}:")
        for alimento in alimentos:
            print(f"- {alimento}")
    
    salvar_dados(nome, {
        "idade": idade,
        "genero": genero,
        "altura": altura,
        "peso": peso,
        "objetivo": objetivo,
        "atividade": atividade,
        "restricoes": restricoes, 
        "refeicoes_por_dia": refeicoes_por_dia,
        "condicoes_medicas": condicoes_medicas
    })
    print("✅ Seus dados foram salvos para futuras consultas!")

chatbot()
