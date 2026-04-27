import machine
import dht
import ssd1306
import time

# Configurações iniciais
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=800000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Inicializa o sensor DHT22
sensor = dht.DHT22(machine.Pin(16))

# Configurações dos botões, LED e buzzer
btn_up = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
btn_down = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# Configurações do alarme
led = machine.Pin(26, machine.Pin.OUT)
buzzer = machine.PWM(machine.Pin(27), duty=0)
alarm_timer = machine.Timer(0)
is_alarming = False

printed = False

threshold = 30.0
history = []

MAX_HISTORY = 1800

last_read_time = 0
last_btn_time = 0

# Logica para alternar o estado do alarme
def toggle_alarm(t):
    if led.value():
        led.value(0)
        buzzer.freq(1000)
    else:
        led.value(1)
        buzzer.freq(1500)

# Função para iniciar o alarme, que liga o buzzer e inicia o timer para alternar o LED
def start_alarm():
    global is_alarming
    if not is_alarming:
        is_alarming = True
        buzzer.duty(512)
        alarm_timer.init(
            period=250, mode=machine.Timer.PERIODIC, callback=toggle_alarm)

# Função para parar o alarme, que desliga o buzzer e o LED, e para o timer
def stop_alarm():
    global is_alarming
    if is_alarming:
        is_alarming = False
        alarm_timer.deinit()
        led.value(0)
        buzzer.duty(0)

# Loop principal
while True:
    current_time = time.ticks_ms()

    # Verifica se os botões foram pressionados para ajustar o threshold da temperatura
    if time.ticks_diff(current_time, last_btn_time) > 150:
        if btn_up.value() == 0:
            threshold += 0.5
            last_btn_time = current_time
        elif btn_down.value() == 0:
            threshold -= 0.5
            last_btn_time = current_time
    # Lê a temperatura do sensor a cada 2 segundos e atualiza o histórico
    if time.ticks_diff(current_time, last_read_time) >= 2000:
        try:
            sensor.measure()
            temp = sensor.temperature()

            history.append(temp)
            if len(history) > MAX_HISTORY:
                history.pop(0)

            t_max = max(history)
            t_min = min(history)
            t_avg = sum(history) / len(history)

            # Verifica se a temperatura atual excede o threshold para ativar ou desativar o alarme
            if temp > threshold:
                start_alarm()
            else:
                stop_alarm()

        except OSError:
            oled.fill(0)
            oled.text("Erro no Sensor!", 0, 0)
            oled.show()

        last_read_time = current_time

    oled.fill(0)
    oled.text(f"Temp: {temp:.1f} C", 0, 0)
    oled.text(f"Max : {t_max:.1f} C", 0, 12)
    oled.text(f"Min : {t_min:.1f} C", 0, 24)
    oled.text(f"Med : {t_avg:.1f} C", 0, 36)
    oled.text(f"Alarme > {threshold:.1f} C", 0, 52)
    oled.show()


    # Print de teste para o github actions, significa que conseguiu rodar o loop com sucesso
    if not printed:
      print("Teste")
      printed = True
