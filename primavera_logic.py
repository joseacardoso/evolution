from __future__ import annotations

PLAN_ORDER = ["Essentials", "Standard", "Plus", "Advanced", "Premium", "Ultimate"]
PLAN_RANK = {name: idx + 1 for idx, name in enumerate(PLAN_ORDER)}

PRIMAVERA_PRICING_SOURCE = {
    "document_name": "Tabela de Preços_PT_v10Fevereiro2026.pdf",
    "document_version_available_from": "2026-02-11",
    "table_version_printed": "2026-02-13",
    "currency": "EUR",
    "prices_include_vat": False,
}

PRIMAVERA_ERP_EVOLUTION_ONPREM = {
    "billing_period": "annual",
    "plans": {
        "Essentials": {"pvp": 189, "included_users": 1, "included_companies": 1, "max_users": 1, "max_companies": 1, "additional_user_price": None, "additional_company_price": None, "activation_fee": None},
        "Standard": {"pvp": 319, "included_users": 1, "included_companies": 1, "max_users": 2, "max_companies": 2, "additional_user_price": 96, "additional_company_price": 98, "activation_fee": None},
        "Plus": {"pvp": 599, "included_users": 2, "included_companies": 2, "max_users": 3, "max_companies": 3, "additional_user_price": 120, "additional_company_price": 115, "activation_fee": 49},
        "Advanced": {"pvp": 849, "included_users": 2, "included_companies": 2, "max_users": 10, "max_companies": 10, "additional_user_price": 150, "additional_company_price": 145, "activation_fee": 49},
        "Premium": {"pvp": 1199, "included_users": 2, "included_companies": 2, "max_users": 10, "max_companies": 20, "additional_user_price": 210, "additional_company_price": 195, "activation_fee": 99},
        "Ultimate": {"pvp": 2609, "included_users": 3, "included_companies": 3, "max_users": None, "max_companies": None, "additional_user_price": 290, "additional_company_price": 265, "activation_fee": 99},
    },
}

