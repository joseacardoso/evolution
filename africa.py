import streamlit as st
from pathlib import Path
from copy import deepcopy
from common import calculate_plan, produtos, setup_page

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
    if tipo:
        tipo = f" {tipo}"
    else:
        tipo = ""
    if qtd == 1:
        return f"1 Utilizador Adicional{tipo}"
    return f"{qtd} Utilizadores Adicionais{tipo}"


def format_full_users(qtd: int) -> str:
    return "1 Full User" if qtd == 1 else f"{qtd} Full Users"


def format_postos(qtd: int, *, adicional: bool = False) -> str:
    label = "Posto" if qtd == 1 else "Postos"
    if adicional:
        label += " Adicional" if qtd == 1 else "s Adicionais"
    return f"{qtd} {label}" if qtd != 1 else f"1 {label}"


st.set_page_config(layout="centered")
setup_page(dark=st.get_option("theme.base") == "dark")

_FONTS_DIR = Path("fonts_dir")
_FONT_REGULAR = _FONTS_DIR / "segoeui.ttf"
_FONT_BOLD = _FONTS_DIR / "segoeuib.ttf"
_FONT_NAME = "Helvetica"
_USE_CUSTOM_FONT = False
if _FONT_REGULAR.exists() and _FONT_REGULAR.stat().st_size > 100000:
    _FONT_NAME = "SegoeUI"
    _USE_CUSTOM_FONT = True

africa_produtos = deepcopy(produtos)
africa_produtos.get("Funcionalidades Adicionais de Gestão", {}).pop("Denúncias", None)
africa_produtos.pop("Connected Services", None)

st.title("Simulador de Plano PHC Evolution - África")

pais = st.selectbox("País", ["Angola", "Moçambique"])
if pais == "Angola":
    fator = 1.25
    taxa = 1050
    moeda = "AOA"
else:
    fator = 1.20
    taxa = 75
    moeda = "MZN"

web_modules = set(WEB_MODULES)
if pais == "Angola":
    web_modules.discard("Vencimento")


def format_moeda(valor: float) -> str:
    valor_africa = int(round(valor * fator))
    valor_local = valor_africa * taxa
    valor_str = f"{int(round(valor_local)):,}".replace(",", ".")
    return f"{valor_str} {moeda}"


