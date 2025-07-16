import csv
from io import StringIO


def process_rows(text: str, plano: int) -> int:
    reader = csv.DictReader(StringIO(text), delimiter="\t")
    tot = rede = mono = web = 0
    for row in reader:
        qtd = int(row["Quantidade"])
        tot += qtd
        desc = row["Designação"].lower()
        prod3 = row.get("Produto3", "").lower()
        if "rede" in desc:
            rede += qtd
        if "mono" in desc:
            mono += qtd
        if "web" in desc or "intranet" in desc or "web" in prod3 or "intranet" in prod3:
            web += qtd
    if plano == 0:
        rede_users = rede * 2 + mono
    else:
        rede_users = rede + mono
    module_total = max(0, tot - rede - mono + rede_users)
    desktop_count = max(0, module_total - web)
    return desktop_count


def test_rede_user_noncorporate():
    text = (
        "Referência\tDesignação\tQuantidade\tProduto\tProduto2\tProduto3\n"
        "CSONDECONT20\tON: CS Desktop Enterprise Contabilidade 6a20 U.A.\t15\tContabilidade\tContabilidade\tDesktop\n"
        "CSONECONTR\tON: CS Enterprise Contabilidade Rede\t1\tContabilidade\tContabilidade\tDesktop\n"
        "CSONDECONT5\tON: CS Desktop Enterprise Contabilidade 1a5 U.A.\t4\tContabilidade\tContabilidade\tDesktop\n"
        "CSONWECONT5\tON: CS Web Enterprise Contabilidade 1a5 U.A.\t1\tContabilidade\tContabilidade\tWeb\n"
    )
    assert process_rows(text, 2) == 20


def test_rede_user_corporate():
    text = (
        "Referência\tDesignação\tQuantidade\tProduto\tProduto2\tProduto3\n"
        "CSONDECONT20\tON: CS Desktop Corporate Contabilidade 6a20 U.A.\t15\tContabilidade\tContabilidade\tDesktop\n"
        "CSONECONTR\tON: CS Corporate Contabilidade Rede\t1\tContabilidade\tContabilidade\tDesktop\n"
        "CSONDECONT5\tON: CS Desktop Corporate Contabilidade 1a5 U.A.\t4\tContabilidade\tContabilidade\tDesktop\n"
        "CSONWECONT5\tON: CS Web Corporate Contabilidade 1a5 U.A.\t1\tContabilidade\tContabilidade\tWeb\n"
    )
    assert process_rows(text, 0) == 21
