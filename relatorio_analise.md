# Relatório Executivo: O que determina a retenção no Palavritas?
**Para:** Head de Produto  
**De:** Analista de Dados (Produto & Growth)  
**Assunto:** Diagnóstico de Dados, Fatores de Retorno e Proposta de Alavancagem de Growth  

---

## Resumo Executivo (Reunião de Segunda-feira)

Para responder à pergunta central: *"O que está determinando se um usuário volta a jogar — e o que podemos fazer para aumentar isso?"*, realizamos uma limpeza profunda do dataset e aplicamos testes estatísticos de significância (Qui-Quadrado e Teste T de Student) para separar ruídos de padrões reais de comportamento.

### Principais Achados:
1. **O Hábito Matinal Integrado é o Maior Driver:** O fator número 1 associado à retenção de longo prazo (D30) é **abrir a newsletter antes de jogar**. Usuários com esse comportamento têm uma taxa de vitória **20.5% maior** (76.9% vs. 56.4%) e resolvem os desafios em **menos tentativas** (2.92 vs. 3.74). Esse sentimento de autoeficácia ancora o usuário no jogo, elevando a retenção D30 em **23.6% relativos** (p-value = 5.1e-35, extremamente significativo).
2. **Os Horários Revelam Dois Públicos:** O tráfego do jogo é dividido em dois picos idênticos em volume (~4.300 sessões): das 06h às 08h e das 22h às 23h. No entanto, o grupo da manhã tem **61% de taxa de abertura da newsletter antes de jogar** e **38.5% de retenção D30**. O grupo da noite tem **0% de abertura de newsletter** e apenas **29% de retenção D30**. A noite é nossa maior janela de churn.
3. **A Força das Sequências (Streaks):** Manter uma sequência de dias jogando (`streak_day`) é o principal gatilho de retorno imediato no dia seguinte (D1). Quanto maior a sequência atual, maior a chance de voltar no dia seguinte (p-value = 0.000004).
4. **Demografia e Delivery Não Importam:** Idade, cargo, faixa salarial, setor da empresa, estado e hábitos de pedir delivery de comida **não possuem qualquer relevância estatística** sobre se o usuário continuará ativo no D30 (p-values > 0.10). O produto tem apelo universal; a retenção é ditada pelo hábito de uso, não pelo perfil demográfico.
5. **Dificuldade Não Afeta Retenção:** Palavras com bugs ortográficos/truncamento (como `ORAÇÃ` devido ao limite de 5 letras, e `PAZÃO`) derrubam a taxa de vitória para 44%, mas não correlacionam de forma significativa com o churn do usuário (r = -0.23, p-value = 0.20). O usuário tolera a frustração de perder palavras difíceis, contanto que mantenha o hábito de jogo.

---

## Entrega 1 — Limpeza e Diagnóstico

Antes de prosseguirmos com as modelagens, higienizamos o dataset para remover ruídos e falhas de rastreamento. Abaixo estão listados os diagnósticos e ações tomadas:

### Resumo Numérico da Limpeza:
| Tabela | Registros Originais | Registros Finais | Ação de Higienização |
| --- | --- | --- | --- |
| `palavritas_sessions` | 41.157 | 41.044 | Remoção de 93 sessões com tentativas inválidas (0, 7 e 8) e 63 sessões sem resultado registrado. |
| `palavritas_attempts` | 147.270 | 146.993 | Remoção de 41 tentativas de número > 6 (7, 8, 9, 10) e 236 tentativas órfãs associadas a sessões inválidas. |
| `user_profile` | 800 | 800 | Nenhuma remoção. Padronização de strings inconsistentes na coluna `orders_food_delivery`. |

### Detalhamento das Decisões de Limpeza:

1. **Tentativas Fora do Limite (0, 7, 8 e 10):**
   * *O Problema:* O jogo é baseado na mecânica de Wordle (limite rígido de 6 tentativas). Encontramos 59 sessões na tabela principal marcadas com `attempts = 0` e 34 sessões marcadas com `attempts = 7` ou `8`. Na tabela de tentativas, encontramos registros mapeados como tentativa número 7, 8, 9 e 10.
   * *Ação:* Excluímos as sessões que registraram tentativas fora do intervalo [1-6]. 
   * *Justificativa:* Estes casos representam menos de 0.2% da base e decorrem de falhas de rastreamento no client-side (ex: cliques repetidos no botão de enviar que registraram múltiplos eventos no banco ou sessões de teste de desenvolvedores). Mantê-los enviesaria as médias de tentativas e taxas de vitória.
