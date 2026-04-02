# Publicar este projeto num novo repositório

Sim — o projeto está pronto para ser colocado num novo repositório.

## 1) Criar repositório vazio (GitHub)

No GitHub, cria um novo repositório (ex.: `primavera-evolution-simulator`) **sem** README inicial.

## 2) Atualizar o remote local

```bash
git remote rename origin old-origin
git remote add origin git@github.com:<teu-user>/primavera-evolution-simulator.git
```

Se preferires HTTPS:

```bash
git remote add origin https://github.com/<teu-user>/primavera-evolution-simulator.git
```

## 3) Enviar branch principal

```bash
git push -u origin HEAD:main
```

## 4) (Opcional) Publicar app no Streamlit Community Cloud

1. Ir a https://share.streamlit.io/
2. Ligar o novo repositório
3. Definir `app.py` como entrypoint
4. Deploy

## 5) Comando completo (atalho)

```bash
git remote rename origin old-origin && \
  git remote add origin git@github.com:<teu-user>/primavera-evolution-simulator.git && \
  git push -u origin HEAD:main
```

---

Se quiseres, no próximo passo eu também te deixo um `README` já pronto para esse novo repositório com descrição comercial (OnPrem vs Cloud, regras e pricing base).
