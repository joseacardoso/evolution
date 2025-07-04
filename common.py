import pandas as pd
import streamlit as st
from functools import lru_cache

with open("style.css", encoding="utf-8") as f:
    STYLE_LIGHT = f.read()

with open("style_dark.css", encoding="utf-8") as f:
    STYLE_DARK = f.read()

IMAGES_DIR = "images"

LOGO_LIGHT_PATH = f"{IMAGES_DIR}/PHC Evolution.svg"
LOGO_DARK_PATH = f"{IMAGES_DIR}/PHC Evolution_white.svg"


@lru_cache(maxsize=None)
def load_precos_planos() -> pd.DataFrame:
    """Load pricing table for plans with caching."""
    return pd.read_csv("precos_planos.csv", sep=",")


@lru_cache(maxsize=None)
def load_precos_produtos() -> pd.DataFrame:
    """Load pricing table for modules with caching."""
    return pd.read_csv("precos_produtos.csv", sep=",")

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
        "Equipa": {"plano": 3, "per_user": True},
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


def setup_page(dark: bool = False) -> None:
    """Apply common Streamlit styling and logo."""
    style = STYLE_DARK if dark else STYLE_LIGHT
    logo_path = LOGO_DARK_PATH if dark else LOGO_LIGHT_PATH
    st.markdown(style, unsafe_allow_html=True)
    # Streamlit can't load SVG files with ``st.image``, so read the file
    # content and embed it directly in the page.
    with open(logo_path, encoding="utf-8") as f:
        logo_svg = f.read()
    st.markdown(f'<div class="logo-container">{logo_svg}</div>', unsafe_allow_html=True)


def format_euro(valor: float, *, pdf: bool = False) -> str:
    """Return ``valor`` formatted in euros.

    The formatting uses a dot as the thousands separator followed by a
    trailing Euro symbol.  When ``pdf`` is ``True`` the Euro sign is returned
    as the Windows‑1252 code point (``chr(128)``) so that ``fpdf`` can encode
    it correctly when using the built‑in fonts.
    """

    valor_str = f"{int(round(valor)):,}".replace(",", ".")
    symbol = chr(128) if pdf else "€"
    return f"{valor_str} {symbol}"


def calculate_plan(
    plano_atual: str,
    tipo_gestao: str | None,
    utilizadores: int,
    selecoes: dict[str, int],
    extras_importados: set[str] | None = None,
    extras_planos: dict[str, int] | None = None,
) -> dict:
    """Return planning information based on selections."""
    extras_importados = extras_importados or set()
    extras_planos = extras_planos or {}
    warnings: list[str] = []

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

    df_precos = load_precos_planos()
    df_produtos = load_precos_produtos()

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
        for area in produtos.values():
            if modulo in area:
                planos.append(area[modulo].get("plano"))
                break

    for extra_mod in extras_importados:
        planos.append(extras_planos.get(extra_mod, 0))

    if "Colaborador" in selecoes and "Vencimento" not in selecoes:
        warnings.append("O módulo Colaborador requer Vencimento")

    plano_final = max(planos) if planos else 1

    preco_planos = {
        int(row["plano_id"]): (
            row["nome"],
            float(row.get("preco_base", 0) or 0),
            int(row.get("utilizadores_incluidos", 0) or 0),
            float(row.get("preco_extra_ate_10", 0))
            if str(row.get("preco_extra_ate_10", "")).strip()
            else 0,
            float(row.get("preco_extra_ate_50", 0))
            if str(row.get("preco_extra_ate_50", "")).strip()
            else 0,
            float(row.get("preco_extra_acima_50", 0))
            if str(row.get("preco_extra_acima_50", "")).strip()
            else 0,
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

    extras = max(0, utilizadores - incluidos)
    grupo1 = grupo2 = grupo3 = 0
    custo_extra_utilizadores = 0

    if extras > 0:
        if plano_final == 6:
            grupo1 = min(5, extras)
            grupo2 = min(40, max(0, extras - 5))
            grupo3 = max(0, extras - 45)
            custo_extra_utilizadores = (
                grupo1 * preco_ate_10 + grupo2 * preco_ate_50 + grupo3 * preco_mais_50
            )
        else:
            grupo1 = extras
            custo_extra_utilizadores = grupo1 * preco_ate_10

    custo_modulos = 0
    modulos_detalhe: dict[str, tuple[float, float]] = {}
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
            custo_modulos += custo_base + custo_extra
            modulos_detalhe[modulo] = (custo_base, custo_extra)

    custo_estimado = preco_base + custo_extra_utilizadores + custo_modulos

    bancos_base = 0
    if "Bank Connector" in selecoes:
        if plano_final == 4:
            bancos_base = 1
        elif plano_final == 5:
            bancos_base = 3
        elif plano_final == 6:
            bancos_base = 5

    return {
        "nome": nome,
        "preco_base": preco_base,
        "custo_estimado": custo_estimado,
        "extras_utilizadores": extras,
        "custo_extra_utilizadores": custo_extra_utilizadores,
        "extras_breakdown": (grupo1, grupo2, grupo3),
        "precos_extras": (preco_ate_10, preco_ate_50, preco_mais_50),
        "modulos_detalhe": modulos_detalhe,
        "plano_final": plano_final,
        "bancos_base": bancos_base,
        "warnings": warnings,
    }
