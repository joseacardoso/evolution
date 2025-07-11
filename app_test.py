try:
    import streamlit as st
    import pandas as pd
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    st = None
    pd = None

__test__ = False
import unicodedata
from io import StringIO
if st is None or pd is None:
    def normalize(text: str) -> str:
        return str(text)
else:
    from common import calculate_plan, format_euro, produtos, setup_page
    from pathlib import Path

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


    def normalize(text: str) -> str:
        """Return lowercase text without accents."""
        return "".join(
            c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn"
        ).lower()
    
    
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
            pdf.cell(colw[2], row_height, format_euro(unit, pdf=not use_custom), border=1, align="R")
            pdf.cell(colw[3], row_height, format_euro(total, pdf=not use_custom), border=1, align="R")
            pdf.ln(row_height)
    
        valor_total = sum(t for _, _, _, t in linhas)
        pdf.set_font(font_name, "B", 10)
        pdf.cell(colw[0] + colw[1] + colw[2], 8, "Total", border=1)
        pdf.cell(colw[3], 8, format_euro(valor_total, pdf=not use_custom), border=1, align="R")
    
        return pdf.output(dest="S").encode("latin-1")
    
    st.title("Simulador de Plano PHC Evolution")
    
    
    # Área para colar tabela do Excel (opcional)
    with st.expander("Importar tabela", expanded=False):
        texto_tabela = st.text_area(
            "Cole aqui a sua tabela em formato CSV ou separado por tabulações",
            height=200,
        )
    
    import_data = {}
    web_data = {}
    utilizadores_importados = None
    plano_importado = 0  # 0=Corporate,1=Advanced,2=Enterprise
    extras_planos = {
        "intrastat": 4,
        "rgpd": 3,
        "documentos": 3,
        "genai": 2,
        "sms": 3,
        "multilingua": 2,
    }
    extras_importados = set()
    manuf_count = 0
    nao_disponiveis = set()
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
    
            manuf_count = 0
            if "Produto3" in df_import.columns:
                mask_manuf = df_import["Produto3"].str.contains("Manufactor", case=False, na=False)
                manuf_count = mask_manuf.sum()
                df_import = df_import[~mask_manuf]
    
            if "Designação" in df_import.columns:
                df_import["Designação"] = df_import["Designação"].astype(str)
            else:
                df_import["Designação"] = ""
    
            sub_col = None
            for c in ["Produto2", "Subproduto"]:
                if c in df_import.columns:
                    sub_col = c
                    break
    
            tot_por_produto = {}
            rede_por_produto = {}
            web_por_produto = {}
            inventario_flag = False
            inv_subs = {
                "equipamentos",
                "equipamento",
                "lotes",
                "grelhas",
                "localizações",
                "localizacoes",
                "ocupação",
                "ocupacao",
                "terminais",
                "terminais portateis",
                "terminais portáteis",
                "serviços",
                "servicos",
                "obras",
            }
    
            for _, row in df_import.iterrows():
                modulo_raw = str(row.get(sub_col, row["Produto"])).strip()
                quantidade = int(row["Quantidade"])
                designacao = str(row.get("Designação", "")).lower()

                tot_por_produto[modulo_raw] = tot_por_produto.get(modulo_raw, 0) + quantidade
                if "rede" in designacao:
                    rede_por_produto[modulo_raw] = rede_por_produto.get(modulo_raw, 0) + quantidade
                prod3 = str(row.get("Produto3", "")).lower()
                if "web" in designacao or "intranet" in designacao or "web" in prod3 or "intranet" in prod3:
                    web_por_produto[modulo_raw] = web_por_produto.get(modulo_raw, 0) + quantidade
                if sub_col and str(row.get(sub_col, "")).strip().lower() in inv_subs:
                    inventario_flag = True
    
            df_import = pd.DataFrame(
                {
                    "Produto": list(tot_por_produto.keys()),
                    "Quantidade": [tot_por_produto[p] for p in tot_por_produto],
                    "Rede": [rede_por_produto.get(p, 0) for p in tot_por_produto],
                    "Web": [web_por_produto.get(p, 0) for p in tot_por_produto],
                }
            )
    
            if inventario_flag:
                import_data["Inventário Avançado"] = 1

            web_mask = False
            if "Designação" in df_import.columns:
                web_mask = web_mask or df_import["Designação"].str.contains(
                    "web|intranet", case=False, na=False
                ).any()
            if "Produto3" in df_import.columns:
                web_mask = web_mask or df_import["Produto3"].astype(str).str.contains(
                    "web|intranet", case=False, na=False
                ).any()

            if web_mask:
                import_data["Documentos"] = max(import_data.get("Documentos", 0), 1)

            nome_map = {
                "careers": "Careers c/ Recrutamento",
                "imobilizado": "Imobilizado",
                "vencimentos": "Vencimento",
                "shst": "SHST",
                "ocupacao": "Ocupação",
                "ocupação": "Ocupação",
                "pos": "Ponto de Venda (POS/Restauração)",
                "restauracao": "Ponto de Venda (POS/Restauração)",
                "restauração": "Ponto de Venda (POS/Restauração)",
                "ponto de venda": "Ponto de Venda (POS/Restauração)",
                "pontos de venda": "Ponto de Venda (POS/Restauração)",
                "denuncias": "Denúncias",
                "documentos": "Documentos",
                "documentos intranet": "Documentos",
                "documentosintranet": "Documentos",
                "doceletrointranet": "Documentos",
                "doc eletro intranet": "Documentos",
                "documentosextranet": "Documentos",
                "documentos extranet": "Documentos",
                "genai": "GenAI",
                "formacao": "Formação",
                "imoveis": "Imóveis",
                "terminais portateis": "Inventário Avançado",
                "terminais portáteis": "Inventário Avançado",
                "equipamento": "Inventário Avançado",
                "suporte extranet": "Suporte",
                "suporteextranet": "Suporte",
                "suporteintranet": "Suporte",
                "suporte intranet": "Suporte",
                "orcamento": "Orçamentação",
                "medicao": "Orçamentação + Medição",
                "controlo": "Orçamentação + Medição + Controlo",
                "planeamento": "Full Project - Controlo + Medição + Orçamentação + Planeamento + Revisão de Preços",
                "revisao": "Full Project - Controlo + Medição + Orçamentação + Planeamento + Revisão de Preços",
            }
    
            modulos_validos = [m for area in produtos.values() for m in area]
    
            modulos_ignorados = {
                "doc.eletr\u00f3nicos",
                "doc.eletronicos",
                "consolidacao",
                "mrp",
                "platform",
                "planning",
                "touch",
                "qualidade",
                "sincro",
                "ecommerceb2c",
                "estacoes",
                "esta\u00e7\u00f5es",
                "clinica",
                "xl",
                "safe credit",
            }
    
            projeto_partes = set()
            projeto_qtd = 0
    
            for _, row in df_import.iterrows():
                modulo = row["Produto"].strip()
                total_mod = int(row["Quantidade"])
                rede_mod = int(row.get("Rede", 0))
                web_mod = int(row.get("Web", 0))
                quantidade = max(0, total_mod - rede_mod)
                desktop_count = max(0, quantidade - web_mod)
                if web_mod:
                    quantidade = desktop_count + max(0, web_mod - 1)
                else:
                    quantidade = desktop_count
                modulo_lower = normalize(modulo)
                if modulo_lower in ["gestao", "gestão"]:
                    utilizadores_importados = total_mod
                    continue
                if modulo_lower in modulos_ignorados:
                    if modulo_lower in {
                        "consolidacao",
                        "mrp",
                        "platform",
                        "planning",
                        "touch",
                        "qualidade",
                    }:
                        manuf_count += 1
                    elif modulo_lower in {
                        "xl",
                        "safe credit",
                        "ecommerceb2c",
                        "estacoes",
                        "esta\u00e7\u00f5es",
                        "clinica",
                    }:
                        nao_disponiveis.add(modulo)
                    continue
                modulo_nome = nome_map.get(modulo_lower, modulo)
                if modulo_nome in modulos_validos:
                    import_data[modulo_nome] = quantidade
                    if web_mod:
                        web_data[modulo_nome] = web_mod
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
    
    
    # Campos para número de utilizadores de Gestão (Desktop e Web)
    c1, c2 = st.columns(2)
    with c1:
        utilizadores_desk = st.number_input(
            "Nº Utilizadores Desktop de Gestão",
            min_value=0,
            step=1,
            format="%d",
            value=utilizadores_importados if utilizadores_importados is not None else 0,
        )
    with c2:
        utilizadores_web = st.number_input(
            "Nº Utilizadores Web de Gestão",
            min_value=0,
            step=1,
            format="%d",
        )
    utilizadores = utilizadores_desk + utilizadores_web
    
    # Captura das seleções
    selecoes = {}
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
                        if escolha in WEB_ONLY_MODULES:
                            def_web = web_data.get(escolha, 0)
                            qtd_web = st.number_input(
                                f"Nº Utilizadores Web - {escolha}",
                                min_value=0,
                                step=1,
                                format="%d",
                                value=def_web,
                            )
                            selecoes[escolha] = qtd_web
                            web_data[escolha] = qtd_web
                        elif escolha in WEB_MODULES:
                            def_total = import_data.get(escolha, 0)
                            def_web = web_data.get(escolha, 0)
                            def_desk = max(0, def_total - max(0, def_web - 1))
                            cpd, cpw = st.columns(2)
                            with cpd:
                                qtd_desk = st.number_input(
                                    f"Nº Utilizadores Desktop - {escolha}",
                                    min_value=0,
                                    step=1,
                                    format="%d",
                                    value=def_desk,
                                )
                            with cpw:
                                qtd_web = st.number_input(
                                    f"Nº Utilizadores Web - {escolha}",
                                    min_value=0,
                                    step=1,
                                    format="%d",
                                    value=def_web,
                                )
                            selecoes[escolha] = qtd_desk + qtd_web
                            web_data[escolha] = qtd_web
                        else:
                            quantidade_padrao = max(1, import_data.get(escolha, 1))
                            selecoes[escolha] = st.number_input(
                                f"Nº Utilizadores - {escolha}",
                                min_value=1,
                                step=1,
                                format="%d",
                                value=quantidade_padrao,
                            )
                            web_data.pop(escolha, None)
                    else:
                        selecoes[escolha] = 1
            else:
                for modulo, info in modulos.items():
                    ativado = st.checkbox(modulo, value=modulo in import_data)
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
                                value=import_data.get(modulo, 0),
                            )
                    elif ativado:
                        if info.get("per_user"):
                            if modulo in WEB_ONLY_MODULES:
                                def_web = web_data.get(modulo, 0)
                                qtd_web = st.number_input(
                                    f"Nº Utilizadores Web - {modulo}",
                                    min_value=0,
                                    step=1,
                                    format="%d",
                                    value=def_web,
                                    key=f"{modulo}_web",
                                )
                                selecoes[modulo] = qtd_web
                                web_data[modulo] = qtd_web
                            elif modulo in WEB_MODULES:
                                def_total = import_data.get(modulo, 0)
                                def_web = web_data.get(modulo, 0)
                                def_desk = max(0, def_total - max(0, def_web - 1))
                                cd, cw = st.columns(2)
                                with cd:
                                    qtd_desk = st.number_input(
                                        f"Nº Utilizadores Desktop - {modulo}",
                                        min_value=0,
                                        step=1,
                                        format="%d",
                                        value=def_desk,
                                        key=f"{modulo}_desk",
                                    )
                                with cw:
                                    qtd_web = st.number_input(
                                        f"Nº Utilizadores Web - {modulo}",
                                        min_value=0,
                                        step=1,
                                        format="%d",
                                        value=def_web,
                                        key=f"{modulo}_web",
                                    )
                                selecoes[modulo] = qtd_desk + qtd_web
                                web_data[modulo] = qtd_web
                            else:
                                quantidade_padrao = max(1, import_data.get(modulo, 1))
                                selecoes[modulo] = st.number_input(
                                    f"Nº Utilizadores - {modulo}",
                                    min_value=1,
                                    step=1,
                                    format="%d",
                                    value=quantidade_padrao,
                                )
                                web_data.pop(modulo, None)
                        else:
                            selecoes[modulo] = 1
    
    # Lógica do plano
    if st.button("Calcular Plano Recomendado"):
        resultado = calculate_plan(
            plano_atual,
            tipo_gestao,
            utilizadores,
            selecoes,
            web_data,
            extras_importados,
            extras_planos,
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
                            f"Preço dos {g1} Full Users (6 a 10)",
                            format_euro(g1 * p1),
                            True,
                        )
                    )
                if g2:
                    detalhes.append(
                        (
                            f"Preço dos {g2} Full Users (11 a 50)",
                            format_euro(g2 * p2),
                            True,
                        )
                    )
                if g3:
                    detalhes.append(
                        (
                            f"Preço dos {g3} Full Users (>50)",
                            format_euro(g3 * p3),
                            True,
                        )
                    )
            else:
                detalhes.append(
                    (
                        f"Preço dos {resultado['extras_utilizadores']} Full Users adicionais",
                        format_euro(resultado["custo_extra_utilizadores"]),
                        True,
                    )
                )
    
        for modulo, custos in resultado["modulos_detalhe"].items():
            custo_base, custo_desk, custo_web, qtd_desk, qtd_web = custos
            detalhes.append((modulo, format_euro(custo_base), False))
            if custo_desk > 0:
                detalhes.append(
                    (
                        f"{modulo} ({qtd_desk} Utilizadores Adicionais Desktop)",
                        format_euro(custo_desk),
                        True,
                    )
                )
            if custo_web > 0:
                detalhes.append(
                    (
                        f"{modulo} ({qtd_web} Utilizadores Adicionais Web)",
                        format_euro(custo_web),
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
    
        if "genai" in extras_importados:
            st.markdown(
                "<p style='color:#000000;'>O cliente tinha GenAI e vai evoluir para Cegid Pulse.</p>",
                unsafe_allow_html=True,
            )
        if manuf_count > 0:
            st.info(
                "O Cegid PHC CS Manufactor n\u00e3o estar\u00e1 dispon\u00edvel no Cegid PHC Evolution, e por isso n\u00e3o ser\u00e1 considerado"
            )
        if nao_disponiveis:
            lista = ", ".join(sorted(nao_disponiveis))
            st.info(
                f"Os m\u00f3dulos {lista} n\u00e3o est\u00e3o dispon\u00edveis no Cegid PHC Evolution, e por isso n\u00e3o ser\u00e3o considerados"
            )
    
        # Gera a tabela de produtos para o PDF
        linhas_pdf = []
        linhas_pdf.append((f"Plano {resultado['nome']}", 1, resultado['preco_base'], resultado['preco_base']))
        if resultado['custo_extra_utilizadores'] > 0:
            if resultado['plano_final'] == 6:
                g1, g2, g3 = resultado['extras_breakdown']
                p1, p2, p3 = resultado['precos_extras']
                if g1:
                    linhas_pdf.append(("  Full Users (6 a 10)", g1, p1, g1 * p1))
                if g2:
                    linhas_pdf.append(("  Full Users (11 a 50)", g2, p2, g2 * p2))
                if g3:
                    linhas_pdf.append(("  Full Users (>50)", g3, p3, g3 * p3))
            else:
                unit = resultado['custo_extra_utilizadores'] / resultado['extras_utilizadores']
                linhas_pdf.append(("  Full Users adicionais", resultado['extras_utilizadores'], unit, resultado['custo_extra_utilizadores']))
    
        for modulo, custos in resultado['modulos_detalhe'].items():
            custo_base, custo_desk, custo_web, qtd_desk, qtd_web = custos

            linhas_pdf.append((modulo, 1, custo_base, custo_base))

            if custo_desk > 0:
                unit_extra = custo_desk / qtd_desk if qtd_desk else custo_desk
                linhas_pdf.append(
                    (
                        f"  {modulo} ({qtd_desk} Utilizadores Adicionais Desktop)",
                        qtd_desk,
                        unit_extra,
                        custo_desk,
                    )
                )
            if custo_web > 0:
                unit_extra = custo_web / qtd_web if qtd_web else custo_web
                linhas_pdf.append(
                    (
                        f"  {modulo} ({qtd_web} Utilizadores Adicionais Web)",
                        qtd_web,
                        unit_extra,
                        custo_web,
                    )
                )
    
        pdf_bytes = gerar_pdf(linhas_pdf)
        st.download_button(
            "Descarregar Or\u00e7amento (PDF)",
            data=pdf_bytes,
            file_name="orcamento.pdf",
            mime="application/pdf",
        )
