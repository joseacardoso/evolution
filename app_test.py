import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from io import StringIO
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

# Área para colar tabela do Excel (opcional)
with st.expander("Importar tabela", expanded=False):
    texto_tabela = st.text_area(
        "Cole aqui a sua tabela em formato CSV ou separado por tabulações",
        height=200,
    )

import_data = {}
utilizadores_importados = None
plano_importado = 0  # 0=Corporate,1=Advanced,2=Enterprise

if texto_tabela:
    try:
        df_import = pd.read_csv(StringIO(texto_tabela), sep=";")
        if df_import.shape[1] == 1 or "Produto" not in df_import.columns:
            df_import = pd.read_csv(StringIO(texto_tabela), sep="\t")
        if "Produto" not in df_import.columns or "Quantidade" not in df_import.columns:
            raise ValueError("missing cols")
    except Exception:
        st.error("Houve um erro na importação dos dados, por favor confirme se está correto")
        df_import = pd.DataFrame()

    if not df_import.empty:
        if "Plano" in df_import.columns:
            df_import["Plano"] = df_import["Plano"].astype(str).str.strip()
            ordem = {"corporate": 0, "advanced": 1, "enterprise": 2}
            for plano in df_import["Plano"]:
                nivel = ordem.get(str(plano).lower(), 0)
                if nivel > plano_importado:
                    plano_importado = nivel
        df_import["Produto"] = df_import["Produto"].astype(str).str.strip()
        df_import["Quantidade"] = pd.to_numeric(df_import["Quantidade"], errors="coerce").fillna(0).astype(int)
        df_import = df_import.groupby("Produto", as_index=False)["Quantidade"].sum()

        for _, row in df_import.iterrows():
            modulo = row["Produto"]
            quantidade = int(row["Quantidade"])
            if modulo.lower() in ["gestão", "gestao"]:
                utilizadores_importados = quantidade
            elif modulo in [m for area in produtos.values() for m in area]:
                import_data[modulo] = quantidade
            else:
                st.warning(f"Módulo não reconhecido: {modulo}")

plano_atual = st.selectbox(
    "Plano Atual",
    ["Corporate", "Advanced", "Enterprise"],
    index=plano_importado,
)

# Tipos de gestão (caso Corporate)
tipo_gestao = None
if plano_atual == "Corporate":
    tipo_gestao = st.selectbox(
        "Tipo de Gestão",
        ["Gestão Clientes", "Gestão Terceiros", "Gestão Completo"],
    )


# Campo para número de utilizadores de Gestão
utilizadores = st.number_input(
    "Nº de Utilizadores de Gestão",
    min_value=0,
    step=1,
    format="%d",
    value=utilizadores_importados if utilizadores_importados is not None else 0,
)

# Captura das seleções
selecoes = {}
for area, modulos in produtos.items():
    st.markdown(f"### {area}")
    for modulo in modulos:
        ativado = st.checkbox(f"{modulo}", value=modulo in import_data)
        
        if ativado:
            quantidade_padrao = import_data.get(modulo, 1)
            selecoes[modulo] = st.number_input(
                f"Nº Utilizadores - {modulo}",
                min_value=1,
                step=1,
                format="%d",
                value=quantidade_padrao,
            )

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

    csv_path = "precos_planos.csv"
    df_precos = pd.read_csv(csv_path, sep=",")

    limites = [
        (int(row["plano_id"]), row.get("limite_utilizadores"))
        for _, row in df_precos.iterrows()
    ]
    limites.sort(key=lambda x: x[0])

    plano_utilizadores = None
    for pid, limite in limites:
        if pd.notna(limite) and str(limite).strip() != "":
            if utilizadores <= int(limite):
                plano_utilizadores = pid
                break
    if plano_utilizadores is None:
        plano_utilizadores = max(pid for pid, _ in limites)

    planos.append(plano_utilizadores)

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
