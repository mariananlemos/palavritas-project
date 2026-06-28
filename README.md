# case técnico — palavritas

Este repositório contém a resolução do case técnico de dados e produto para o Palavritas, o jogo de palavras do *the news*. 

O objetivo do projeto foi analisar a base de dados de uso do jogo, identificar o que realmente influencia a retenção dos usuários no 30º dia (D30).

O dashboard interativo está publicado e pode ser acessado aqui: https://palavritas-project.vercel.app/

## o que foi analisado e descoberto

Ao cruzar os dados de comportamento dos jogadores, identifiquei que o principal fator para a retenção do usuário a longo prazo não tem a ver com dados demográficos (idade, salário, cargo ou se ele pede muito delivery não influenciam no retorno), mas sim com a criação de um hábito integrado à leitura da newsletter:

- **efeito newsletter:** quem lê a newsletter antes de jogar ganha mais rápido, se frustra menos e tem uma taxa de retenção muito maior no D30.
- **usuários noturnos:** identifiquei um volume grande de acessos à noite (entre 22h e 23h), mas esses usuários jogam sem ler a newsletter (0% de abertura prévia) e, por isso, desistem do jogo muito mais rápido. Essa seria a maior oportunidade de melhoria.

Sugestão com um teste A/B: enviar uma notificação via push às 20h30 para os jogadores noturnos com uma pista sobre a palavra do dia, simulando o efeito facilitador da newsletter matinal.

## estrutura do projeto

- [relatorio_analise.md](relatorio_analise.md): relatório completo explicando a limpeza dos dados, os testes estatísticos e o raciocínio das propostas.
- [clean_and_analyze.py](clean_and_analyze.py): processa a planilha original e exporta as métricas simplificadas.
- [public/](public/): arquivos do dashboard (HTML, CSS e JavaScript) carregados no Vercel.

## rodando localmente

1. instale as bibliotecas necessárias: `pip install pandas numpy scipy openpyxl`
2. execute: `python clean_and_analyze.py`
3. abra a pasta `public` usando um servidor local simples (ex: `python -m http-server 8000` dentro da pasta) e acesse `http://localhost:8000`.