import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os

# Força tema claro no Streamlit
st.set_page_config(layout="centered")

# Estilo personalizado com fundo branco e tudo a preto
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI&display=swap');

        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #FFFFFF !important;
        }

        .stApp {
            background-color: #FFFFFF !important;
        }

        body, h1, h2, h3, h4, p, label, span,
        .stCheckbox>div, .stCheckbox span, .stCheckbox label span,
        .stSelectbox label, .stNumberInput label,
        .stMarkdown span, .stMarkdown p, .stMarkdown div,
        .css-1x8cf1d, .css-1v0mbdj span, .css-17eq0hr, .css-1r6slb0 {
            color: #000000 !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }

        .stSelectbox div[data-baseweb],
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }

        .stNumberInput button {
            background-color: #FF5C35 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
        }

        .stButton>button {
            background-color: #FF5C35 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.4em 1.2em !important;
            font-weight: bold !important;
            font-size: 1rem !important;
            display: block;
            margin: 1.2em auto 1em auto !important;
            width: auto;
            max-width: 240px;
            white-space: nowrap !important;
            line-height: 1.2 !important;
        }

        .stButton>button:hover {
            background-color: #cc4829 !important;
            color: #FFFFFF !important;
            transition: background-color 0.3s ease;
        }

        .stButton button * {
            color: #FFFFFF !important;
        }

        .stSuccess {
            background-color: #c9cfd3 !important;
            border-left: 6px solid #0046FE !important;
            color: #000000 !important;
        }

        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="logo-container">
        <img src="https://phcsoftware.com/pt/wp-content/uploads/sites/3/2023/11/logo.svg" width="220" />
    </div>
""", unsafe_allow_html=True)

st.title("Simulador de Plano PHC Evolution")
plano_atual = st.selectbox("Plano Atual", ["Corporate", "Advanced", "Enterprise"])

# Tipos de gestão (caso Corporate)
tipo_gestao = None
if plano_atual == "Corporate":
    tipo_gestao = st.selectbox("Tipo de Gestão", [
        "Gestão Clientes",
        "Gestão Terceiros",
        "Gestão Completo"
    ])

utilizadores = st.number_input("Nº de Utilizadores de Gestão", min_value=0, step=1, format="%d")

# Produtos com planos mínimos
produtos = {
    "Área Financeira / RH": {
        "Contabilidade": 3,
        "Imobilizado": 3,
        "Vencimentos": 3,
        "Careers": 5,
        "Colaborador": 4
    },
    "Áreas Verticais": {
        "Suporte": 2,
        "Clínica": 3,
        "Formação": 3,
        "Projeto": 3
    },
    "Outros": {
        "CRM": 3,
        "RGPD": 3,
        "Intrastat": 4,
        "Denúncias": 5,
        "Inventário Avançado (Lotes, Grelhas, Localizações, Ocupação, etc)": 3
    }
}

# Captura das seleções
selecoes = {}
for area, modulos in produtos.items():
    st.markdown(f"### {area}")
    for modulo in modulos:
        ativado = st.checkbox(f"{modulo}")
        if ativado:
            selecoes[modulo] = st.number_input(f"Nº Utilizadores - {modulo}", min_value=1, step=1, format="%d")

# Lógica do plano
if st.button("Calcular Plano Recomendado"):
    planos = []

    if plano_atual == "Enterprise":
        planos.append(6)
    elif plano_atual == "Advanced":
        planos.append(4)
    elif plano_atual == "Corporate":
        planos.append(1)
        if tipo_gestao == "Gestão Terceiros":
            planos.append(2)
        elif tipo_gestao == "Gestão Completo":
            planos.append(3)

    if utilizadores <= 1:
        planos.append(1)
    elif utilizadores <= 2:
        planos.append(2)
    elif utilizadores <= 5:
        planos.append(3)
    elif utilizadores <= 10:
        planos.append(4)
    elif utilizadores <= 50:
        planos.append(5)
    else:
        planos.append(6)

    for modulo, num_utilizadores in selecoes.items():
        if num_utilizadores > 0:
            plano_min = None
            for area in produtos.values():
                if modulo in area:
                    plano_min = area[modulo]
                    break
            if plano_min:
                planos.append(plano_min)

    plano_final = max(planos) if planos else 1

    csv_path = "precos_planos.csv"
    df_precos = pd.read_csv(csv_path, sep=",")
    preco_planos = {
        int(row["plano_id"]): (
            row["nome"],
            float(row.get("preco_base", 0) or 0),
            int(row.get("utilizadores_incluidos", 0) or 0),
            float(row.get("preco_extra_ate_10", 0)) if str(row.get("preco_extra_ate_10", "")).strip() else 0,
            float(row.get("preco_extra_ate_50", 0)) if str(row.get("preco_extra_ate_50", "")).strip() else 0,
            float(row.get("preco_extra_acima_50", 0)) if str(row.get("preco_extra_acima_50", "")).strip() else 0
        )
        for _, row in df_precos.iterrows()
    }

    nome, preco_base, incluidos, preco_ate_10, preco_ate_50, preco_mais_50 = preco_planos[plano_final]

    custo_extra_utilizadores = 0
    extras = max(0, utilizadores - incluidos)
    grupo1 = grupo2 = grupo3 = 0

    if extras > 0:
        if plano_final == 6:
            grupo1 = min(5, extras)
            grupo2 = min(40, max(0, extras - 5))
            grupo3 = max(0, extras - 45)
            custo_extra_utilizadores = grupo1 * preco_ate_10 + grupo2 * preco_ate_50 + grupo3 * preco_mais_50
        else:
            grupo1 = extras
            custo_extra_utilizadores = grupo1 * preco_ate_10

    custo_estimado = preco_base + custo_extra_utilizadores

    st.success(f"Plano PHC Evolution recomendado: {nome}")
    st.markdown(f"**Previsão de Custo do Plano:** {custo_estimado:.2f} €")

    detalhes = []
    detalhes.append(f"Plano Base: {preco_base:.2f} €")
    if grupo1 > 0:
        detalhes.append(f"{grupo1} Utilizadores adicionais (até 10): {grupo1 * preco_ate_10:.2f} €")
    if grupo2 > 0:
        detalhes.append(f"{grupo2} Utilizadores adicionais (até 50): {grupo2 * preco_ate_50:.2f} €")
    if grupo3 > 0:
        detalhes.append(f"{grupo3} Utilizadores adicionais (mais de 50): {grupo3 * preco_mais_50:.2f} €")

    for linha in detalhes:
        st.markdown(f"<p style='color:#000000;'>• {linha}</p>", unsafe_allow_html=True)