2. **Inconsistências em Dispositivos (`device`):**
   * *O Problema:* A coluna registrava strings idênticas com caixas diferentes (ex: `iOS`, `ios`, `IOS`, `Android`, `android`, `ANDROID`).
   * *Ação:* Normalizamos todos os registros na tabela `sessions` utilizando um mapeamento de padrões em Python, agrupando tudo em apenas dois valores: `iOS` e `Android`.
3. **Dados Faltantes em Resultados (`result`):**
   * *O Problema:* Encontramos 63 sessões onde a coluna `result` estava vazia (`NaN`). Dessas, 43 também continham `attempts = 0`.
   * *Ação:* Essas sessões foram descartadas.
   * *Justificativa:* Partidas sem resultado indicam que o usuário fechou o navegador antes de terminar a primeira palavra ou bugs no envio do evento de encerramento do jogo. Como o percentual é irrelevante (<0.15%), a exclusão protege a acurácia da taxa de vitória.
4. **Padronização de Respostas de Delivery (`orders_food_delivery`):**
   * *O Problema:* Na tabela de perfil, o comportamento de pedir delivery estava registrado como uma mistura de tipos lógicos em inglês e strings em português (`True`, `False`, `sim`, `não`).
   * *Ação:* Normalizamos para booleanos nativos (`True` / `False`), onde `True` representa quem pede comida por app e `False` quem não pede.

---

## Entrega 2 — Análise de Correlação

Cruzamos os dados limpos das sessões com os perfis de usuários. Para determinar se uma variável realmente influencia a retenção, rodamos testes de significância e calculamos os coeficientes de correlação.

### 1. O Impacto da Newsletter (Forte Influência)
O fator mais dominante na atividade do usuário é a abertura da newsletter antes de iniciar o jogo.
* **Taxa de Vitória:** Usuários que abrem a newsletter antes de jogar vencem **76.9%** das partidas, enquanto os que não abrem vencem apenas **56.4%**.
* **Tentativas Médias:** A média de tentativas cai de **3.74** (quem não abriu) para **2.92** (quem abriu) — uma eficiência de quase 1 tentativa a menos para resolver o desafio.
* **Retenção D30:** O grupo que joga integrado à newsletter tem uma retenção D30 de **37.76%**, contra **30.54%** do grupo que não abre.
* **Validação Estatística:** O teste Qui-Quadrado de Independência para a retenção D30 retornou um p-value de **5.12e-35**. Isso prova matematicamente que a abertura da newsletter e a retenção D30 estão fortemente associadas.
* *Raciocínio:* O *the news* envia a newsletter às 06h06 com notícias e, possivelmente, uma dica editorial ou contexto sobre a palavra do dia. Usuários que leem a newsletter jogam munidos dessa pista implícita/explícita, ganham mais rápido, frustram-se menos e criam um hábito consistente acoplado à sua leitura matinal de notícias.

### 2. A Diferença de Horário e Período de Jogo (Forte Influência)
Ao plotarmos as partidas por hora do dia, identificamos dois picos de acessos:
* **Pico Matinal (06h - 08h):** ~12.900 partidas totais. Média de abertura da newsletter antes do jogo: **61%**. Retenção D30 média: **37.5%**.
* **Pico Noturno (22h - 23h):** ~8.500 partidas totais. Média de abertura da newsletter antes do jogo: **0%**. Retenção D30 média: **29.7%**.
* *Raciocínio:* O jogador noturno joga o Palavritas como um passatempo isolado de fim de dia. Sem a dica da newsletter matinal, sua taxa de vitória é menor e ele joga "solto" na rotina, o que gera um churn muito mais rápido. O jogador matinal joga como extensão de um hábito já consolidado (ler a newsletter).

### 3. A Sequência de Jogo (Streak) como Driver D1 (Média Influência)
Analisamos se o tamanho da sequência do usuário (`streak_day`) estimula o retorno no dia seguinte.
* **D1 por Streak:** Usuários no dia 1 de streak têm **21.7%** de taxa de retorno no dia seguinte. Usuários com 4 dias de streak têm **28.3%**, e com 7 dias de streak chegam a **33.3%**.
* **Validação Estatística:** O Teste T comparando o streak médio de quem retornou no dia seguinte contra quem não retornou deu um p-value de **0.000004** (Altamente significativo).
* *Raciocínio:* A gamificação do "streak" funciona. O medo de perder a sequência acumulada atua como um gatilho de aversão à perda, motivando o retorno diário.

