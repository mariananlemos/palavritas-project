# o que determina a retenção no Palavritas?

para responder à pergunta central: *"o que está determinando se um usuário volta a jogar — e o que podemos fazer para aumentar isso?"*, realizei uma limpeza do dataset e apliquei testes estatísticos de significância (qui-quadrado e teste T de student) para separar ruídos de padrões reais de comportamento.

### diagnóstico:
1. **o hábito matinal integrado é o maior driver:** o fator número 1 associado à retenção de longo prazo (D30) é **abrir a newsletter antes de jogar**. leitores com esse comportamento têm uma taxa de vitória **20.5% maior** (76.9% vs. 56.4%) e resolvem os desafios em **menos tentativas** (2.92 vs. 3.74). esse sentimento de autoeficácia leva o usuário no jogo, aumentando a retenção D30 em **23.6% relativos** (p-value = 5.1e-35, extremamente significativo).
2. **os horários revelam dois públicos:** o tráfego do jogo é dividido em dois picos idênticos em volume (~4.300 sessões): das 06h às 08h e das 22h às 23h. no entanto, o grupo da manhã tem **61% de taxa de abertura da newsletter antes de jogar** e **38.5% de retenção D30**. o grupo da noite tem **0% de abertura de newsletter** e apenas **29% de retenção D30**. a noite é a maior janela de churn.
3. **a força do hábito:** manter uma sequência de dias jogando (`streak_day`) é o principal gatilho de retorno imediato no dia seguinte (D1). quanto maior a sequência atual, maior a chance de voltar no dia seguinte (p-value = 0.000004).
4. **demografia e Delivery não importam:** idade, cargo, faixa salarial, setor da empresa, estado e hábitos de pedir delivery de comida **não possuem qualquer relevância estatística** sobre se o usuário continuará ativo no D30 (p-values > 0.10). a retenção é ditada pelo hábito de uso, não pelo perfil demográfico.
5. **dificuldade:** palavras com bugs ortográficos (como `ORAÇÃ` devido ao limite de 5 letras, e `PAZÃO`) derrubam a taxa de vitória para 44%, mas não correlacionam de forma significativa com o churn do usuário (r = -0.23, p-value = 0.20). o leitor tolera a frustração de perder palavras difíceis, contanto que mantenha o hábito de jogo.

---

## entrega 1 — limpeza e diagnóstico

antes de prosseguir com as modelagens, higienizei o dataset para remover ruídos e falhas de rastreamento.

### resumo da limpeza:
| Tabela | Registros Originais | Registros Finais | Ação de Higienização |
| --- | --- | --- | --- |
| `palavritas_sessions` | 41.157 | 41.044 | Remoção de 93 sessões com tentativas inválidas (0, 7 e 8) e 63 sessões sem resultado registrado. |
| `palavritas_attempts` | 147.270 | 146.993 | Remoção de 41 tentativas de número > 6 (7, 8, 9, 10) e 236 tentativas órfãs associadas a sessões inválidas. |
| `user_profile` | 800 | 800 | Nenhuma remoção. Padronização de strings inconsistentes na coluna `orders_food_delivery`. |

### detalhamento:

1. **tentativas fora do limite (0, 7, 8 e 10):**
   * o jogo é baseado na mecânica de wordle (limite rígido de 6 tentativas). encontrei 59 sessões na tabela principal marcadas com `attempts = 0` e 34 sessões marcadas com `attempts = 7` ou `8`. na tabela de tentativas, encontrei registros mapeados como tentativa número 7, 8, 9 e 10.
   * excluí as sessões que registraram tentativas fora do intervalo [1-6]. 
   * esses casos representam menos de 0.2% da base e vem de falhas de rastreamento no client-side (ex: cliques repetidos no botão de enviar que registraram múltiplos eventos no banco de dados). acreditei que manter esses dados enviesaria as médias de tentativas e taxas de vitória.
2. **inconsistências em dispositivos (`device`):**
   * a coluna registrava strings idênticas com caixas diferentes (ex: `iOS`, `ios`, `IOS`, `Android`, `android`, `ANDROID`).
   * normalizei todos os registros na tabela `sessions` usando um mapeamento de padrões em python, agrupando tudo em apenas dois valores: `iOS` e `Android`.
3. **dados faltantes em resultados (`result`):**
   * encontrei 63 sessões onde a coluna `result` estava vazia (`NaN`). dessas, 43 também continham `attempts = 0`.
   * essas sessões foram descartadas.
   * partidas sem resultado indicam que o usuário fechou o navegador antes de terminar a primeira palavra ou bugs no envio do evento de encerramento do jogo. como o percentual é irrelevante (<0.15%), a exclusão protegeria a acurácia da taxa de vitória.
