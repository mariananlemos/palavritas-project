# Case Técnico — Palavritas (the news)

Este repositório contém a resolução do case técnico de dados e produto para o Palavritas, o jogo de palavras do *the news*. 

O objetivo do projeto foi analisar a base de dados de uso do jogo, identificar o que realmente influencia a retenção dos usuários no 30º dia (D30) e propor melhorias práticas de produto para aumentar o engajamento geral.

O dashboard interativo está publicado e pode ser acessado aqui: https://palavritas-project.vercel.app/

## O que foi analisado e descoberto

Ao cruzar os dados de comportamento dos jogadores, identificamos que o principal fator para a retenção do usuário a longo prazo não tem a ver com dados demográficos (idade, salário, cargo ou se ele pede muito delivery não influenciam no retorno), mas sim com a criação de um hábito integrado à leitura da newsletter:

- **Efeito Newsletter:** Quem lê a newsletter antes de jogar ganha mais rápido, frustra-se menos e tem uma taxa de retenção muito maior no D30.
- **Usuários Noturnos (Churn):** Identificamos um volume expressivo de acessos à noite (entre 22h e 23h), mas esses usuários jogam sem ler a newsletter (0% de abertura prévia) e, por isso, desistem do jogo muito mais rápido. Essa é a nossa maior oportunidade de melhoria.

## Propostas de Próximos Passos (Testes A/B)

Com base nas descobertas, propomos testar três ações na próxima semana:
1. **Dica Noturna:** Enviar uma notificação curta por e-mail ou push às 20h30 para os jogadores noturnos com uma pista sobre a palavra do dia, simulando o efeito facilitador da newsletter matinal.
2. **Streak Guard:** Notificar perto do final do dia os usuários com sequências de dias ativas (streaks) que ainda não jogaram hoje, ativando o gatilho de aversão à perda.
3. **Qualidade do Banco de Palavras:** Filtrar palavras quebradas ou com erros no banco para evitar quebras de expectativa na experiência do jogo.

## Estrutura do projeto

- [relatorio_analise.md](relatorio_analise.md): Relatório executivo completo explicando a limpeza dos dados, os testes estatísticos e o raciocínio das propostas.
- [clean_and_analyze.py](clean_and_analyze.py): Script em Python que processa a planilha original e exporta as métricas simplificadas.
- [public/](public/): Arquivos do dashboard web (HTML, CSS e JavaScript) carregados no Vercel.

## Como rodar localmente

Se quiser rodar o processamento dos dados ou abrir o painel localmente:
1. Instale as bibliotecas necessárias: `pip install pandas numpy scipy openpyxl`
2. Execute o script de dados: `python clean_and_analyze.py`
3. Abra a pasta `public` usando um servidor local simples (ex: `python -m http-server 8000` dentro da pasta) e acesse `http://localhost:8000`.

Feito por Mariana Lemos.
