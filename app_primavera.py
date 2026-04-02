import streamlit as st

if __name__ == "__main__" and not st.runtime.exists():  # pragma: no cover - CLI guard
    import sys
    import streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
    sys.exit(stcli.main())

from common import format_euro, setup_page
from primavera_logic import (
    PRIMAVERA_ADDONS,
    PRIMAVERA_ERP_EVOLUTION_CLOUD,
    PRIMAVERA_ERP_EVOLUTION_ONPREM,
    calculate_primavera_plan,
)


def render_primavera() -> None:
    st.subheader("Primavera Evolution")
    st.caption("Subscrição OnPrem e Cloud com regras de disponibilidade por plano.")

    subscription_type = st.radio("Tipo de Subscrição", ["OnPrem", "Cloud"], horizontal=True)

    c1, c2 = st.columns(2)
    with c1:
        users = st.number_input("Nº total de utilizadores", min_value=1, step=1, format="%d")
    with c2:
        companies = st.number_input("Nº de empresas", min_value=1, step=1, format="%d")
    include_activation_fee = st.checkbox("Incluir taxa de ativação (1ª encomenda)", value=False)

    st.markdown("### Add-ons")
    selected_modules: dict[str, int] = {}
    for category, modules in PRIMAVERA_ADDONS.items():
        with st.expander(category, expanded=False):
            for module_name in modules:
                enabled = st.checkbox(module_name, key=f"prm_mod_{module_name}")
                if enabled:
                    module_users = st.number_input(
                        f"Utilizadores do módulo - {module_name}",
                        min_value=1,
                        step=1,
                        format="%d",
                        key=f"prm_users_{module_name}",
                    )
                    selected_modules[module_name] = module_users

    if st.button("Calcular Plano Primavera", key="btn_primavera"):
        result = calculate_primavera_plan(
            subscription_type=subscription_type,
            users=users,
            companies=companies,
            selected_modules=selected_modules,
            include_activation_fee=include_activation_fee,
        )

        for warning in result["warnings"]:
            st.warning(warning)

        st.success(f"Plano Primavera Evolution recomendado: {result['plan_name']}")
        st.markdown(
            f"**Preço estimado ({'anual' if result['billing_period'] == 'annual' else 'mensal'}):** {format_euro(result['total_price'])}"
        )
        st.markdown(
            f"- **Plano:** {result['plan_name']}  \n"
            f"- **Tipo:** {subscription_type}  \n"
            f"- **Utilizadores incluídos:** {result['included_users']}  \n"
            f"- **Empresas incluídas:** {result['included_companies']}  \n"
            f"- **Base:** {format_euro(result['base_price'])}  \n"
            f"- **Extra utilizadores:** {format_euro(result['extra_user_cost'])}  \n"
            f"- **Extra empresas:** {format_euro(result['extra_company_cost'])}  \n"
            f"- **Add-ons:** {format_euro(result['modules_cost'])}  \n"
            f"- **Taxa de ativação:** {format_euro(result['activation_fee'])}"
        )

        if result["selected_modules"]:
            st.markdown("### Módulos selecionados")
            for module, module_users in result["selected_modules"].items():
                st.markdown(f"- {module}: {module_users} utilizador(es)")

        if result["blocked_modules"]:
            st.error("Alguns módulos não estão disponíveis neste tipo/plano:")
            for module, reason in result["blocked_modules"].items():
                st.markdown(f"- **{module}**: {reason}")

    st.markdown("---")
    st.markdown("### Tabela de preços base Primavera")
    catalog = (
        PRIMAVERA_ERP_EVOLUTION_ONPREM
        if subscription_type == "OnPrem"
        else PRIMAVERA_ERP_EVOLUTION_CLOUD
    )
    for plan_name, plan in catalog["plans"].items():
        st.markdown(
            f"- **{plan_name}**: {format_euro(plan['pvp'])} "
            f"(inclui {plan['included_users']} user(s) e {plan['included_companies']} empresa(s))"
        )


st.set_page_config(layout="centered")
setup_page(dark=st.get_option("theme.base") == "dark")
st.title("Simulador Primavera Evolution")
render_primavera()
