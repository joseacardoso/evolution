from functools import lru_cache
from pathlib import Path

import streamlit as st

from phc_logic import (  # backward compatibility exports
    BANK_PACK_PRICES,
    POS_LIMITS,
    WEB_MODULES,
    WEB_ONLY_MODULES,
    calculate_plan,
    load_precos_planos,
    load_precos_produtos,
    produtos,
)
from primavera_logic import (
    PRIMAVERA_ADDONS,
    PRIMAVERA_CLOUD_ALLOWED,
    PRIMAVERA_ONPREM_MIN_PLAN,
    PRIMAVERA_PLANS,
    calculate_primavera_plan,
)

_BASE_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def _load_style(dark: bool) -> str:
    style_file = "style_dark.css" if dark else "style.css"
    return (_BASE_DIR / style_file).read_text(encoding="utf-8")




IMAGES_DIR = _BASE_DIR / "images"
LOGO_LIGHT_PATH = IMAGES_DIR / "PHC Evolution.svg"
LOGO_DARK_PATH = IMAGES_DIR / "PHC Evolution_white.svg"


def setup_page(dark: bool = False) -> None:
    """Apply common Streamlit styling and logo."""
    style = _load_style(dark)
    logo_path = LOGO_DARK_PATH if dark else LOGO_LIGHT_PATH
    st.markdown(style, unsafe_allow_html=True)
    with open(logo_path, encoding="utf-8") as f:
        logo_svg = f.read()
    st.markdown(f'<div class="logo-container">{logo_svg}</div>', unsafe_allow_html=True)


def format_euro(valor: float, *, pdf: bool = False) -> str:
    """Return ``valor`` formatted in euros."""
    valor_str = f"{int(round(valor)):,}".replace(",", ".")
    symbol = chr(128) if pdf else "€"
    return f"{valor_str} {symbol}"


