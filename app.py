# AVISO: Para executar corretamente esta aplicação Streamlit, use o seguinte comando no terminal:
# streamlit run "C:\Projeto Python PSU\SQL\SimuladorEvolution.py"

import streamlit as st
import streamlit.components.v1 as components

# Força tema claro no Streamlit
st.set_page_config(layout="centered")

# Estilo personalizado com fundo branco e tudo a preto
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI&display=swap');

        /* ========== Base global ========= */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            background-color: #FFFFFF !important;
        }

        .stApp {
            background-color: #FFFFFF !important;
        }

        /* ========== Texto padrão a preto ========= */
        body, h1, h2, h3, h4, p, label, span,
        .stCheckbox>div, .stCheckbox span, .stCheckbox label span,
        .stSelectbox label, .stNumberInput label,
        .stMarkdown span, .stMarkdown p,
        .css-1x8cf1d, .css-1v0mbdj span, .css-17eq0hr, .css-1r6slb0 {
            color: #000000 !important;
            font-weight: 500 !important;
            opacity: 1 !important;
        }

        /* ========== Inputs e campos ========= */
        .stSelectbox div[data-baseweb],
        .stNumberInput input,
        .stSelectbox [data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }

        /* ========== Botões de +/- ========= */
        .stNumberInput button {
            background-color: #FF5C35 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important;
        }

        /* ========== Botão principal ========= */
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

        /* Força branco nos filhos do botão */
        .stButton button * {
            color: #FFFFFF !important;
        }

        /* ========== Caixas de sucesso ========= */
        .stSuccess {
            background-color: #c9cfd3 !important;
            border-left: 6px solid #0046FE !important;
            color: #000000 !important;
        }

        /* ========== Logotipo ========= */
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Logo PHC original no topo com fundo branco
st.markdown("""
    <div class="logo-container">
        <img src="https://phcsoftware.com/pt/wp-content/uploads/sites/3/2023/11/logo.svg" width="220" />
    </div>
""", unsafe_allow_html=True)

# Título e inputs principais
st.title("Simulador de Plano PHC Evolution")
plano_atual = st.selectbox("Plano Atual", ["Corporate", "Advanced", "Enterprise"])

# Tipo de Gestão apenas para Corporate
tipo_gestao = None
if plano_atual == "Corporate":
    tipo_gestao = st.selectbox("Tipo de Gestão", [
        "Gestão Clientes",
        "Gestão Terceiros",
        "Gestão Completo"
    ])

utilizadores = st.number_input("Nº de Utilizadores de Gestão", min_value=0, step=1, format="%d")

# Produtos por área com planos mínimos (apenas para lógica, não exibidos)
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

# Interface de seleção por área (sem mostrar planos mínimos)
selecoes = {}
for area, modulos in produtos.items():
    st.markdown(f"### {area}")
    for modulo in modulos:
        selecoes[modulo] = st.checkbox(modulo)

# Cálculo do plano
if st.button("Calcular Plano Recomendado"):
    planos = []

    if plano_atual == "Enterprise":
        planos.append(6)
    elif plano_atual == "Advanced":
        planos.append(4)
    elif plano_atual == "Corporate":
        planos.append(1)
        # Lógica extra para tipo de gestão
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

    for modulo, ativo in selecoes.items():
        if ativo:
            plano_min = None
            for area in produtos.values():
                if modulo in area:
                    plano_min = area[modulo]
                    break
            if plano_min:
                planos.append(plano_min)

    plano_final = max(planos) if planos else 1

    nome_planos = {
        1: "Essentials",
        2: "Standard",
        3: "Plus",
        4: "Advanced",
        5: "Premium",
        6: "Ultimate"
    }

    nome = nome_planos.get(plano_final, f"Plano {plano_final}")
    st.success(f"Plano PHC Evolution recomendado: {nome}")
