import streamlit as st

if __name__ == "__main__" and not st.runtime.exists():  # pragma: no cover - CLI guard
    import sys
    import streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
    sys.exit(stcli.main())

from common import setup_page

st.set_page_config(layout="centered")
setup_page(dark=st.get_option("theme.base") == "dark")
st.title("Simuladores Evolution")
st.markdown("Use apps separadas por produto:")
st.markdown("- `app_phc.py` para PHC Evolution")
st.markdown("- `app_primavera.py` para Primavera Evolution")
