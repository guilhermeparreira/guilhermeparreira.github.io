# Seção Futmesa — briefing para o site (Quarto, GitHub Pages)

Colar este arquivo na raiz do repositório do site (ou o conteúdo no `CLAUDE.md` de lá).

## Objetivo

Nova seção **Futmesa** no site (não é um post do blog), sobre o histórico do Campeonato Brasileiro
Individual de Futebol de Mesa (12 Toques), 1989–2025. Público: os próprios botonistas.

1. **Landing page da análise histórica**: como o esporte se comportou ao longo dos anos
   (participantes por ano, categoria e estado; campeões; divisões; clubes).
2. **Página do botonista**: a pessoa escolhe o nome e vê toda a trajetória (ano, categoria,
   divisão, posição, estatísticas). Uma página única com filtro (Observable JS) e o id na URL
   (`?botonista=robertinho-pr`) para compartilhar, em vez de ~1.700 páginas.
3. **Aviso de inconsistência**: link para um formulário em cada página, para não poluir os comentários.
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

## Automação desejada

No workflow de publicação, antes do `quarto render`, baixar os três Parquet do `futmesa-brasileirao`.
