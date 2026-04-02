from functools import lru_cache
from pathlib import Path

import streamlit as st

from phc_logic import (  # backward compatibility exports
    BANK_PACK_PRICES,
    POS_LIMITS,
    WEB_MODULES,
    WEB_ONLY_MODULES,
    calculate_plan,
    load_precos_planos,
    load_precos_produtos,
    produtos,
)
from primavera_logic import (
    PRIMAVERA_ADDONS,
    PRIMAVERA_CLOUD_ALLOWED,
    PRIMAVERA_ONPREM_MIN_PLAN,
    PRIMAVERA_PLANS,
    calculate_primavera_plan,
)

_BASE_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def _load_style(dark: bool) -> str:
    style_file = "style_dark.css" if dark else "style.css"
    return (_BASE_DIR / style_file).read_text(encoding="utf-8")


IMAGES_DIR = _BASE_DIR / "images"
LOGO_LIGHT_PATH = IMAGES_DIR / "PHC Evolution.svg"
LOGO_DARK_PATH = IMAGES_DIR / "PHC Evolution_white.svg"


def setup_page(dark: bool = False) -> None:
    """Apply common Streamlit styling and logo."""
    style = _load_style(dark)
    logo_path = LOGO_DARK_PATH if dark else LOGO_LIGHT_PATH
    st.markdown(style, unsafe_allow_html=True)
    with open(logo_path, encoding="utf-8") as f:
        logo_svg = f.read()
    st.markdown(f'<div class="logo-container">{logo_svg}</div>', unsafe_allow_html=True)


def format_euro(valor: float, *, pdf: bool = False) -> str:
    """Return ``valor`` formatted in euros."""
    valor_str = f"{int(round(valor)):,}".replace(",", ".")
    symbol = chr(128) if pdf else "€"
    return f"{valor_str} {symbol}"
