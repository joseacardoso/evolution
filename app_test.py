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
    "Core e Transversais": {
        "Inventário Avançado": {"plano": 3, "per_user": False},
        "Frota": {"plano": 3, "per_user": False},
        "Logística": {"plano": 3, "per_user": False},
        "Denúncias": {"plano": 5, "per_user": False},
        "CRM": {"plano": 3, "per_user": True},
        "BPM": {"plano": 3, "per_user": False},
        "Ponto de Venda (POS/Restauração)": {"plano": 3, "per_user": True},
    },
    "Área Financeira e Recursos Humanos": {
        "Contabilidade": {"plano": 3, "per_user": True},
        "Ativos": {"plano": 3, "per_user": True},
        "Vencimento": {"plano": 3, "per_user": True},
        "Colaborador": {"plano": 4, "per_user": True},
        "Careers c/ Recrutamento": {"plano": 5, "per_user": True},
        "OKR": {"plano": 3, "per_user": True},
    },
    "Outros": {
        "Suporte": {"plano": 2, "per_user": True},
        "Ecommerce B2B": {"plano": 3, "per_user": False},
    },
    "Projeto": {
        "Orçamentação": {"plano": 3, "per_user": True},
        "Orçamentação + Medição": {"plano": 3, "per_user": True},
        "Orçamentação + Medição + Controlo": {"plano": 3, "per_user": True},
        "Full Project - Controlo + Medição + Orçamentação + Planeamento + Revisão de Preços": {
            "plano": 3,
            "per_user": True,
        },
    },
    "Connected Services": {
        "Bank Connector": {"plano": 4, "per_user": False},
        "EDI Broker": {"plano": 1, "per_user": False},
    },
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
bank_connector_selecionado = False
for area, modulos in produtos.items():
    st.markdown(f"### {area}")
    if area == "Projeto":
        opcoes = ["Nenhum"] + list(modulos.keys())
        escolha = st.radio(
            "Selecione o módulo de Projeto",
            opcoes,
            index=0,
        )
        if escolha != "Nenhum":
            info = modulos[escolha]
            if info.get("per_user"):
                quantidade_padrao = import_data.get(escolha, 1)
                selecoes[escolha] = st.number_input(
                    f"Nº Utilizadores - {escolha}",
                    min_value=1,
                    step=1,
                    format="%d",
                    value=quantidade_padrao,
                )
            else:
                selecoes[escolha] = 1
    else:
        for modulo, info in modulos.items():
            ativado = st.checkbox(modulo, value=modulo in import_data)
            if modulo == "Bank Connector":
                st.markdown(
                    "Advanced inclui 1 banco base | Premium 3 | Ultimate 5"
                )
                bank_connector_selecionado = ativado
            if ativado:
                if info.get("per_user"):
                    quantidade_padrao = import_data.get(modulo, 1)
                    selecoes[modulo] = st.number_input(
                        f"Nº Utilizadores - {modulo}",
                        min_value=1,
                        step=1,
                        format="%d",
                        value=quantidade_padrao,
                    )
                else:
                    selecoes[modulo] = 1

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

    for modulo in selecoes:
        plano_min = None
        for area in produtos.values():
            if modulo in area:
                info = area[modulo]
                plano_min = info.get("plano")
                break
        if plano_min:
            planos.append(plano_min)
    if "Colaborador" in selecoes and "Vencimento" not in selecoes:
        st.warning("O módulo Colaborador requer Vencimento")

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

    if bank_connector_selecionado:
        bancos_base = 0
        if plano_final == 4:
            bancos_base = 1
        elif plano_final == 5:
            bancos_base = 3
        elif plano_final == 6:
            bancos_base = 5
        if bancos_base:
            st.markdown(
                f"<p style='color:#000000;'>Bank Connector inclui {bancos_base} banco(s) base.</p>",
                unsafe_allow_html=True,
            )
