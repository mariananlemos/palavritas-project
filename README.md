# 📝 Case Técnico Palavritas — the news

**feito por Mariana Lemos**  
*Análise de Produto & Growth*

---

## 🎯 Sobre o Projeto

Este repositório reúne a análise de dados e propostas de crescimento do **Palavritas**, o jogo diário de palavras da newsletter **the news**. 

O principal objetivo deste projeto é responder à pergunta:  
> *"O que está determinando se um usuário volta a jogar — e o que podemos fazer para aumentar isso?"*

---

## 💡 O que Descobrimos (Principais Insights)

* **O Hábito com a Newsletter é o Maior Aliado:** Leitores que abrem a newsletter da manhã antes de jogar resolvem as palavras mais rápido, vencem mais (76,9% de vitórias vs. 56,4%) e possuem uma **retenção 23% superior** no longo prazo.
* **A Janela Noturna é o Nosso Maior Churn:** O fluxo de jogadores tem dois picos: de manhã e de noite. No entanto, os jogadores da noite jogam "no escuro" (sem ler a newsletter) e abandonam o jogo com muito mais frequência.
* **O Jogo é Universal:** Fatores como idade, salário, profissão e estado não têm impacto estatístico no retorno do jogador. A retenção depende puramente do hábito construído, não do perfil social.

---

## 🚀 Propostas de Ação (Próximos Testes)

1. **Campanha "Dica Noturna":** Enviar uma notificação curta ou e-mail às 20h30 para os jogadores noturnos com uma pista sobre a palavra do dia, simulando o efeito positivo que a newsletter matinal traz.
2. **Notificação "Streak Guard":** Lembrar automaticamente no final do dia os usuários que jogaram ontem e possuem uma sequência ativa (streak) de que eles estão prestes a perdê-la.
3. **Filtro de Palavras:** Garantir que palavras truncadas ou com erros ortográficos sejam filtradas de antemão, reduzindo frustrações desnecessárias.

---

## 📂 Onde Encontrar Cada Entrega

* **Relatório Completo de Negócios:** [relatorio_analise.md](file:///c:/Users/Usuario/Desktop/repositorios-mariana/thenews-dados/palavritas-project/relatorio_analise.md) — Contém o detalhamento da limpeza dos dados, as análises de correlação e as propostas estruturadas em Hipótese, Ação e Sucesso.
* **Dashboard Interativo:** [public/index.html](file:///c:/Users/Usuario/Desktop/repositorios-mariana/thenews-dados/palavritas-project/public/index.html) — Um painel visual responsivo construído para acompanhar o desempenho diário dos cohorts de jogadores.
* **Código de Limpeza e Processamento:** [clean_and_analyze.py](file:///c:/Users/Usuario/Desktop/repositorios-mariana/thenews-dados/palavritas-project/clean_and_analyze.py) — O script em Python responsável por higienizar a base de dados original e rodar os cálculos estatísticos.

---

## 🛠️ Como Testar e Visualizar

1. **Preparação dos Dados (Python):**
   Instale as bibliotecas necessárias com `pip install pandas numpy scipy openpyxl` e execute:
   ```bash
   python clean_and_analyze.py
   ```
2. **Acessando o Dashboard:**
   Abra a pasta `public` em um servidor web local (por exemplo, executando `python -m http-server 8000` dentro da pasta `public`) e acesse `http://localhost:8000` no seu navegador.