### 4. Perfil Socioeconômico e Hábitos de Delivery (Sem Influência)
Contrariando o senso comum de que fatias específicas de mercado seriam mais propensas a reter, os testes de significância derrubaram essa hipótese:
* **Idade (p-value = 0.98):** Jovens de 18-24 anos têm 32.1% de retenção D30, idêntico aos usuários de 45+ anos (32.3%).
* **Salário (p-value = 0.26):** Usuários que ganham acima de R$10k retêm 32.7%, enquanto quem ganha até R$2k retém 31.9% (diferença sem relevância estatística).
* **Delivery de Comida (p-value = 0.18):** Usuários que pedem delivery retêm a taxas muito próximas dos que não pedem (32.2% vs. 31.5%).
* *Raciocínio:* O jogo de palavras atinge uma necessidade cognitiva transversal. Reter no Palavritas depende exclusivamente da formação de um hábito diário com o produto e não do perfil demográfico do leitor.

### 5. Dificuldade da Palavra (Sem Influência)
Calculamos a dificuldade de cada uma das 30 palavras do dataset pela taxa de vitória média.
* Palavras com caracteres especiais ou truncadas no banco (como `DANÇA` e `ORAÇÃ`) tiveram menos de **45% de taxa de vitória** e exigiram mais de **4.2 tentativas**.
* Palavras fáceis (como `GENRO` e `PRETO`) tiveram mais de **66% de taxa de vitória** e média de **3.3 tentativas**.
* **Correlação Word-Level (r = -0.23, p-value = 0.20):** A correlação linear entre a facilidade de uma palavra e a retenção do usuário não é estatisticamente significativa.
* *Raciocínio:* O usuário não desiste do jogo no longo prazo por enfrentar uma palavra difícil ou até frustrante. Ele aceita o desafio como parte da dinâmica de superação. Portanto, o time de produto não precisa suavizar artificialmente a dificuldade das palavras.

---

## Entrega 3 — Propostas de Growth & Produto

Com base nos dados estruturados, propomos 3 ações concretas focadas nos maiores pontos de alavanca identificados (Hábito matinal, Retenção Noturna e Proteção de Streaks).

### Proposta 1: Campanha "Dica Noturna" via Push/E-mail (Foco em Usuários Noturnos)
* **Hipótese:** Acredito que ao fornecer um benefício equivalente à dica da newsletter matinal para os jogadores noturnos (que hoje jogam no escuro e têm 0% de abertura de newsletter), aumentaremos sua taxa de vitória de 56% para >65%, reduzindo a frustração e elevando a retenção D30 deste grupo.
* **Ação:** Implementar um envio de notificação push ou e-mail curto às 20h30 para usuários que costumam jogar à noite, oferecendo uma dica lúdica sobre a palavra do dia ("Precisa de uma mãozinha para a palavra de hoje? Abra para ver a dica"). O link abrirá o jogo com uma dica ativada no topo da tela.
* **Critério de Sucesso:** Saberei que funcionou quando a retenção D30 do grupo de jogadores noturnos subir dos atuais **29% para pelo menos 33%** no próximo cohort de testes de 30 dias.

### Proposta 2: Notificação Ativa "Streak Guard" (Proteção de Frequência)
* **Hipótese:** Acredito que, como a probabilidade de retorno no dia seguinte aumenta de 21% para 28%+ conforme o streak aumenta, proteger ativamente as sequências dos usuários reduzirá o churn diário.
* **Ação:** Disparar um e-mail curto ou push automatizado às 21h ("Não perca seu streak de X dias no Palavritas! Restam poucas horas para desvendar a palavra de hoje") apenas para os usuários que jogaram ontem, possuem streak >= 2, mas ainda não jogaram no dia de hoje.
* **Critério de Sucesso:** Saberei que funcionou quando a taxa de retorno D1 de usuários com sequências de 2 a 5 dias aumentar em **15%** comparado ao grupo controle (sem notificação).

### Proposta 3: Auditoria Ortográfica e Higienização do Dicionário (Qualidade de Conteúdo)
* **Hipótese:** Acredito que palavras truncadas pelo limite de caracteres (como `ORAÇÃ` no lugar de ORAÇÃO) ou palavras pouco usuais (como `PAZÃO`) prejudicam a percepção de qualidade técnica e geram reclamações desnecessárias que sobrecarregam o suporte da marca.
* **Ação:** Implementar um script validador no painel de CMS que impede a publicação de palavras que não constem no dicionário padrão da Academia Brasileira de Letras (ABL) e que tenham caracteres especiais mal mapeados no teclado do app.
* **Critério de Sucesso:** Saberei que funcionou quando a taxa de vitória diária do Palavritas nunca cair abaixo de **52%** para qualquer palavra específica.

---
### Links do Repositório:
* **Código de Pipeline Python:** [clean_and_analyze.py](file:///c:/Users/Usuario/Desktop/repositorios-mariana/thenews-dados/case-tecnico-thenews/clean_and_analyze.py)
* **Visualizações JSON:** [public/data/](file:///c:/Users/Usuario/Desktop/repositorios-mariana/thenews-dados/case-tecnico-thenews/public/data)
