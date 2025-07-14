import streamlit as st
from common import (
    BANK_PACK_PRICES,
    calculate_plan,
    format_euro,
    produtos,
    setup_page,
)

WEB_MODULES = {
    "CRM",
    "Suporte",
    "Equipa",
    "Careers c/ Recrutamento",
    "Vencimento",
    "Contabilidade",
    "Imobilizado",
}

WEB_ONLY_MODULES = {"Colaborador"}


def format_additional_users(qtd: int, tipo: str | None = None) -> str:
    """Return a formatted string for ``qtd`` additional users.

    ``tipo`` can be "Desktop" or "Web" to specify the user type."""
    if tipo:
        tipo = f" {tipo}"
    else:
        tipo = ""
    if qtd == 1:
        return f"1 Utilizador Adicional{tipo}"
    return f"{qtd} Utilizadores Adicionais{tipo}"


def format_full_users(qtd: int) -> str:
    """Return a formatted string for ``qtd`` Full Users."""
    return "1 Full User" if qtd == 1 else f"{qtd} Full Users"


def format_postos(qtd: int, *, adicional: bool = False) -> str:
    """Return a formatted string for ``qtd`` POS stations."""
    label = "Posto" if qtd == 1 else "Postos"
    if adicional:
        label += " Adicional" if qtd == 1 else " Adicionais"
    return f"{qtd} {label}"

st.set_page_config(layout="centered")
setup_page(dark=st.get_option("theme.base") == "dark")

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

c1, c2 = st.columns(2)
with c1:
    utilizadores_desk = st.number_input(
        "Nº Utilizadores Desktop de Gestão", min_value=0, step=1, format="%d"
    )
with c2:
    utilizadores_web = st.number_input(
        "Nº Utilizadores Web de Gestão", min_value=0, step=1, format="%d"
    )
utilizadores = utilizadores_desk + utilizadores_web

# Captura das seleções
selecoes = {}
web_selecoes = {}
for area, modulos in produtos.items():
    with st.expander(area, expanded=False):
        if area == "Projeto":
            opcoes = ["Nenhum"] + list(modulos.keys())
            escolha = st.radio("Selecione o módulo de Projeto", opcoes, index=0)
            if escolha != "Nenhum":
                info = modulos[escolha]
                if info.get("per_user"):
                    if escolha in WEB_ONLY_MODULES:
                        qtd_web = st.number_input(
                            f"Nº Utilizadores Web - {escolha}",
                            min_value=0,
                            step=1,
                            format="%d",
                            key=f"{escolha}_web",
                        )
                        selecoes[escolha] = qtd_web
                        web_selecoes[escolha] = qtd_web
                    elif escolha in WEB_MODULES:
                        cpd, cpw = st.columns(2)
                        with cpd:
                            qtd_desk = st.number_input(
                                f"Nº Utilizadores Desktop - {escolha}",
                                min_value=0,
                                step=1,
                                format="%d",
                                key=f"{escolha}_desk",
                            )
                        with cpw:
                            qtd_web = st.number_input(
                                f"Nº Utilizadores Web - {escolha}",
                                min_value=0,
                                step=1,
                                format="%d",
                                key=f"{escolha}_web",
                            )
                        selecoes[escolha] = qtd_desk + qtd_web
                        web_selecoes[escolha] = qtd_web
                    else:
                        label = (
                            f"Nº Postos - {escolha}"
                            if escolha == "Ponto de Venda (POS/Restauração)"
                            else f"Nº Utilizadores - {escolha}"
                        )
                        qtd_desk = st.number_input(
                            label,
                            min_value=0,
                            step=1,
                            format="%d",
                        )
                        selecoes[escolha] = qtd_desk
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
                        if modulo in WEB_ONLY_MODULES:
                            qtd_web = st.number_input(
                                f"Nº Utilizadores Web - {modulo}",
                                min_value=0,
                                step=1,
                                format="%d",
                                key=f"{modulo}_web",
                            )
                            selecoes[modulo] = qtd_web
                            web_selecoes[modulo] = qtd_web
                        elif modulo in WEB_MODULES:
                            cd, cw = st.columns(2)
                            with cd:
                                qtd_desk = st.number_input(
                                    f"Nº Utilizadores Desktop - {modulo}",
                                    min_value=0,
                                    step=1,
                                    format="%d",
                                    key=f"{modulo}_desk",
                                )
                            with cw:
                                qtd_web = st.number_input(
                                    f"Nº Utilizadores Web - {modulo}",
                                    min_value=0,
                                    step=1,
                                    format="%d",
                                    key=f"{modulo}_web",
                                )
                            selecoes[modulo] = qtd_desk + qtd_web
                            web_selecoes[modulo] = qtd_web
                        else:
                            label = (
                                f"Nº Postos - {modulo}"
                                if modulo == "Ponto de Venda (POS/Restauração)"
                                else f"Nº Utilizadores - {modulo}"
                            )
                            qtd_desk = st.number_input(
                                label,
                                min_value=0,
                                step=1,
                                format="%d",
                            )
                            selecoes[modulo] = qtd_desk
                    else:
                        selecoes[modulo] = 1