4. **padronização de respostas de delivery (`orders_food_delivery`):**
   * na tabela de perfil, o comportamento de pedir delivery estava registrado como uma mistura de tipos lógicos em inglês e strings em português (`True`, `False`, `sim`, `não`).
   * normalizei para booleanos nativos (`True` / `False`), onde `True` representa quem pede comida por app e `False` quem não pede.

---

## entrega 2 — análise

cruzei os dados limpos das sessões com os perfis de usuários. para determinar se uma variável realmente influencia a retenção, rodei testes de significância e calculei os coeficientes de correlação.

### 1. impacto da newsletter
o fator mais dominante na atividade do usuário é a abertura da newsletter antes de iniciar o jogo.
* **taxa de vitória:** usuários que abrem a newsletter antes de jogar vencem **76.9%** das partidas, enquanto os que não abrem vencem apenas **56.4%**.
* **tentativas médias:** a média de tentativas cai de **3.74** (quem não abriu) para **2.92** (quem abriu), uma eficiência de quase 1 tentativa a menos para resolver o desafio.
* **retenção D30:** o grupo que joga integrado à newsletter tem uma retenção D30 de **37.76%**, contra **30.54%** do grupo que não abre.
* **validação estatística:** o teste qui-quadrado de independência para a retenção D30 retornou um p-value de **5.12e-35**. isso prova matematicamente que a abertura da newsletter e a retenção D30 estão fortemente associadas.
* o *the news* envia a newsletter às 06h06. quem lê antes de jogar chega com mais contexto, erra menos e acaba criando um hábito duplo: ler e jogar fazem parte da mesma rotina matinal.

### 2. diferença de horário e período de jogo
* **pico matinal (06h - 08h):** ~12.900 partidas totais. média de abertura da newsletter antes do jogo: **61%**. retenção D30 média: **37.5%**.
* **pico noturno (22h - 23h):** ~8.500 partidas totais. média de abertura da newsletter antes do jogo: **0%**. retenção D30 média: **29.7%**.
* o jogador noturno joga o Palavritas como um passatempo de fim de dia. sem a dica da newsletter matinal, sua taxa de vitória é menor e ele joga solto na rotina, o que gera um churn muito mais rápido. o jogador matinal joga como extensão de um hábito já consolidado -> ler a newsletter.

### 3. a sequência de jogo como driver
* **D1 por sequência de jogo:** usuários no dia 1 de streak têm **21.7%** de taxa de retorno no dia seguinte. usuários com 4 dias de streak têm **28.3%**, e com 7 dias de streak chegam a **33.3%**.
* **validação estatística:** o teste T comparando o streak médio de quem retornou no dia seguinte contra quem não retornou deu um p-value de **0.000004** (Altamente significativo).
* a gamificação do streak funcionou. o medo de perder a sequência acumulada atua como um gatilho de aversão à derrota, motivando o retorno diário.

### 4. perfil socioeconômico e hábitos de delivery
* **idade (p-value = 0.98):** jovens de 18-24 anos têm 32.1% de retenção D30, idêntico aos usuários de 45+ anos (32.3%).
* **dalário (p-value = 0.26):** usuários que ganham acima de R$10k retêm 32.7%, enquanto quem ganha até R$2k retém 31.9% (diferença sem relevância estatística).
* **delivery de comida (p-value = 0.18):** usuários que pedem delivery retêm a taxas muito próximas dos que não pedem (32.2% vs. 31.5%).
* reter no Palavritas depende exclusivamente da formação de um hábito diário com o produto e não do perfil demográfico do leitor.

### 5. dificuldade da palavra
* palavras com caracteres especiais ou faltantes (como `DANÇA` e `ORAÇÃ`) tiveram menos de **45% de taxa de vitória** e exigiram mais de **4.2 tentativas**.
* palavras fáceis (como `GENRO` e `PRETO`) tiveram mais de **66% de taxa de vitória** e média de **3.3 tentativas**.
* a correlação linear entre a facilidade de uma palavra e a retenção do usuário não é estatisticamente significativa.
* o usuário não desiste do jogo no longo prazo por enfrentar uma palavra difícil. ele aceita o desafio como parte da dinâmica.

---

## entrega 3 — proposta

### proposta: campanha "dica noturna" via push
* acredito que ao fornecer um benefício equivalente à dica da newsletter matinal para os jogadores noturnos, seria possivel aumentar a taxa de vitória de 56% para >65%, reduzindo a frustração e elevando a retenção D30 deste grupo.
* como? implementando um envio de notificação push curto às 20h30 para usuários que costumam jogar à noite, oferecendo uma dica lúdica sobre a palavra do dia ("Precisa de uma mãozinha para a palavra de hoje? Abra para ver a dica").
* a resposta de que funcionou seria analisar quando a retenção D30 do grupo de jogadores noturnos subir dos atuais **29% para pelo menos 33%** nos próximos 30 dias atraves de um teste a/b.