def calculate_plan(
    plano_atual: str,
    tipo_gestao: str | None,
    utilizadores_desktop: int,
    utilizadores_web: int,
    selecoes: dict[str, int],
    web_selecoes: dict[str, int] | None = None,
    extras_importados: set[str] | None = None,
    extras_planos: dict[str, int] | None = None,
    pos_counts: list[int] | None = None,
) -> dict:
    """Return planning information based on selections."""
    extras_importados = extras_importados or set()
    extras_planos = extras_planos or {}
    web_selecoes = web_selecoes or {}
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
            lim = int(limite)
            if utilizadores_desktop <= lim and utilizadores_web <= lim:
                plano_utilizadores = pid
                break
    if plano_utilizadores is None:
        plano_utilizadores = max(pid for pid, _ in limites)

    planos.append(plano_utilizadores)

    # Adjust plan based on number of POS stations
    pos_qtd = selecoes.get("Ponto de Venda (POS/Restauração)", 0)
    if pos_qtd:
        for pid in sorted(POS_LIMITS):
            limite = POS_LIMITS[pid]
            if limite is None or pos_qtd <= limite:
                planos.append(pid)
                break

    for modulo in selecoes:
        for area in produtos.values():
            if modulo in area:
                planos.append(area[modulo].get("plano"))
                break

    for extra_mod in extras_importados:
        planos.append(extras_planos.get(extra_mod, 0))

    if "Colaborador" in selecoes and "Vencimento" not in selecoes:
        warnings.append("O módulo Colaborador requer Vencimento")
    if "SHST" in selecoes and "Vencimento" not in selecoes:
        warnings.append("O módulo SHST requer Vencimento")
    if "Ocupação" in selecoes and "Inventário Avançado" not in selecoes:
        warnings.append("O módulo Ocupação faz parte do Inventário Avançado")

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

    nome, preco_base, incluidos_desk, preco_ate_10, preco_ate_50, preco_mais_50 = preco_planos[plano_final]

    incluidos_web = incluidos_desk if plano_final >= 3 else 0

    preco_produtos = {
        (row["produto"], int(row["plano_id"])): (
            float(row.get("preco_base", 0) or 0),
            float(row.get("preco_unidade", 0) or 0),
        )
        for _, row in df_produtos.iterrows()
    }

    extras_desk = max(0, utilizadores_desktop - incluidos_desk)
    extras_web = max(0, utilizadores_web - incluidos_web)
    extras = extras_desk + extras_web
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
    modulos_detalhe: dict[str, tuple[float, float, float, int, int]] = {}
    pos_breakdown = None
    bank_packs = (0, 0)

    for modulo, quantidade in selecoes.items():
        if modulo == "Bank Connector":
            extras_bancos = quantidade
            pack10 = extras_bancos // 10
            resto = extras_bancos % 10
            pack5 = 0
            if resto:
                if resto <= 5:
                    pack5 = 1
                else:
                    pack10 += 1
            bank_packs = (pack5, pack10)
            continue
        if modulo == "Ponto de Venda (POS/Restauração)":
            preco_primeiro = preco_produtos.get(("POS (1º)", plano_final), (0, 0))[0]
            preco_2_10 = preco_produtos.get(("POS (2 a 10)", plano_final), (0, 0))[1]
            preco_maior_10 = preco_produtos.get(("POS (>10)", plano_final), (0, 0))[1]

            if quantidade > 0:
                grupos = pos_counts if pos_counts is not None else [quantidade]
                extras_grupos = [max(q - 1, 0) for q in grupos]
                num_primeiros = len(grupos)
                ate_10 = sum(min(e, 9) for e in extras_grupos)
                acima_10 = sum(max(e - 9, 0) for e in extras_grupos)
                custo_base = num_primeiros * preco_primeiro
                custo_extra = ate_10 * preco_2_10 + acima_10 * preco_maior_10
                qtd_desk = ate_10 + acima_10
                pos_breakdown = (
                    num_primeiros,
                    ate_10,
                    acima_10,
                    preco_primeiro,
                    preco_2_10,
                    preco_maior_10,
                )
            else:
                custo_base = 0
                custo_extra = 0
                qtd_desk = 0
            qtd_web = 0
            custo_extra_desk = custo_extra
            custo_extra_web = 0
        else:
            base, unidade = preco_produtos.get((modulo, plano_final), (0, 0))
            custo_base = base
            if unidade and quantidade > 0:
                info = None
                for mods in produtos.values():
                    if modulo in mods:
                        info = mods[modulo]
                        break
                if info and info.get("web_only"):
                    web_total = web_selecoes.get(modulo, 0)
                    web_paid = max(0, web_total - 1)
                    desk_paid = 0
                elif modulo in WEB_MODULES:
                    web_total = web_selecoes.get(modulo, 0)
                    desk_total = quantidade - web_total
                    web_paid = max(0, web_total - 1)
                    desk_paid = max(0, desk_total - 1)
                else:
                    web_paid = 0
                    desk_paid = max(0, quantidade - 1)
                custo_extra_desk = desk_paid * unidade
                custo_extra_web = web_paid * unidade
                qtd_desk = desk_paid
                qtd_web = web_paid
            else:
                custo_extra_desk = custo_extra_web = 0
                qtd_desk = qtd_web = 0

        custo_extra = custo_extra_desk + custo_extra_web
        custo_modulos += custo_base + custo_extra
        modulos_detalhe[modulo] = (
            custo_base,
            custo_extra_desk,
            custo_extra_web,
            qtd_desk,
            qtd_web,
        )

    custo_estimado = preco_base + custo_extra_utilizadores + custo_modulos

    bancos_base = 0
    if "Bank Connector" in selecoes:
        if plano_final == 4:
            bancos_base = 1
        elif plano_final == 5:
            bancos_base = 3
        elif plano_final == 6:
            bancos_base = 5

    bancos_total = bancos_base + bank_packs[0] * 5 + bank_packs[1] * 10

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
        "bank_packs": bank_packs,
        "bancos_total": bancos_total,
        "pos_breakdown": pos_breakdown,
        "warnings": warnings,
    }

PRIMAVERA_PLANS = {
    1: {
        "name": "Essentials",
        "price": 189,
        "included_users": 1,
        "max_users": 1,
        "included_companies": 1,
        "max_companies": 1,
    },
    2: {
        "name": "Standard",
        "price": 319,
        "included_users": 1,
        "max_users": 2,
        "included_companies": 1,
        "max_companies": 2,
    },
    3: {
        "name": "Plus",
        "price": 599,
        "included_users": 2,
        "max_users": 3,
        "included_companies": 2,
        "max_companies": 3,
    },
    4: {
        "name": "Advanced",
        "price": 849,
        "included_users": 2,
        "max_users": 10,
        "included_companies": 2,
        "max_companies": 10,
    },
    5: {
        "name": "Premium",
        "price": 1199,
        "included_users": 2,
        "max_users": 10,
        "included_companies": 2,
        "max_companies": 20,
    },
    6: {
        "name": "Ultimate",
        "price": 2609,
        "included_users": 3,
        "max_users": None,
        "included_companies": 3,
        "max_companies": None,
    },
}