# Lógica do plano
if st.button("Calcular Plano Recomendado"):
    resultado = calculate_plan(
        plano_atual,
        tipo_gestao,
        utilizadores_desk,
        utilizadores_web,
        selecoes,
        web_selecoes,
    )

    for msg in resultado["warnings"]:
        st.warning(msg)

    st.success(f"Plano PHC Evolution recomendado: {resultado['nome']}")
    st.markdown(
        f"**Previsão de Custo do Plano:** {format_euro(resultado['custo_estimado'])}"
    )

    detalhes = []
    detalhes.append(("Preço do Plano Base", format_euro(resultado["preco_base"]), False))
    if resultado["custo_extra_utilizadores"] > 0:
        if resultado["plano_final"] == 6:
            g1, g2, g3 = resultado["extras_breakdown"]
            p1, p2, p3 = resultado["precos_extras"]
            if g1:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g1)} (6 a 10)",
                        format_euro(g1 * p1),
                        True,
                    )
                )
            if g2:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g2)} (11 a 50)",
                        format_euro(g2 * p2),
                        True,
                    )
                )
            if g3:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g3)} (>50)",
                        format_euro(g3 * p3),
                        True,
                    )
                )
        else:
            detalhes.append(
                (
                    f"Preço de {format_full_users(resultado['extras_utilizadores'])} adicional",
                    format_euro(resultado["custo_extra_utilizadores"]),
                    True,
                )
            )

    pos_info = resultado.get("pos_breakdown")
    for modulo, custos in resultado["modulos_detalhe"].items():
        custo_base, custo_desk, custo_web, qtd_desk, qtd_web = custos
        if modulo == "Ponto de Venda (POS/Restauração)" and pos_info:
            ate_10, acima_10, preco_primeiro, preco_2_10, preco_maior_10 = pos_info
            detalhes.append(("1º Ponto de Venda (POS/Restauração)", format_euro(preco_primeiro), False))
            if ate_10 > 0:
                total = ate_10 * preco_2_10
                detalhes.append(
                    (
                        f"Ponto de Venda (POS/Restauração) - ({format_postos(ate_10, adicional=True)} - Escalão de 2 a 10)",
                        f"{format_euro(total)} ({format_euro(preco_2_10)} por Posto)",
                        True,
                    )
                )
            if acima_10 > 0:
                total = acima_10 * preco_maior_10
                detalhes.append(
                    (
                        f"Ponto de Venda (POS/Restauração) - ({format_postos(acima_10, adicional=True)} - Escalão de 11 a 50)",
                        f"{format_euro(total)} ({format_euro(preco_maior_10)} por Posto)",
                        True,
                    )
                )
        else:
            detalhes.append((modulo, format_euro(custo_base), False))
            if custo_desk > 0:
                texto_extra = format_additional_users(qtd_desk, "Desktop")
                unit_price = custo_desk / qtd_desk if qtd_desk else custo_desk
                detalhes.append(
                    (
                        f"{modulo} ({texto_extra})",
                        f"{format_euro(custo_desk)} ({format_euro(unit_price)} por Utilizador)",
                        True,
                    )
                )
            if custo_web > 0:
                unit_price = custo_web / qtd_web if qtd_web else custo_web
                detalhes.append(
                    (
                        f"{modulo} ({format_additional_users(qtd_web, 'Web')})",
                        f"{format_euro(unit_price * qtd_web)} ({format_euro(unit_price)} por Utilizador)",
                        True,
                    )
                )

    for texto, valor, indent in detalhes:
        bullet = "" if indent else "• "
        prefix = "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" if indent else ""
        st.markdown(
            f"<p style='color:#FF5C35;'>{bullet}{prefix}{texto}: {valor}</p>",
            unsafe_allow_html=True,
        )

    if resultado["bancos_base"]:
        banco_label = "banco" if resultado["bancos_base"] == 1 else "bancos"
        st.markdown(
            f"<p style='color:#000000;'>Bank Connector inclui {resultado['bancos_base']} {banco_label} base.</p>",
            unsafe_allow_html=True,
        )
    pack5, pack10 = resultado.get("bank_packs", (0, 0))
    if pack5 or pack10:
        texto = []
        if pack5:
            texto.append(f"{pack5} Bank Connector 5")
        if pack10:
            texto.append(f"{pack10} Bank Connector 10")
        packs = " e ".join(texto)
        st.markdown(
            f"<p style='color:#000000;'>Necessário adicionar {packs} (total de {resultado['bancos_total']} bancos).</p>",
            unsafe_allow_html=True,
        )
        if pack5:
            st.markdown(
                f"<p style='color:#000000;'>Bank Connector 5: {format_euro(BANK_PACK_PRICES[5] * pack5)}</p>",
                unsafe_allow_html=True,
            )
        if pack10:
            st.markdown(
                f"<p style='color:#000000;'>Bank Connector 10: {format_euro(BANK_PACK_PRICES[10] * pack10)}</p>",
                unsafe_allow_html=True,
            )

    if "GenAI" in selecoes:
        st.markdown(
            "<p style='color:#000000;'>O cliente tinha GenAI e vai evoluir para Cegid Pulse.</p>",
            unsafe_allow_html=True,
        )
