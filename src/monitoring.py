import psutil
import time
import json
import socket
from ping3 import ping
import GPUtil
import platform
import base64
import paho.mqtt.client as mqtt
from datetime import datetime, timezone
from pynput import keyboard, mouse

# Configurações
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "pc/monitoring"
SEND_INTERVAL = 5  # segundos
PING_HOST = "8.8.8.8"

# Inicializa cliente MQTT com protocolo especificado
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Contadores de teclado e mouse
key_counter = {}
key_count = 0
mouse_clicks = 0
last_input_time = time.time()

# Função para capturar teclas
def on_press(key):
    global key_count, last_input_time
    key_str = str(key)
    key_counter[key_str] = key_counter.get(key_str, 0) + 1
    key_count += 1
    last_input_time = time.time()

# Função para capturar cliques do mouse
def on_click(x, y, button, pressed):
    global mouse_clicks, last_input_time
    if pressed:
        mouse_clicks += 1
        last_input_time = time.time()

# Inicia listeners
keyboard_listener = keyboard.Listener(on_press=on_press)
mouse_listener = mouse.Listener(on_click=on_click)
keyboard_listener.start()
mouse_listener.start()

def get_latency(host):
    try:
        latency = ping(host, timeout=1)
        if latency is not None:
            return round(latency * 1000, 2)  # para milissegundos
    except Exception:
        pass
    return None

# Função principal de coleta
def collect_data():
    global key_count, mouse_clicks
    prev_net = psutil.net_io_counters()
    time.sleep(SEND_INTERVAL)
    curr_net = psutil.net_io_counters()

    timestamp = datetime.now(timezone.utc).isoformat()
    boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
    latency_ms = get_latency(PING_HOST)

    hostname = socket.gethostname()

    # GPU
    gpu_info = []
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            gpu_info.append({
                "name": gpu.name,
                "load": gpu.load,
                "memoryUtil": gpu.memoryUtil,
                "temperature": gpu.temperature
            })
    except Exception:
        gpu_info = []

    # Top processos
    top_procs = sorted(
        [(p.info["name"], p.info["cpu_percent"]) for p in psutil.process_iter(["name", "cpu_percent"]) if p.info["cpu_percent"]],
        key=lambda x: x[1],
        reverse=True
    )[:5]

    idle_time = time.time() - last_input_time

    # Temperaturas (tratamento para sistemas que não suportam)
    try:
        temps = {k: [t.current for t in v] for k, v in psutil.sensors_temperatures().items()}
    except Exception:
        temps = {}

    data = {
        "timestamp": timestamp,
        "hostname": hostname,
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else None,
        "boot_time": boot_time,
        "processes": len(psutil.pids()),
        "swap": psutil.swap_memory().percent,
        "net_io": {
            "bytes_sent": curr_net.bytes_sent,
            "bytes_recv": curr_net.bytes_recv
        },
        "net_speed": {
            "upload_speed_MBps": round((curr_net.bytes_sent - prev_net.bytes_sent) / SEND_INTERVAL / 1024 / 1024, 3),
            "download_speed_MBps": round((curr_net.bytes_recv - prev_net.bytes_recv) / SEND_INTERVAL / 1024 / 1024, 3),
        },
        "disk_io": {
            "read_count": psutil.disk_io_counters().read_count,
            "write_count": psutil.disk_io_counters().write_count,
            "read_bytes": psutil.disk_io_counters().read_bytes,
            "write_bytes": psutil.disk_io_counters().write_bytes
        },
        "temps": temps,
        "gpu": gpu_info,
        "top_processes": top_procs,
        "latency_ms": latency_ms,
        "keys_per_min": key_count * (60 // SEND_INTERVAL),
        "mouse_clicks_per_min": mouse_clicks * (60 // SEND_INTERVAL),
        "idle_time_sec": round(idle_time, 2),
        "key_counts": dict(key_counter),
        "platform": platform.platform()
    }

    # Reset counters
    key_count = 0
    mouse_clicks = 0

    return data

# Loop principal de envio
if __name__ == "__main__":
    while True:
        info = collect_data()
        json_data = json.dumps(info)
        b64_payload = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
        client.publish(MQTT_TOPIC, b64_payload)
        print(f"[{datetime.now().isoformat()}] Dados enviados com sucesso.")
