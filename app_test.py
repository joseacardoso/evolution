import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import unicodedata
from io import StringIO
import os


def normalize(text: str) -> str:
    """Return lowercase text without accents."""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn"
    ).lower()

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
@@ -73,217 +81,466 @@ st.markdown("""

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
        "Logística": {"plano": 5, "per_user": False},
        "Denúncias": {"plano": 5, "per_user": False},
        "Documentos": {"plano": 3, "per_user": False},
        "GenAI": {"plano": 2, "per_user": False},
        "CRM": {"plano": 3, "per_user": True},
        "BPM": {"plano": 5, "per_user": False},
        "Ponto de Venda (POS/Restauração)": {"plano": 1, "per_user": True},
    },
    "Área Financeira e Recursos Humanos": {
        "Contabilidade": {"plano": 3, "per_user": True},
        "Ativos": {"plano": 3, "per_user": True},
        "Vencimento": {"plano": 3, "per_user": True},
        "Colaborador": {"plano": 5, "per_user": True},
        "Careers c/ Recrutamento": {"plano": 5, "per_user": True},
        "OKR": {"plano": 4, "per_user": True},
        "Formação": {"plano": 3, "per_user": False},
        "Imóveis": {"plano": 3, "per_user": False},
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
extras_planos = {
    "intrastat": 4,
    "rgpd": 3,
    "documentos": 3,
    "genai": 2,
}
extras_importados = set()

if texto_tabela:
    try:
        df_import = pd.read_csv(StringIO(texto_tabela), sep=";")
        if df_import.shape[1] == 1 or "Produto" not in df_import.columns:
            df_import = pd.read_csv(StringIO(texto_tabela), sep="\t")
        cols = [c.strip() for c in df_import.columns]
        df_import.columns = cols
        if "Produto" not in cols or "Quantidade" not in cols:
            raise ValueError("missing cols")
    except Exception:
        st.error("Houve um erro na importação dos dados, por favor confirme se está correto")
        df_import = pd.DataFrame()

    if not df_import.empty:
        ordem = {"corporate": 0, "advanced": 1, "enterprise": 2}
        if "Plano" in df_import.columns:
            df_import["Plano"] = df_import["Plano"].astype(str).str.strip()
            for plano in df_import["Plano"]:
                nivel = ordem.get(str(plano).lower(), 0)
                if nivel > plano_importado:
                    plano_importado = nivel
        elif "Designação" in df_import.columns:
            df_import["Designação"] = df_import["Designação"].astype(str)
            for designacao in df_import["Designação"]:
                texto = str(designacao).lower()
                for nome, nivel in ordem.items():
                    if nome in texto and nivel > plano_importado:
                        plano_importado = nivel

        df_import["Produto"] = df_import["Produto"].astype(str).str.strip()
        df_import["Quantidade"] = (
            pd.to_numeric(df_import["Quantidade"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        if "Produto3" in df_import.columns:
            df_import = df_import[~df_import["Produto3"].str.contains("Manufactor", case=False, na=False)]

        if "Designação" in df_import.columns:
            df_import["Designação"] = df_import["Designação"].astype(str)
        else:
            df_import["Designação"] = ""
        tot_por_produto = {}
        rede_por_produto = {}

        for _, row in df_import.iterrows():
            modulo_raw = str(row["Produto"]).strip()
            quantidade = int(row["Quantidade"])
            designacao = str(row.get("Designação", "")).lower()

            tot_por_produto[modulo_raw] = tot_por_produto.get(modulo_raw, 0) + quantidade
            if "rede" in designacao:
                rede_por_produto[modulo_raw] = rede_por_produto.get(modulo_raw, 0) + quantidade

        df_import = pd.DataFrame(
            {
                "Produto": list(tot_por_produto.keys()),
                "Quantidade": [tot_por_produto[p] for p in tot_por_produto],
                "Rede": [rede_por_produto.get(p, 0) for p in tot_por_produto],
            }
        )

        nome_map = {
            "careers": "Careers c/ Recrutamento",
            "imobilizado": "Ativos",
            "vencimentos": "Vencimento",
            "denuncias": "Denúncias",
            "documentos": "Documentos",
            "genai": "GenAI",
            "formacao": "Formação",
            "imoveis": "Imóveis",
        }

        modulos_validos = [m for area in produtos.values() for m in area]

        modulos_ignorados = {
            "doc.eletr\u00f3nicos",
            "doc.eletronicos",
        }

        projeto_partes = set()
        projeto_qtd = 0

        for _, row in df_import.iterrows():
            modulo = row["Produto"].strip()
            total_mod = int(row["Quantidade"])
            rede_mod = int(row.get("Rede", 0))
            quantidade = max(0, total_mod - rede_mod)
            modulo_lower = normalize(modulo)
            if modulo_lower in ["gestao", "gestão"]:
                utilizadores_importados = total_mod
                continue
            if modulo_lower in modulos_ignorados:
                continue
            modulo_nome = nome_map.get(modulo_lower, modulo)
            if modulo_nome in modulos_validos:
                import_data[modulo_nome] = quantidade
            elif modulo_lower in extras_planos:
                extras_importados.add(modulo_lower)
            else:
                # captura de modulos antigos de projeto
                if "full project" in modulo_lower or modulo_lower == "projeto":
                    projeto_partes.update([
                        "orcamentacao",
                        "medicao",
                        "controlo",
                        "planeamento",
                        "revisao",
                    ])
                    projeto_qtd = max(projeto_qtd, quantidade)
                elif any(k in modulo_lower for k in ["orcament", "medic", "control", "plane", "revisa"]):
                    if "plane" in modulo_lower:
                        projeto_partes.add("planeamento")
                    if "revisa" in modulo_lower:
                        projeto_partes.add("revisao")
                    if "control" in modulo_lower:
                        projeto_partes.add("controlo")
                    if "medic" in modulo_lower:
                        projeto_partes.add("medicao")
                    if "orcament" in modulo_lower:
                        projeto_partes.add("orcamentacao")
                    projeto_qtd = max(projeto_qtd, quantidade)
                else:
                    st.warning(f"M\u00f3dulo n\u00e3o reconhecido: {modulo}")

        projeto_modulos_novos = set(produtos["Projeto"].keys())
        if not any(m in import_data for m in projeto_modulos_novos):
            destino = None
            if projeto_partes:
                if "planeamento" in projeto_partes or "revisao" in projeto_partes or len(projeto_partes) >= 4:
                    destino = "Full Project - Controlo + Medição + Orçamentação + Planeamento + Revisão de Preços"
                elif "controlo" in projeto_partes and ("orcamentacao" in projeto_partes or "medicao" in projeto_partes):
                    destino = "Orçamentação + Medição + Controlo"
                elif "medicao" in projeto_partes:
                    destino = "Orçamentação + Medição"
                elif "orcamentacao" in projeto_partes:
                    destino = "Orçamentação"
            if destino:
                import_data[destino] = projeto_qtd if projeto_qtd else 1

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
    with st.expander(area, expanded=False):
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
                        "O Plano Advanced inclui ligação a 1 Banco, o Plano Premium a 3 Bancos e o Ultimate a 5 Bancos, se precisar de mais bancos além dos incluídos, indique o nº necessário"
                    )
                    bank_connector_selecionado = ativado
                    if ativado:
                        selecoes[modulo] = st.number_input(
                            "Nº Bancos Adicionais",
                            min_value=0,
                            step=1,
                            format="%d",
                            value=import_data.get(modulo, 0),
                        )
                elif ativado:
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
    df_produtos = pd.read_csv("precos_produtos.csv", sep=",")

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
    for extra_mod in extras_importados:
        planos.append(extras_planos.get(extra_mod, 0))
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

    preco_produtos = {
        (row["produto"], int(row["plano_id"])): (
            float(row.get("preco_base", 0) or 0),
            float(row.get("preco_unidade", 0) or 0),
        )
        for _, row in df_produtos.iterrows()
    }

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

    custo_modulos = 0
    modulos_detalhe = {}
    for modulo, quantidade in selecoes.items():
        if modulo == "Ponto de Venda (POS/Restauração)":
            preco_primeiro = preco_produtos.get(("POS (1º)", plano_final), (0, 0))[0]
            preco_2_10 = preco_produtos.get(("POS (2 a 10)", plano_final), (0, 0))[1]
            preco_maior_10 = preco_produtos.get(("POS (>10)", plano_final), (0, 0))[1]

            if quantidade > 0:
                restantes = quantidade - 1
                ate_10 = min(restantes, 9)
                acima_10 = max(restantes - 9, 0)
                custo_base = preco_primeiro
                custo_extra = ate_10 * preco_2_10 + acima_10 * preco_maior_10
            else:
                custo_base = 0
                custo_extra = 0
        else:
            base, unidade = preco_produtos.get((modulo, plano_final), (0, 0))
            custo_base = base
            custo_extra = unidade * quantidade if unidade else 0

        if custo_base or custo_extra:
            custo_total = custo_base + custo_extra
            custo_modulos += custo_total
            modulos_detalhe[modulo] = (custo_base, custo_extra)

    custo_estimado = preco_base + custo_extra_utilizadores + custo_modulos

    st.success(f"Plano PHC Evolution recomendado: {nome}")
    def format_euro(valor: float) -> str:
        return f"{int(round(valor)):,}".replace(",", ".") + " €"

    st.markdown(f"**Previsão de Custo do Plano:** {format_euro(custo_estimado)}")

    detalhes = []
    detalhes.append(("Preço do Plano Base", format_euro(preco_base), False))
    if custo_extra_utilizadores > 0:
        detalhes.append(
            (f"Preço dos {extras} Full Users adicionais", format_euro(custo_extra_utilizadores), True)
        )

    for modulo, custos in modulos_detalhe.items():
        custo_base, custo_extra = custos
        detalhes.append((modulo, format_euro(custo_base), False))
        if custo_extra > 0:
            detalhes.append(
                (f"{modulo} (Utilizadores Adicionais)", format_euro(custo_extra), True)
            )

    for texto, valor, indent in detalhes:
        bullet = "" if indent else "• "
        prefix = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" if indent else ""
        st.markdown(
            f"<p style='color:#FF5C35;'>{bullet}{prefix}{texto}: {valor}</p>",
            unsafe_allow_html=True,
        )

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

    if "genai" in extras_importados:
        st.markdown(
            "<p style='color:#000000;'>O cliente tinha GenAI e vai evoluir para Cegid Pulse.</p>",
            unsafe_allow_html=True,
        )
