import streamlit as st

if __name__ == "__main__" and not st.runtime.exists():  # pragma: no cover - CLI guard
    import sys
    import streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
    sys.exit(stcli.main())

from common import format_euro, setup_page
from primavera_logic import PRIMAVERA_ADDONS, PRIMAVERA_PLANS, calculate_primavera_plan


def render_primavera() -> None:
    st.subheader("Primavera Evolution")
    st.caption("Subscrição OnPrem e Cloud com regras de disponibilidade por plano.")

    subscription_type = st.radio("Tipo de Subscrição", ["OnPrem", "Cloud"], horizontal=True)

    c1, c2 = st.columns(2)
    with c1:
        users = st.number_input("Nº total de utilizadores", min_value=1, step=1, format="%d")
    with c2:
        companies = st.number_input("Nº de empresas", min_value=1, step=1, format="%d")

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
        )

        for warning in result["warnings"]:
            st.warning(warning)

        st.success(f"Plano Primavera Evolution recomendado: {result['plan_name']}")
        st.markdown(f"**Preço base estimado:** {format_euro(result['base_price'])}")
        st.markdown(
            f"- **Plano:** {result['plan_name']}  \n"
            f"- **Tipo:** {subscription_type}  \n"
            f"- **Utilizadores incluídos:** {result['included_users']}  \n"
            f"- **Empresas incluídas:** {result['included_companies']}"
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
    for plan_id in sorted(PRIMAVERA_PLANS):
        plan = PRIMAVERA_PLANS[plan_id]
        st.markdown(
            f"- **{plan['name']}**: {format_euro(plan['price'])} "
            f"(inclui {plan['included_users']} user(s) e {plan['included_companies']} empresa(s))"
        )


st.set_page_config(layout="centered")
setup_page(dark=st.get_option("theme.base") == "dark")
st.title("Simulador Primavera Evolution")
render_primavera()
