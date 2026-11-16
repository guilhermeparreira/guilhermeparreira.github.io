---
name: atualizar-futmesa
description: Use quando sair um novo Campeonato Brasileiro de Futebol de Mesa (12 Toques) e for preciso incluir a edição na base de dados e atualizar a seção Futmesa do site (por exemplo, "atualiza o Futmesa com o Brasileiro de 2026").
argument-hint: <ano> [caminho do PDF]
---

# Atualizar o Futmesa com uma nova edição do Brasileiro

Inclui uma nova edição do Campeonato Brasileiro Individual (12 Toques) na base e atualiza o site.
Pedido do usuário: $ARGUMENTS (se o ano não vier, pergunte; o próximo esperado é 2026).

São dois repositórios, nesta ordem:

1. `../futmesa-brasileirao` — lê o PDF e gera a base (`saida/`). É o único lugar onde dado é corrigido.
2. Este repositório — só consome a base e apresenta. Nunca corrija dado aqui.

## Antes de começar

Confirme com o usuário, numa pergunta só, o que faltar:

- o **PDF** com a classificação da nova edição (histórico atualizado da CBFM ou PDF avulso do campeonato) e o caminho dele;
- **cidade, UF, local, datas** e, se houver, o **número de participantes informado** pela organização.

O PDF fica fora do git. Leia `../futmesa-brasileirao/CLAUDE.md` e o `README.md` de lá antes de mexer.

## Parte 1 — Base de dados (`../futmesa-brasileirao`)

1. Acrescente a linha da edição em `dados/campeonatos.csv` (ano, edição, cidade, UF, local, datas, participantes).
2. Rode o pipeline só para o ano novo (os outros anos são mantidos):
   - histórico atualizado: `python -m futmesa --pdf <PDF> --saida saida --anos <ano>`
   - PDF avulso: `python -m futmesa --pdf <PDF> --saida saida --ano-unico <ano> --cidade "<cidade>" --uf <UF>`
   - O Python padrão desta máquina não tem as bibliotecas. Use um ambiente virtual com `pip install -r requirements.txt` (precisa também de `pdftotext`, do `poppler-utils`).
3. Rode `python -m pytest -q tests`.
4. Confira a aba/verificação `qualidade`: não pode ganhar `chave_duplicada`, `posicoes_descontinuas` nem `botonista_repetido_no_ano`.
5. Revise o que é novo e mostre ao usuário antes de seguir:
   - nomes que não bateram com botonistas já existentes (candidatos a entrar em `dados/depara_botonistas.csv`);
   - pessoas com o mesmo nome em estados diferentes ou que mudaram de estado (`dados/pessoas_manual.csv`);
   - categoria ou divisão que não existia antes.
   Erro de digitação do PDF vai em `dados/correcoes_texto.csv`, nunca no código.
6. Com o aval do usuário, faça commit e push (o site baixa os Parquet do GitHub na publicação).

## Parte 2 — Site (este repositório)

1. Regere o JSON da página a partir da base local:
   `python _scripts/futmesa_dados.py --origem ../futmesa-brasileirao/saida` (precisa de `polars`).
   Confira na saída que o número de edições subiu em 1.
2. Veja se algo novo exige mudança de código:
   - categoria nova → `CATEGORIA_AGRUPADA` em `_scripts/futmesa_dados.py` e a lista `categorias` em `futmesa/historico-brasileiro/index.qmd` (decisão do usuário: agrupar ou criar filtro);
   - outro ano sem campeonato → `ANOS_SEM_CAMPEONATO` no script.
3. Atualize os textos fixos. Recalcule cada número a partir do JSON, não confie no texto antigo:
   - `futmesa/historico-brasileiro/index.qmd`: `description` (nº de edições e período), parágrafo de abertura ("35 edições"), as listas de anos com classificação incompleta (`edicoes[].parcial`), os botonistas que jogaram duas categorias na mesma edição, o total de linhas sem UF, e a referência ao documento da CBFM (nome e número da edição do PDF). Acrescente `date-modified` com a data de hoje.
   - `futmesa.qmd`: período ("de 1989 a 2025").
   - `CLAUDE.md`: período e contagens do briefing.
   - Thumbnail: edite o texto em `futmesa/historico-brasileiro/_thumbnail.html` e gere o PNG:
     `google-chrome --headless=new --no-sandbox --hide-scrollbars --window-size=1200,675 --screenshot=futmesa/historico-brasileiro/thumbnail.png file://$PWD/futmesa/historico-brasileiro/_thumbnail.html`
4. Renderize tudo com `quarto render` e confira a página servindo a pasta de saída por HTTP
   (`python3 -m http.server` dentro de `docs/`; abrir o HTML direto do disco não carrega os dados):
   - nenhum erro de célula (elementos `.observablehq--error`) em nenhuma das opções do filtro de categoria;
   - o ano novo aparece no eixo dos gráficos como `<ano> - <cidade> (<UF>)`;
   - números de destaque, campeões e títulos por estado incluem a edição nova;
   - temas claro e escuro, e largura de celular.
5. Mostre ao usuário um resumo do que mudou (novos campeões, total de participantes, qualquer número que pareça estranho) e só então publique: `make update MSG="futmesa: Brasileiro de <ano>"`. O push em `main` dispara a publicação.

## Cuidados

- Estatísticas ausentes no PDF ficam vazias; nada é estimado.
- Identifique pessoas sempre por `id_botonista`.
- Textos para o leitor em português; nomes de colunas em português; código e docstrings em inglês.
- Não cite o link direto do PDF da CBFM (ele muda); cite a página de documentos históricos.
