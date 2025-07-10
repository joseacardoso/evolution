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
    result = common.calculate_plan("Corporate", "Gestão Completo", 2, {})
    plan = read_plan_row(3)
    assert result["plano_final"] == 3
    assert result["nome"] == plan["nome"]


def test_additional_user_pricing(common):
    result = common.calculate_plan("Advanced", None, 8, {})
    plan = read_plan_row(4)
    included = int(plan["utilizadores_incluidos"])
    extra_price = float(plan["preco_extra_ate_10"])
    extras = 8 - included
    expected_cost = extras * extra_price
    assert result["plano_final"] == 4
    assert result["extras_utilizadores"] == extras
    assert result["custo_extra_utilizadores"] == expected_cost


def test_module_costs(common):
    result = common.calculate_plan("Enterprise", None, 5, {"CRM": 3})
    plan = read_plan_row(6)
    module = read_module_row("CRM", 6)
    base = float(module["preco_base"])
    unit = float(module["preco_unidade"])
    expected_module_base = base
    expected_module_extra = unit * 3
    expected_total = float(plan["preco_base"]) + expected_module_base + expected_module_extra
    assert result["modulos_detalhe"]["CRM"] == (
        expected_module_base,
        expected_module_extra,
        0,
        3,
        0,
    )
    assert result["custo_estimado"] == expected_total


def test_web_module_allocation(common):
    result = common.calculate_plan(
        "Enterprise",
        None,
        5,
        {"CRM": 12},
        {"CRM": 4},
    )
    unit = float(read_module_row("CRM", 6)["preco_unidade"])
    assert result["modulos_detalhe"]["CRM"] == (
        0,
        unit * 9,
        unit * 3,
        9,
        3,
    )
