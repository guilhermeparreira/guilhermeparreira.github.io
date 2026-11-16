# Seção Futmesa — briefing para o site (Quarto, GitHub Pages)

Para incluir uma nova edição do campeonato, use a skill `atualizar-futmesa` (`.claude/skills/`).

## Regras de trabalho neste repositório

- **Publicação**: o site é renderizado e publicado pelo GitHub Actions a cada push em `main`
  (`.github/workflows/publish-quarto.yml`, branch `gh-pages`). `make update MSG="..."` faz add, commit e push
  de tudo: só rode quando eu pedir para publicar.
- **`docs/`** é a saída do `quarto render` local e está versionada, mas não é o que vai ao ar. Não edite à mão.
  Para testar sem sujar `docs/`, renderize em outra pasta: `quarto render --output-dir <pasta temporária>`.
- **Só `.qmd` vira página** (`render` no `_quarto.yml`). Arquivos e pastas que começam com `_` são ignorados pelo Quarto.
- **Idioma**: blog (`posts/`) em inglês; seção Futmesa (`futmesa/`) em português. Em código: nomes de colunas e
  textos para o leitor em português; código e docstrings em inglês.
- **Datas no YAML dos posts**: `MM-DD-YYYY` ou `YYYY-MM-DD`. `DD-MM-YYYY` é lido errado pelo Quarto.
- **Python**: o Python padrão da máquina não tem `polars`/`pandas`; os posts antigos dependem do `_freeze/`.
  Para rodar `_scripts/futmesa_dados.py` use um ambiente com `polars` (no Actions ele vem do `requirements.txt`).
- **Tema**: o site abre no tema do sistema do visitante. Qualquer coisa visual precisa funcionar no claro (yeti)
  e no escuro (slate), e em largura de celular.
- **Verificação**: depois de mexer em página com OJS, renderize e abra no navegador servindo por HTTP
  (abrir o HTML do disco não carrega os dados). Não diga que funciona sem ter visto.
- **Serviços externos** (comentários, formulários, etc.): confirme que o serviço está no ar antes de recomendar.
- **RSS**: removido do site de propósito. Não recriar feeds.

## Como a seção Futmesa funciona

- `futmesa.qmd` é a listagem da seção; toda página dentro de `futmesa/` aparece nela, e não no blog.
- `_scripts/futmesa_dados.py` lê os Parquet (do GitHub, ou de `--origem`) e grava `futmesa/dados/brasileiro.json`.
  O JSON fica versionado para o preview local funcionar; o Actions regera antes do render.
- As páginas usam Observable JS (blocos `{ojs}`) e Observable Plot: os dados são carregados e agregados no
  navegador. O filtro de categoria no topo vale para a página inteira.
- `futmesa/futmesa.css` guarda as cores dos gráficos (variáveis `--fm-*`, com versão clara e escura).
- Comentários da seção: Disqus (`futmesa/_disqus.html`). O blog usa giscus.
- Aviso de inconsistência: issue no `futmesa-brasileirao` (template `inconsistencia.yml`).

## Decisões já tomadas no relatório

- Sub-20 (2008) conta como Sub-18 e Infantil (1994) como Sub-15; há o filtro "Sub-15 + Sub-18".
- "Estado de origem" = UF da primeira participação (a base não tem estado de nascimento).
- Anos com classificação incompleta: menos de 90% dos participantes informados ou menos de 60 linhas.
  Não quebram sequências de participação, mas só contam para quem aparece.
- 2020 e 2021 aparecem no eixo dos gráficos como "Pandemia", sem dados.
- Títulos de todas as categorias do filtro têm o mesmo peso.
- Referência ao PDF: citar a página de documentos históricos da CBFM, nunca o link direto do arquivo.

## Objetivo

Nova seção **Futmesa** no site (não é um post do blog), sobre o histórico do Campeonato Brasileiro
Individual de Futebol de Mesa (12 Toques), 1989–2025. Público: os próprios botonistas.

1. **Landing page da análise histórica**: como o esporte se comportou ao longo dos anos
   (participantes por ano, categoria e estado; campeões; divisões; clubes).
2. **Página do botonista**: a pessoa escolhe o nome e vê toda a trajetória (ano, categoria,
   divisão, posição, estatísticas). Uma página única com filtro (Observable JS) e o id na URL
   (`?botonista=robertinho-pr`) para compartilhar, em vez de ~1.700 páginas.
3. **Aviso de inconsistência**: link em cada página para abrir uma issue no `futmesa-brasileirao`, para não poluir os comentários.
4. **Transparência**: página mostrando o de-para de nomes usado.
5. Futuro: storytelling sobre os campeonatos.

## Dados

Vêm do repositório `futmesa-brasileirao` (pasta `saida/`); o site só consome, nunca corrige dados.

- `classificacao.parquet`: 1 linha por botonista × ano × categoria × divisão (5.102 linhas).
  Colunas principais: `ano`, `edicao`, `cidade_campeonato`, `uf_campeonato`, `categoria`, `divisao`,
  `divisao_nivel` (1 = principal), `posicao`, `id_botonista`, `botonista_padronizado`, `botonista`
  (como impresso), `clube_padronizado`, `uf_botonista`, `wo`, `jogos`, `vitorias`, `empates`,
  `derrotas`, `gols_pro`, `gols_contra`, `saldo_gols`, `pontos`, `observacao`.
- `botonistas.parquet`: 1 linha por pessoa (`id_botonista`, nome, UFs, período, nº de campeonatos).
- `campeonatos.parquet`: 1 linha por edição (sede, local, datas, participantes informados).
- De-para: `dados/depara_botonistas.csv` e `dados/depara_clubes.csv` do mesmo repositório.

## Cuidados com os dados

- Não houve campeonato em 2020 e 2021.
- Estatísticas (J, V, E, D, gols, pontos) só existem a partir de 2002, e E/D só a partir de 2006;
  antes disso ficam vazias.
- Vários anos antigos publicam só os primeiros colocados: número de linhas não é número de participantes
  (use `participantes_informados` quando existir).
- `posicao` vazia = participante citado sem colocação (Master 1996).
- Categorias: Adulto, Master, Sub-18, Sub-15, Sub-20 (2008), Infantil (1994). Divisões mudam de nome
  ao longo do tempo (Ouro/Prata/Bronze/Extra/Copa → 1ª a 5ª Divisão); comparar por `divisao_nivel`.
- Use sempre `id_botonista` para identificar a pessoa (nomes se repetem; pessoas mudam de estado).
  O ID é heurístico e pode ter erros.

## Automação

No workflow de publicação, antes do `quarto render`, `_scripts/futmesa_dados.py` baixa os Parquet do
`futmesa-brasileirao` e regera o JSON. Ainda falta: disparar a publicação do site quando `saida/` mudar lá.