def gerar_pdf(linhas: list[tuple[str, int, float, float]]) -> bytes:
    """Create a simple PDF with a table of products."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()

    font_name = _FONT_NAME
    use_custom = _USE_CUSTOM_FONT
    if _USE_CUSTOM_FONT:
        pdf.add_font(font_name, "", str(_FONT_REGULAR), uni=True)
        if _FONT_BOLD.exists() and _FONT_BOLD.stat().st_size > 100000:
            pdf.add_font(font_name, "B", str(_FONT_BOLD), uni=True)

    pdf.set_font(font_name, size=12)
    pdf.cell(0, 10, "Proposta interna Cegid PHC Evolution", ln=True, align="C")
    pdf.ln(5)

    colw = [80, 20, 40, 40]
    headers = ["Produto", "Qtd", "Valor Unit.", "Total"]
    pdf.set_font(font_name, "B", 10)
    for w, h in zip(colw, headers):
        pdf.cell(w, 8, h, border=1, align="C")
    pdf.ln()
    pdf.set_font(font_name, size=10)

    for prod, qtd, unit, total in linhas:
        start_x = pdf.get_x()
        start_y = pdf.get_y()

        pdf.multi_cell(colw[0], 8, str(prod), border=1)
        row_height = pdf.get_y() - start_y

        pdf.set_xy(start_x + colw[0], start_y)
        pdf.cell(colw[1], row_height, str(qtd), border=1, align="C")
        pdf.cell(colw[2], row_height, format_moeda(unit), border=1, align="R")
        pdf.cell(colw[3], row_height, format_moeda(total), border=1, align="R")
        pdf.ln(row_height)

    valor_total = sum(t for _, _, _, t in linhas)
    pdf.set_font(font_name, "B", 10)
    pdf.cell(colw[0] + colw[1] + colw[2], 8, "Total", border=1)
    pdf.cell(colw[3], 8, format_moeda(valor_total), border=1, align="R")

    return pdf.output(dest="S").encode("latin-1")

plano_atual = st.selectbox("Plano Atual", ["Corporate", "Advanced", "Enterprise"])

tipo_gestao = None
if plano_atual == "Corporate":
    tipo_gestao = st.selectbox("Tipo de Gestão", [
        "Gestão Clientes",
        "Gestão Terceiros",
        "Gestão Completo",
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

selecoes = {}
web_selecoes = {}
for area, modulos in africa_produtos.items():
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
                    elif escolha in web_modules:
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
                        elif modulo in web_modules:
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
        f"**Previsão de Custo do Plano:** {format_moeda(resultado['custo_estimado'])}"
    )

    detalhes = []
    detalhes.append(("Preço do Plano Base", format_moeda(resultado["preco_base"]), False))
    if resultado["custo_extra_utilizadores"] > 0:
        if resultado["plano_final"] == 6:
            g1, g2, g3 = resultado["extras_breakdown"]
            p1, p2, p3 = resultado["precos_extras"]
            if g1:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g1)} (6 a 10)",
                        format_moeda(g1 * p1),
                        True,
                    )
                )
            if g2:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g2)} (11 a 50)",
                        format_moeda(g2 * p2),
                        True,
                    )
                )
            if g3:
                detalhes.append(
                    (
                        f"Preço de {format_full_users(g3)} (>50)",
                        format_moeda(g3 * p3),
                        True,
                    )
                )
        else:
            detalhes.append(
                (
                    f"Preço de {format_full_users(resultado['extras_utilizadores'])} adicional",
                    format_moeda(resultado["custo_extra_utilizadores"]),
                    True,
                )
            )

    pos_info = resultado.get("pos_breakdown")
    for modulo, custos in resultado["modulos_detalhe"].items():
        custo_base, custo_desk, custo_web, qtd_desk, qtd_web = custos
        if modulo == "Ponto de Venda (POS/Restauração)" and pos_info:
            ate_10, acima_10, preco_primeiro, preco_2_10, preco_maior_10 = pos_info
            detalhes.append(("1º Ponto de Venda (POS/Restauração)", format_moeda(preco_primeiro), False))
            if ate_10 > 0:
                total = ate_10 * preco_2_10
                detalhes.append(
                    (
                        f"Ponto de Venda (POS/Restauração) - ({format_postos(ate_10, adicional=True)} - Escalão de 2 a 10)",
                        f"{format_moeda(total)} ({format_moeda(preco_2_10)} por Posto)",
                        True,
                    )
                )
            if acima_10 > 0:
                total = acima_10 * preco_maior_10
                detalhes.append(
                    (
                        f"Ponto de Venda (POS/Restauração) - ({format_postos(acima_10, adicional=True)} - Escalão de 11 a 50)",
                        f"{format_moeda(total)} ({format_moeda(preco_maior_10)} por Posto)",
                        True,
                    )
                )
        else:
            detalhes.append((modulo, format_moeda(custo_base), False))
            if custo_desk > 0:
                texto_extra = format_additional_users(qtd_desk, "Desktop")
                unit_price = custo_desk / qtd_desk if qtd_desk else custo_desk
                detalhes.append(
                    (
                        f"{modulo} ({texto_extra})",
                        f"{format_moeda(custo_desk)} ({format_moeda(unit_price)} por Utilizador)",
                        True,
                    )
                )
            if custo_web > 0:
                unit_price = custo_web / qtd_web if qtd_web else custo_web
                detalhes.append(
                    (
                        f"{modulo} ({format_additional_users(qtd_web, 'Web')})",
                        f"{format_moeda(unit_price * qtd_web)} ({format_moeda(unit_price)} por Utilizador)",
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
        st.markdown(
            f"<p style='color:#000000;'>Bank Connector inclui {resultado['bancos_base']} banco(s) base.</p>",
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

    if "GenAI" in selecoes:
        st.markdown(
            "<p style='color:#000000;'>O cliente tinha GenAI e vai evoluir para Cegid Pulse.</p>",
            unsafe_allow_html=True,
        )

    linhas_pdf = []
    linhas_pdf.append((f"Plano {resultado['nome']}", 1, resultado['preco_base'], resultado['preco_base']))
    if resultado['custo_extra_utilizadores'] > 0:
        if resultado['plano_final'] == 6:
            g1, g2, g3 = resultado['extras_breakdown']
            p1, p2, p3 = resultado['precos_extras']
            if g1:
                linhas_pdf.append((f"  {format_full_users(g1)} (6 a 10)", g1, p1, g1 * p1))
            if g2:
                linhas_pdf.append((f"  {format_full_users(g2)} (11 a 50)", g2, p2, g2 * p2))
            if g3:
                linhas_pdf.append((f"  {format_full_users(g3)} (>50)", g3, p3, g3 * p3))
        else:
            unit = resultado['custo_extra_utilizadores'] / resultado['extras_utilizadores']
            linhas_pdf.append((f"  {format_full_users(resultado['extras_utilizadores'])} adicional", resultado['extras_utilizadores'], unit, resultado['custo_extra_utilizadores']))

    pos_info = resultado.get('pos_breakdown')
    for modulo, custos in resultado['modulos_detalhe'].items():
        custo_base, custo_desk, custo_web, qtd_desk, qtd_web = custos

        if modulo == 'Ponto de Venda (POS/Restauração)' and pos_info:
            ate_10, acima_10, preco_primeiro, preco_2_10, preco_maior_10 = pos_info
            linhas_pdf.append(("1º Ponto de Venda (POS/Restauração)", 1, preco_primeiro, preco_primeiro))
            if ate_10 > 0:
                linhas_pdf.append((
                    f"  Ponto de Venda (POS/Restauração) - ({format_postos(ate_10, adicional=True)} - Escalão de 2 a 10)",
                    ate_10,
                    preco_2_10,
                    ate_10 * preco_2_10,
                ))
            if acima_10 > 0:
                linhas_pdf.append((
                    f"  Ponto de Venda (POS/Restauração) - ({format_postos(acima_10, adicional=True)} - Escalão de 11 a 50)",
                    acima_10,
                    preco_maior_10,
                    acima_10 * preco_maior_10,
                ))
        else:
            linhas_pdf.append((modulo, 1, custo_base, custo_base))

            if custo_desk > 0:
                unit_extra = custo_desk / qtd_desk if qtd_desk else custo_desk
                texto_extra = format_additional_users(qtd_desk, 'Desktop')
                linhas_pdf.append(
                    (
                        f"  {modulo} ({texto_extra})",
                        qtd_desk,
                        unit_extra,
                        custo_desk,
                    )
                )
            if custo_web > 0:
                unit_extra = custo_web / qtd_web if qtd_web else custo_web
                linhas_pdf.append(
                    (
                        f"  {modulo} ({format_additional_users(qtd_web, 'Web')})",
                        qtd_web,
                        unit_extra,
                        custo_web,
                    )
                )

    pdf_bytes = gerar_pdf(linhas_pdf)
    st.download_button(
        "Descarregar Orçamento (PDF)",
        data=pdf_bytes,
        file_name="orcamento.pdf",
        mime="application/pdf",
    )
