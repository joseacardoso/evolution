import streamlit as st
from common import calculate_plan, format_euro, produtos, setup_page

setup_page()

st.title("Simulador de Plano PHC Evolution")
plano_atual = st.selectbox("Plano Atual", ["Corporate", "Advanced", "Enterprise"])

# Tipos de gestão (caso Corporate)
tipo_gestao = None
if plano_atual == "Corporate":
    tipo_gestao = st.selectbox("Tipo de Gestão", [
        "Gestão Clientes",
        "Gestão Terceiros",
        "Gestão Completo"
    ])

utilizadores = st.number_input("Nº de Utilizadores de Gestão", min_value=0, step=1, format="%d")

# Captura das seleções
selecoes = {}
for area, modulos in produtos.items():
    with st.expander(area, expanded=False):
        if area == "Projeto":
            opcoes = ["Nenhum"] + list(modulos.keys())
            escolha = st.radio("Selecione o módulo de Projeto", opcoes, index=0)
            if escolha != "Nenhum":
                info = modulos[escolha]
                if info.get("per_user"):
                    selecoes[escolha] = st.number_input(
                        f"Nº Utilizadores - {escolha}",
                        min_value=1,
                        step=1,
                        format="%d",
                    )
                else:
                    selecoes[escolha] = 1
        else:
            for modulo, info in modulos.items():
                ativado = st.checkbox(modulo)
                if modulo == "Bank Connector":
                    st.markdown(
                        "O Plano Advanced inclui ligação a 1 Banco, o Plano Premium a 3 Bancos e o Ultimate a 5 Bancos, se precisar de mais bancos além dos incluídos, indique o nº necessário"
                    )
                    if ativado:
                        selecoes[modulo] = st.number_input(
                            "Nº Bancos Adicionais",
                            min_value=0,
                            step=1,
                            format="%d",
                        )
                elif ativado:
                    if info.get("per_user"):
                        selecoes[modulo] = st.number_input(
                            f"Nº Utilizadores - {modulo}",
                            min_value=1,
                            step=1,
                            format="%d",
                        )
                    else:
                        selecoes[modulo] = 1

# Lógica do plano
if st.button("Calcular Plano Recomendado"):
    resultado = calculate_plan(plano_atual, tipo_gestao, utilizadores, selecoes)

    for msg in resultado["warnings"]:
        st.warning(msg)

    st.success(f"Plano PHC Evolution recomendado: {resultado['nome']}")
    st.markdown(
        f"**Previsão de Custo do Plano:** {format_euro(resultado['custo_estimado'])}"
    )

    detalhes = []
    detalhes.append(("Preço do Plano Base", format_euro(resultado["preco_base"]), False))
    if resultado["custo_extra_utilizadores"] > 0:
        detalhes.append(
            (
                f"Preço dos {resultado['extras_utilizadores']} Full Users adicionais",
                format_euro(resultado["custo_extra_utilizadores"]),
                True,
            )
        )

    for modulo, custos in resultado["modulos_detalhe"].items():
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

    if resultado["bancos_base"]:
        st.markdown(
            f"<p style='color:#000000;'>Bank Connector inclui {resultado['bancos_base']} banco(s) base.</p>",
            unsafe_allow_html=True,
        )

    if "GenAI" in selecoes:
        st.markdown(
            "<p style='color:#000000;'>O cliente tinha GenAI e vai evoluir para Cegid Pulse.</p>",
            unsafe_allow_html=True,
        )
