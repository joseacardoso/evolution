import types
import importlib
import sys
import csv

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
    st_stub = types.SimpleNamespace(markdown=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "pandas", pd_stub)
    monkeypatch.setitem(sys.modules, "streamlit", st_stub)
    import common as cm
    importlib.reload(cm)
    return cm


def test_primavera_onprem_reaches_premium_for_finance_modules(common):
    result = common.calculate_primavera_plan(
        subscription_type="OnPrem",
        users=4,
        companies=2,
        selected_modules={"Contabilidade Gestão": 2},
    )
    assert result["plan_name"] == "Premium"


def test_primavera_cloud_blocks_unavailable_modules(common):
    result = common.calculate_primavera_plan(
        subscription_type="Cloud",
        users=4,
        companies=2,
        selected_modules={"API": 2},
    )
    assert "API" in result["blocked_modules"]


def test_primavera_ultimate_required_for_high_module_users(common):
    result = common.calculate_primavera_plan(
        subscription_type="OnPrem",
        users=12,
        companies=3,
        selected_modules={"RH": 11},
    )
    assert result["plan_name"] == "Ultimate"