PRIMAVERA_ERP_EVOLUTION_CLOUD = {
    "billing_period": "monthly",
    "plans": {
        "Standard": {"pvp": 50, "included_users": 1, "included_companies": 1, "max_users": 2, "max_companies": 2, "additional_user_price": 27, "additional_company_price": 11, "activation_fee": 49},
        "Plus": {"pvp": 68, "included_users": 2, "included_companies": 2, "max_users": 3, "max_companies": 3, "additional_user_price": 29, "additional_company_price": 13, "activation_fee": 99},
        "Advanced": {"pvp": 79, "included_users": 2, "included_companies": 2, "max_users": 10, "max_companies": 10, "additional_user_price": 32, "additional_company_price": 16, "activation_fee": 99},
        "Premium": {"pvp": 150, "included_users": 2, "included_companies": 2, "max_users": 20, "max_companies": 20, "additional_user_price": 37, "additional_company_price": 21, "activation_fee": 199},
    },
PRIMAVERA_PLANS = {
    1: {"name": "Essentials", "price": 189, "included_users": 1, "max_users": 1, "included_companies": 1, "max_companies": 1},
    2: {"name": "Standard", "price": 319, "included_users": 1, "max_users": 2, "included_companies": 1, "max_companies": 2},
    3: {"name": "Plus", "price": 599, "included_users": 2, "max_users": 3, "included_companies": 2, "max_companies": 3},
    4: {"name": "Advanced", "price": 849, "included_users": 2, "max_users": 10, "included_companies": 2, "max_companies": 10},
    5: {"name": "Premium", "price": 1199, "included_users": 2, "max_users": 10, "included_companies": 2, "max_companies": 20},
    6: {"name": "Ultimate", "price": 2609, "included_users": 3, "max_users": None, "included_companies": 3, "max_companies": None},
}

PRIMAVERA_ADDONS = {
    "Financeiro & Fiscal": ["Contabilidade Gestão", "Ativos", "Fiscal Reporting Manager", "Fiscal Automation"],
    "Setoriais": ["Serviços Técnicos", "Projetos e Obras", "Produção + Track&Trace", "Produção + Planeamento"],
    "Projetos Avançados": ["Pre+Orç+Plan+AMed+Ccus", "Revisão de preços"],
    "Instrumentos de Gestão": ["Gestão de contratos", "Controlo financeiro projetos"],
    "Recursos Humanos": ["RH", "Formação"],
    "Extensibilidade & Integração": ["API", "Web API", "Webhooks", "Pex Advanced", "Multi-país", "Multi-P&T Manager", "Multi-P&T Manager Advanced"],
}

PRIMAVERA_CORE_MODULE_MIN_PLAN = {
    "on_premises": {
        "Vendas": "Essentials",
        "Contas Correntes": "Essentials",
        "POS": "Essentials",
        "Inventário Avançado": "Standard",
        "Encomendas": "Standard",
        "Compras": "Plus",
        "Contactos": "Advanced",
        "OPV": "Advanced",
        "Cobranças": "Advanced",
        "Dashboards": "Premium",
    },
    "cloud": {
        "Vendas": "Standard",
        "Contas Correntes": "Standard",
        "POS": "Standard",
        "Inventário Avançado": "Standard",
        "Encomendas": "Standard",
        "Compras": "Plus",
        "Contactos": "Advanced",
        "OPV": "Advanced",
        "Cobranças": "Advanced",
        "Dashboards": "Premium",
    },
}

PRIMAVERA_ONPREM_MIN_PLAN = {
    "Contabilidade Gestão": "Premium",
    "Ativos": "Premium",
    "Fiscal Reporting Manager": "Premium",
    "Fiscal Automation": "Premium",
    "Serviços Técnicos": "Advanced",
    "Projetos e Obras": "Advanced",
    "Produção + Track&Trace": "Premium",
    "Produção + Planeamento": "Premium",
    "Pre+Orç+Plan+AMed+Ccus": "Premium",
    "Revisão de preços": "Premium",
    "Gestão de contratos": "Premium",
    "Controlo financeiro projetos": "Premium",
    "RH": "Premium",
    "Formação": "Premium",
    "API": "Advanced",
    "Web API": "Advanced",
    "Webhooks": "Advanced",
    "Pex Advanced": "Advanced",
    "Multi-país": "Advanced",
    "Multi-P&T Manager": "Essentials",
    "Multi-P&T Manager Advanced": "Essentials",
}

PRIMAVERA_CLOUD_MIN_PLAN = {
    "Contabilidade Gestão": "Premium",
    "Ativos": "Premium",
    "Fiscal Reporting Manager": "Premium",
    "RH": "Premium",
    "Serviços Técnicos": "Premium",
    "Projetos e Obras": "Premium",
    "Gestão de contratos": "Premium",
    "Controlo financeiro projetos": "Premium",
    "Formação": "Premium",
    "Web API": "Plus",
    "Webhooks": "Premium",
    "Multi-país": "Plus",
}
PRIMAVERA_CLOUD_ALLOWED = set(PRIMAVERA_CLOUD_MIN_PLAN.keys())

ONPREM_OPTIONAL_PRICES = {
    "Contabilidade Gestão": {"initial": 391, "additional": 128},
    "Ativos": {"initial": 356, "additional": 107},
    "Fiscal Reporting Manager": {"initial": 190, "additional": 57},
    "Serviços Técnicos": {"initial": 427, "additional": 131},
    "Projetos e Obras": {"initial": 275, "additional": 83},
    "Pre+Orç+Plan+AMed+Ccus": {"initial": 806, "additional": 358},
    "Revisão de preços": {"initial": 355, "additional": None},
    "Produção + Track&Trace": {"initial": 615, "additional": 387},
    "Produção + Planeamento": {"initial": 1933, "additional": 592},
    "Gestão de contratos": {"initial": 417, "additional": 124},
    "Controlo financeiro projetos": {"initial": 412, "additional": 83},
    "RH": {"initial": 534, "additional": 107},
    "Formação": {"initial": 532, "additional": 97},
    "API": {"Advanced": 299, "Premium": 399, "Ultimate": 499},
    "Web API": {"Advanced": 599, "Premium": 749, "Ultimate": 949},
    "Webhooks": {"Advanced": 135, "Premium": 135},
    "Pex Advanced": {"Advanced": 215, "Premium": 215},
    "Multi-país": {"Advanced": 192, "Premium": 273, "Ultimate": 486},
    "Multi-P&T Manager": {"initial_post": 109, "additional_post": 33},
    "Multi-P&T Manager Advanced": {"initial_post": 159, "additional_post": 48},
}

CLOUD_OPTIONAL_PRICES = {
    "Contabilidade Gestão": {"initial": 50, "additional": 31},
    "Ativos": {"initial": 42, "additional": 29},
    "Fiscal Reporting Manager": {"initial": 58, "additional": 25},
    "Serviços Técnicos": {"initial": 79, "additional": 40},
    "Projetos e Obras": {"initial": 58, "additional": 25},
    "Gestão de contratos": {"initial": 61, "additional": 30},
    "Controlo financeiro projetos": {"initial": 60, "additional": 28},
    "RH": {"initial": 50, "additional": 29},
    "Formação": {"initial": 71, "additional": 29},
    "Multi-país": {"initial": 87, "additional": 27},
    "Webhooks": {"initial": 50, "additional": 19},
    "Web API": {"initial": 79, "additional": 102},
}


def _normalize_subscription(subscription_type: str) -> str:
    return "on_premises" if subscription_type.lower() in {"onprem", "on_premises", "on-premises"} else "cloud"


def _plan_rank(plan_name: str) -> int:
    return PLAN_RANK[plan_name]


def _supports_capacity(plan: dict, users: int, companies: int) -> bool:
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


def _module_min_plan(deployment: str, module: str) -> str | None:
    if deployment == "on_premises":
        return PRIMAVERA_ONPREM_MIN_PLAN.get(module, "Ultimate")
    return PRIMAVERA_CLOUD_MIN_PLAN.get(module)


def _module_cost(deployment: str, module: str, module_users: int, plan_name: str) -> tuple[float, str | None]:
    prices = ONPREM_OPTIONAL_PRICES if deployment == "on_premises" else CLOUD_OPTIONAL_PRICES
    if module not in prices:
        return 0.0, "Preço do módulo não mapeado (mantido a 0)."
    cfg = prices[module]

    if "initial" in cfg:
        initial = cfg["initial"]
        additional = cfg.get("additional")
        if additional is None:
            return float(initial), None
        return float(initial + max(0, module_users - 1) * additional), None

    if "initial_post" in cfg:
        return float(cfg["initial_post"] + max(0, module_users - 1) * cfg["additional_post"]), None

    plan_price = cfg.get(plan_name)
    if plan_price is None:
        return 0.0, f"{module}: sem preço específico para o plano {plan_name}."
    return float(plan_price), None
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
    selected_core_modules: list[str] | None = None,
    *,
    include_activation_fee: bool = False,
) -> dict:
    """Calculate Primavera plan recommendation with 2026 pricing data."""
    deployment = _normalize_subscription(subscription_type)
    catalog = PRIMAVERA_ERP_EVOLUTION_ONPREM if deployment == "on_premises" else PRIMAVERA_ERP_EVOLUTION_CLOUD
    plans = catalog["plans"]

    warnings: list[str] = []
    blocked_modules: dict[str, str] = {}
    selected_core_modules = selected_core_modules or []

    required_rank = min(_plan_rank(p) for p in plans)
    core_min_plan = PRIMAVERA_CORE_MODULE_MIN_PLAN[deployment]
    for core_module in selected_core_modules:
        min_plan = core_min_plan.get(core_module)
        if min_plan is None:
            warnings.append(f"{core_module}: módulo base sem mapeamento de plano mínimo.")
            continue
        required_rank = max(required_rank, _plan_rank(min_plan))

    for module, module_users in selected_modules.items():
        min_plan = _module_min_plan(deployment, module)
        if min_plan is None:
            blocked_modules[module] = "Indisponível no modelo Cloud atual."
            continue
        required_rank = max(required_rank, _plan_rank(min_plan))

        if min_plan == "Advanced" and module_users > 2:
            required_rank = max(required_rank, _plan_rank("Premium"))
            warnings.append(f"{module}: Advanced suporta até 2 utilizadores por módulo; recomendado Premium.")
        if min_plan == "Premium" and module_users > 10 and deployment == "on_premises":
            required_rank = max(required_rank, _plan_rank("Ultimate"))
            warnings.append(f"{module}: Premium suporta até 10 utilizadores por módulo; recomendado Ultimate.")

    candidate_plan_name = None
    for plan_name in PLAN_ORDER:
        if plan_name not in plans:
            continue
        if _plan_rank(plan_name) < required_rank:
            continue
        if _supports_capacity(plans[plan_name], users, companies):
            candidate_plan_name = plan_name
            break

    if candidate_plan_name is None:
        candidate_plan_name = max(plans.keys(), key=_plan_rank)
        warnings.append("Capacidade acima dos limites standard; aplicado maior plano disponível.")

    plan = plans[candidate_plan_name]
    extra_users = max(0, users - plan["included_users"])
    extra_companies = max(0, companies - plan["included_companies"])
    extra_user_cost = 0.0 if plan["additional_user_price"] is None else extra_users * plan["additional_user_price"]
    extra_company_cost = 0.0 if plan["additional_company_price"] is None else extra_companies * plan["additional_company_price"]

    modules_cost = 0.0
    modules_breakdown: dict[str, float] = {}
    for module, module_users in selected_modules.items():
        if module in blocked_modules:
            continue
        price, warning = _module_cost(deployment, module, module_users, candidate_plan_name)
        modules_cost += price
        modules_breakdown[module] = price
        if warning:
            warnings.append(warning)

    activation_fee = float(plan.get("activation_fee") or 0) if include_activation_fee else 0.0
    total_price = float(plan["pvp"] + extra_user_cost + extra_company_cost + modules_cost + activation_fee)

    return {
        "deployment": deployment,
        "billing_period": catalog["billing_period"],
        "plan_id": _plan_rank(candidate_plan_name),
        "plan_name": candidate_plan_name,
        "base_price": plan["pvp"],
        "included_users": plan["included_users"],
        "included_companies": plan["included_companies"],
        "extra_users": extra_users,
        "extra_companies": extra_companies,
        "extra_user_cost": extra_user_cost,
        "extra_company_cost": extra_company_cost,
        "activation_fee": activation_fee,
        "modules_cost": modules_cost,
        "modules_breakdown": modules_breakdown,
        "total_price": total_price,
        "selected_modules": selected_modules,
        "selected_core_modules": selected_core_modules,
        "blocked_modules": blocked_modules,
        "warnings": warnings,
    }


# Backward-compatible shape used by existing UI listing (id keyed)
PRIMAVERA_PLANS = {
    PLAN_RANK[name]: {
        "name": name,
        "price": data["pvp"],
        "included_users": data["included_users"],
        "included_companies": data["included_companies"],
    }
    for name, data in PRIMAVERA_ERP_EVOLUTION_ONPREM["plans"].items()
}
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
            warnings.append(f"{module}: Advanced suporta até 2 users por módulo; recomendado Premium.")
        if module_plan == 5 and module_users > 10:
            required_plan = max(required_plan, 6)
            warnings.append(f"{module}: Premium suporta até 10 users por módulo; recomendado Ultimate.")

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
