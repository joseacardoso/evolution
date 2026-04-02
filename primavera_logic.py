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
