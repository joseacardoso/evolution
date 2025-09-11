import types
import csv
import importlib
import sys

import pytest


class DummyPandas(types.SimpleNamespace):
    class DataFrame(list):
        def iterrows(self):
            for idx, row in enumerate(self):
                yield idx, row

    def read_csv(self, path, sep=","):
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=sep)
            return self.DataFrame([row for row in reader])

    def notna(self, value):
        return value is not None and str(value).strip() != ""


@pytest.fixture()
def common(monkeypatch):
    pd_stub = DummyPandas()
    st_stub = types.SimpleNamespace()
    monkeypatch.setitem(sys.modules, "pandas", pd_stub)
    monkeypatch.setitem(sys.modules, "streamlit", st_stub)
    import common as cm
    importlib.reload(cm)
    return cm


def read_plan_row(plan_id):
    with open("precos_planos.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=","):
            if row["plano_id"] == str(plan_id):
                return row
    raise ValueError("plan not found")


def read_module_row(product, plan_id):
    with open("precos_produtos.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=","):
            if row["produto"] == product and row["plano_id"] == str(plan_id):
                return row
    raise ValueError("module not found")


def test_plan_selection(common):
    result = common.calculate_plan("Corporate", "Gestão Completo", 1, 1, {})
    plan = read_plan_row(3)
    assert result["plano_final"] == 3
    assert result["nome"] == plan["nome"]


def test_platform_limits(common):
    result = common.calculate_plan("Corporate", "Gestão Completo", 5, 5, {})
    assert result["plano_final"] == 3


def test_platform_limit_exceeded(common):
    result = common.calculate_plan("Corporate", "Gestão Completo", 6, 5, {})
    assert result["plano_final"] == 4


def test_additional_user_pricing(common):
    result = common.calculate_plan("Advanced", None, 5, 3, {})
    plan = read_plan_row(4)
    included = int(plan["utilizadores_incluidos"])
    extra_price = float(plan["preco_extra_ate_10"])
    extras = 2
    expected_cost = extras * extra_price
    assert result["plano_final"] == 4
    assert result["extras_utilizadores"] == extras
    assert result["custo_extra_utilizadores"] == expected_cost


def test_module_costs(common):
    result = common.calculate_plan("Enterprise", None, 5, 0, {"CRM": 3})
    plan = read_plan_row(6)
    module = read_module_row("CRM", 6)
    base = float(module["preco_base"])
    unit = float(module["preco_unidade"])
    expected_module_base = base
    expected_module_extra = unit * 2
    expected_total = float(plan["preco_base"]) + expected_module_base + expected_module_extra
    assert result["modulos_detalhe"]["CRM"] == (
        expected_module_base,
        expected_module_extra,
        0,
        2,
        0,
    )
    assert result["custo_estimado"] == expected_total


def test_web_module_allocation(common):
    result = common.calculate_plan(
        "Enterprise",
        None,
        5,
        0,
        {"CRM": 12},
        {"CRM": 4},
    )
    unit = float(read_module_row("CRM", 6)["preco_unidade"])
    assert result["modulos_detalhe"]["CRM"] == (
        0,
        unit * 7,
        unit * 3,
        7,
        3,
    )


def test_web_only_module(common):
    result = common.calculate_plan(
        "Enterprise",
        None,
        5,
        0,
        {"Colaborador": 5},
        {"Colaborador": 5},
    )
    unit = float(read_module_row("Colaborador", 6)["preco_unidade"])
    assert result["modulos_detalhe"]["Colaborador"] == (
        0,
        0,
        unit * 4,
        0,
        4,
    )


def test_zero_cost_module_included(common):
    result = common.calculate_plan("Enterprise", None, 1, 0, {"Logística": 1})
    assert result["modulos_detalhe"]["Logística"] == (0, 0, 0, 0, 0)


def test_pos_plan_limit(common):
    result = common.calculate_plan(
        "Corporate",
        "Gestão Completo",
        1,
        0,
        {"Ponto de Venda (POS/Restauração)": 6},
    )
    # 6 postos requerem o plano Advanced (10 postos)
    assert result["plano_final"] == 4


def test_pos_restauracao_counts_separate(common):
    result = common.calculate_plan(
        "Enterprise",
        None,
        1,
        0,
        {"Ponto de Venda (POS/Restauração)": 4},
        pos_counts=[1, 3],
    )
    preco_primeiro = float(read_module_row("POS (1º)", 6)["preco_base"])
    preco_2_10 = float(read_module_row("POS (2 a 10)", 6)["preco_unidade"])
    detalhes = result["modulos_detalhe"]["Ponto de Venda (POS/Restauração)"]
    assert detalhes == (
        preco_primeiro * 2,
        preco_2_10 * 2,
        0,
        2,
        0,
    )
    num_primeiros, ate_10, acima_10, *_ = result["pos_breakdown"]
    assert num_primeiros == 2
    assert ate_10 == 2
    assert acima_10 == 0
