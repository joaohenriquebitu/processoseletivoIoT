# Relatório Técnico - Sistema de Monitoramento de Temperatura com Alarme

## Identificação do Candidato

* **Nome completo:** João Henrique de Brito Leandro Bitu Corrêa

---

##  1. Visão Geral da Solução

O projeto consiste em um sistema inteligente de monitoramento de temperatura projetado para atuar como um alarme configurável. O dispositivo lê continuamente a temperatura ambiente e exibe em tempo real as estatísticas (temperatura atual, máxima, mínima e média da última 1 hora de operação) em um display OLED. 

A interação com o usuário ocorre por meio de dois botões físicos, que permitem o ajuste dinâmico do *threshold* de disparo do alarme. Caso a temperatura lida ultrapasse o limite definido, um sistema de alerta audiovisual (LED e Buzzer) é acionado de forma pulsante para alertar o usuário.

<img width="1136" height="591" alt="Wokwi" src="https://github.com/user-attachments/assets/7db9bcbf-b3b2-4663-ab14-300bad7a3ddd" />

---

## 2. Arquitetura do Sistema Embarcado

A arquitetura lógica foi desenhada com foco em responsividade e eficiência, evitando completamente o uso de delays bloqueantes. O fluxo principal baseia-se em uma máquina de estados contínua orientada a tempo:

* **Loop Principal (Main Loop):** Utiliza a função `time.ticks_diff()` para gerenciar múltiplas tarefas simultâneas sem travar o microcontrolador.
* **Aquisição e Processamento de Dados:** A cada 2 segundos o sistema realiza a leitura da temperatura, atualiza o vetor de histórico e recalcula as métricas estatísticas de máxima, mínima e média.
* **Interface e Entradas:** A leitura dos botões é feita por *polling* no loop principal, mas protegida por uma janela de *debounce* por software de 150ms. O display OLED é atualizado a cada iteração do loop para refletir mudanças imediatas.
* **Assincronismo do Alarme:** O atuador de alarme não depende do loop principal. Quando a condição de alerta é atingida, um Timer de Hardware (`machine.Timer(0)`) é inicializado. Esse timer dispara uma interrupção a cada 250ms que alterna o estado do LED e a frequência do PWM do Buzzer, garantindo um alerta constante sem comprometer a leitura dos sensores e botões.

---

## 3. Componentes Utilizados na Simulação

O hardware virtual foi estruturado no `diagram.json` contendo os seguintes componentes:

* **Placa ESP32 (`board-esp32-devkit-v1`):** Microcontrolador principal responsável pela orquestração de todo o sistema e geração dos sinais de hardware (I2C, PWM, Interrupções).
* **Sensor DHT22 (`wokwi-dht22`):** Conectado ao pino GPIO16 (`RX2`), responsável por captar a temperatura ambiente.
* **Display OLED SSD1306 (`board-ssd1306`):** Conectado via barramento I2C (SCL no GPIO22, SDA no GPIO21). Responsável pela interface visual do usuário.
* **Botões / Pushbuttons (`wokwi-pushbutton`):** 
    * **Botão UP (Verde):** Conectado ao GPIO12. Incrementa a temperatura limite do alarme.
  * **Botão DOWN (Vermelho):** Conectado ao GPIO14. Decrementa a temperatura limite do alarme.
* **LED Vermelho (`wokwi-led`):** Conectado ao GPIO26 em série com um resistor de 330Ω, atua como alerta visual.
* **Buzzer (`wokwi-buzzer`):** Conectado ao GPIO27, utiliza modulação PWM para gerar um alerta sonoro.

---

## 4. Características Técnicas Relevantes

* **Temporização Não-Bloqueante:** O controle de tempo do fluxo principal é realizado de forma concorrente através das funções `time.ticks_ms()` e `time.ticks_diff()`. Essa implementação garante que a verificação dos botões e a atualização do display OLED ocorram continuamente, sem sofrer atrasos pelo intervalo de 2 segundos exigido para a leitura do sensor DHT22.
* **Timer de Hardware para o Alarme:** O controle do alerta audiovisual foi implementado utilizando interrupções de hardware com a classe `machine.Timer(0)`. Quando o alarme é acionado, o timer dispara uma rotina a cada 250ms que alterna o estado do LED e a frequência do PWM, operando de forma paralela ao loop principal.
* **Buffer Circular (Janela Deslizante):** O armazenamento dos dados históricos utiliza uma estrutura de Fila em um array com tamanho fixo. O limite é definido pela constante `MAX_HISTORY = 1800`, o que corresponde exatamente a 1 hora de operação (1 leitura a cada 2 segundos). Dados novos entram via `append()` e os mais antigos saem via `pop(0)`, o que mantém o consumo de memória RAM constante e fornece a base de dados para o cálculo dinâmico da temperatura média, máxima e mínima.

## 5. Funcionamento

A simulação do firmware no ambiente Wokwi apresenta o seguinte comportamento funcional:

* O display OLED inicializa corretamente e exibe a temperatura atual e o threshold, além das métricas agregadas (máxima, mínima e média) formatadas com uma casa decimal.
* O controle de dados em buffer circular evita o acúmulo excessivo de variáveis em memória, atualizando as estatísticas da última hora conforme novas leituras são registradas pelo DHT22.
* A interface física (botões UP e DOWN) permite o incremento e decremento do limite de temperatura (threshold) com resposta visual imediata no display.
* Quando a temperatura ultrapassa o limite estabelecido pelo usuário, a interrupção do timer aciona o alarme: o LED de alerta pisca sequencialmente e o Buzzer alterna sua emissão sonora entre 1000Hz e 1500Hz. O sistema cessa o alarme automaticamente quando a temperatura lida cai para baixo do limite configurado.

