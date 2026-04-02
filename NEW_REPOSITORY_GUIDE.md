# Publicar este projeto no repositório `primavera-evolution-simulator`

Perfeito — como já criaste o repositório, basta ligar este projeto ao remote novo e fazer push.

## 1) Definir o remote `origin`

### SSH
```bash
git remote add origin git@github.com:<teu-user>/primavera-evolution-simulator.git
```

### HTTPS
```bash
git remote add origin https://github.com/<teu-user>/primavera-evolution-simulator.git
```

> Se já existir um `origin`, substitui por:
```bash
git remote set-url origin git@github.com:<teu-user>/primavera-evolution-simulator.git
```

## 2) Publicar a branch atual como `main`

```bash
git push -u origin HEAD:main
```

## 3) Publicar atualizações seguintes

```bash
git push
```

## 4) (Opcional) Publicar app no Streamlit Community Cloud

1. Ir a https://share.streamlit.io/
2. Ligar o repositório `primavera-evolution-simulator`
3. Definir `app.py` como entrypoint
4. Deploy

## Atalho (SSH)

```bash
git remote add origin git@github.com:<teu-user>/primavera-evolution-simulator.git && \
  git push -u origin HEAD:main
```
