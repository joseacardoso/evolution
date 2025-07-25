# Evolution App

This repository contains a Streamlit application.

## Setup

It is recommended to use a virtual environment with **Python 3.11**. After activating it, install the Python dependencies with:

```bash
pip install -r requirements.txt
```

Then start the app with:

```bash
streamlit run app.py
```

## Logos

Create a folder named `images` in the repository root (already added) and add the
two logo files there:

- `PHC Evolution.svg` for the light theme
- `PHC Evolution_white.svg` for the dark theme

The application will automatically pick the correct image depending on the theme
selected in Streamlit.

## Fonts

Create a folder named `fonts_dir` in the repository root and copy the `segoeui.ttf` and `segoeuib.ttf` files into it. These fonts are used when generating PDFs.

For a detailed description of the plan calculation logic see [LOGICA_PLANOS.md](LOGICA_PLANOS.md).
