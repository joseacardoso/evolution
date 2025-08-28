# Lógica dos Planos

Este documento resume as regras utilizadas pelas aplicações `app.py` (geral) e `app_test.py` (versão de migrações) para determinar o plano PHC Evolution mais adequado e respetivos custos.

## 1. Determinação do Plano

1. **Plano base**
   - *Corporate*: começa no plano **Essentials** (id 1). Consoante o tipo de gestão selecionado acrescenta-se:
     - "Gestão Terceiros" → plano **Standard** (id 2).
     - "Gestão Completo" → plano **Plus** (id 3).
   - *Advanced*: corresponde ao plano **Advanced** (id 4).
   - *Enterprise*: corresponde ao plano **Ultimate** (id 6).

2. **Número de utilizadores**
   - Cada plano tem limites de utilizadores desktop e web (tabela `precos_planos.csv`).
   - O plano mais baixo cujo limite suporta ambos os valores é considerado. Caso nenhum limite seja suficiente, assume-se o plano de id superior.

3. **Pontos de venda (POS)**
   - Para o módulo "Ponto de Venda (POS/Restauração)" aplica-se uma tabela de limites (`POS_LIMITS`). O plano deve permitir o número total de postos indicados.

4. **Módulos adicionais**
   - Cada módulo possui um plano mínimo definido em `common.produtos`. A presença de um módulo obriga pelo menos ao respetivo plano.

5. **Extras de migração** (apenas em `app_test.py`)
   - Durante a importação de dados podem ser identificados extras do PHC CS que alteram o plano. O mapa `extras_planos` associa o nome do extra ao plano a considerar (ex.: `intrastat` → plano 4).

6. **Plano final**
   - O plano final é o valor máximo obtido de todas as regras anteriores.

## 2. Cálculo de Custos

1. **Preço base do plano**
   - Obtido de `precos_planos.csv` mediante o id do plano final.

2. **Utilizadores incluídos e adicionais**
   - Cada plano inclui um número de utilizadores desktop (e web a partir do plano Plus).
   - Utilizadores extra pagam conforme:
     - Planos até Premium: preço único por utilizador.
     - Plano Ultimate: três escalões (1–5, 6–50, >50) com preços diferentes.

3. **Módulos**
   - Para cada módulo selecionado existe um preço base e, caso o módulo seja cobrado por utilizador, um valor por cada utilizador adicional (desktop e/ou web). O primeiro utilizador é normalmente gratuito.
   - O POS tem regras específicas para o primeiro posto, para postos 2–10 e para os restantes.

4. **Bank Connector**
   - Inclui bancos base variáveis consoante o plano final (1 no Advanced, 3 no Premium e 5 no Ultimate).

## 3. Regras Extra da Aplicação de Migração

`app_test.py` permite importar tabelas provenientes do PHC CS e aplica várias heurísticas antes de chamar `calculate_plan`:

1. **Leitura e identificação do plano**
   - O ficheiro aceita colunas separadas por ponto e vírgula ou tabulação contendo, pelo menos, `Produto` e `Quantidade`.
   - Colunas opcionais `Plano` ou `Designação` são analisadas para deduzir o plano atual (Corporate, Advanced ou Enterprise).
   - A linha "Gestão" define o número de utilizadores e tenta inferir o tipo de gestão (`Gestão Clientes`, `Gestão Terceiros` ou `Gestão Completo`).

2. **Tratamento de quantidades**
   - Campos `Rede`, `Mono` e `Web` calculam os utilizadores desktop e web. No plano Corporate cada licença de rede conta como dois utilizadores; nos restantes conta como um.
   - Subprodutos como "equipamentos", "lotes", "localizações" ou "serviços" ativam automaticamente o módulo **Inventário Avançado**.
   - A presença de "web" ou "intranet" em qualquer descrição força a inclusão do módulo **Documentos**.

3. **Normalização de nomes**
   - Os produtos são convertidos para minúsculas sem acentos e mapeados via um dicionário para os módulos oficiais.
   - Partes antigas do módulo **Projeto** são combinadas para selecionar o equivalente mais completo disponível.

4. **Extras e módulos especiais**
   - Entradas que coincidam com `extras_planos` (`intrastat`, `rgpd`, `documentos`, `genai`, `sms`, `multilingua`, …) são adicionadas a `extras_importados`, podendo elevar o plano final.
   - Módulos não suportados ou pertencentes a listas de exclusão são ignorados; módulos do antigo Manufactor apenas geram um aviso. Módulos desconhecidos são sinalizados ao utilizador.

5. **Resultado**
   - Após o processamento, são calculados os utilizadores de cada módulo (desktop e web) e as respetivas seleções, que são então passadas a `calculate_plan` para determinar o plano e custos finais.

## 4. Avisos e Dependências

Ao calcular o plano podem surgir avisos se forem detetadas dependências não satisfeitas:

- O módulo **Colaborador** requer a seleção do módulo **Vencimento**.
- O módulo **SHST** requer **Vencimento**.
- O módulo **Ocupacão** faz parte do **Inventário Avançado**.

## 5. Resumo

A lógica completa encontra-se implementada na função `calculate_plan` em `common.py`. Tanto a aplicação principal como a de migração recorrem a esta função, variando apenas na origem dos dados (entrada manual vs. importação de ficheiros).