PRIMAVERA_ADDONS = {
    "Financeiro & Fiscal": [
        "Contabilidade Gestão",
        "Ativos",
        "Fiscal Reporting Manager",
        "Fiscal Automation",
    ],
    "Setoriais": [
        "Serviços Técnicos",
        "Projetos e Obras",
        "Produção + Track&Trace",
        "Produção + Planeamento",
    ],
    "Projetos Avançados": [
        "Pre+Orç+Plan+AMed+Ccus",
        "Revisão de preços",
    ],
    "Instrumentos de Gestão": [
        "Gestão de contratos",
        "Controlo financeiro projetos",
    ],
    "Recursos Humanos": [
        "RH",
        "Formação",
    ],
    "Extensibilidade & Integração": [
        "API",
        "Web API",
        "Webhooks",
        "Pex Advanced",
        "Multi-país",
        "Multi-P&T Manager",
        "Multi-P&T Manager Advanced",
    ],
}

# Earliest plan where each add-on is available for OnPrem subscriptions.
PRIMAVERA_ONPREM_MIN_PLAN = {
    "Contabilidade Gestão": 5,
    "Ativos": 5,
    "Fiscal Reporting Manager": 5,
    "Fiscal Automation": 5,
    "Serviços Técnicos": 4,
    "Projetos e Obras": 4,
    "Produção + Track&Trace": 5,
    "Produção + Planeamento": 5,
    "Pre+Orç+Plan+AMed+Ccus": 5,
    "Revisão de preços": 5,
    "Gestão de contratos": 5,
    "Controlo financeiro projetos": 5,
    "RH": 5,
    "Formação": 5,
    "API": 4,
    "Web API": 4,
    "Webhooks": 4,
    "Pex Advanced": 4,
    "Multi-país": 4,
    "Multi-P&T Manager": 1,
    "Multi-P&T Manager Advanced": 1,
}

# In Cloud, provided rules state availability is mostly restricted to Premium.
PRIMAVERA_CLOUD_ALLOWED = {
    "Contabilidade Gestão",
    "Ativos",
    "Fiscal Reporting Manager",
    "RH",
    "Multi-país",
    "Webhooks",
    "Web API",
}


def _supports_capacity(plan_id: int, users: int, companies: int) -> bool:
    plan = PRIMAVERA_PLANS[plan_id]
    user_ok = plan["max_users"] is None or users <= plan["max_users"]
    company_ok = plan["max_companies"] is None or companies <= plan["max_companies"]
    return user_ok and company_ok


def _module_plan_requirement(subscription_type: str, module: str) -> int | None:
    if subscription_type == "Cloud":
        if module not in PRIMAVERA_CLOUD_ALLOWED:
            return None
        return 5
    return PRIMAVERA_ONPREM_MIN_PLAN.get(module, 6)


def calculate_primavera_plan(
    subscription_type: str,
    users: int,
    companies: int,
    selected_modules: dict[str, int],
) -> dict:
    """Calculate recommended Primavera Evolution plan and availability checks."""
    warnings: list[str] = []
    blocked_modules: dict[str, str] = {}

    required_plan = 1
    for module, module_users in selected_modules.items():
        module_plan = _module_plan_requirement(subscription_type, module)
        if module_plan is None:
            blocked_modules[module] = "Indisponível no modelo Cloud atual."
            continue
        required_plan = max(required_plan, module_plan)

        if module_plan == 4 and module_users > 2:
            required_plan = max(required_plan, 5)
            warnings.append(
                f"{module}: Advanced suporta até 2 users por módulo; recomendado Premium."
            )
        if module_plan == 5 and module_users > 10:
            required_plan = max(required_plan, 6)
            warnings.append(
                f"{module}: Premium suporta até 10 users por módulo; recomendado Ultimate."
            )

    recommended_plan_id = None
    for plan_id in sorted(PRIMAVERA_PLANS):
        if plan_id < required_plan:
            continue
        if _supports_capacity(plan_id, users, companies):
            recommended_plan_id = plan_id
            break

    if recommended_plan_id is None:
        recommended_plan_id = 6
        warnings.append("Capacidade acima dos limites standard; aplicado Ultimate (ilimitado).")

    plan = PRIMAVERA_PLANS[recommended_plan_id]

    if recommended_plan_id == 4 and users > 10:
        warnings.append("Advanced: limite prático de utilizadores adicionais pode ser insuficiente.")
    if recommended_plan_id == 5 and users > 20:
        warnings.append("Premium: validar limite de utilizadores por módulo no desenho final.")

    return {
        "plan_id": recommended_plan_id,
        "plan_name": plan["name"],
        "base_price": plan["price"],
        "included_users": plan["included_users"],
        "included_companies": plan["included_companies"],
        "selected_modules": selected_modules,
        "blocked_modules": blocked_modules,
        "warnings": warnings,
    }
