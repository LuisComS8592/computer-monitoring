# Computer Monitoring

Projeto para monitoramento de métricas de sistema (CPU, RAM, disco, GPU, latência, processos, teclado e mouse) com coleta em Python, transmissão via MQTT, processamento e armazenamento no InfluxDB usando Node-RED.

---

## Estrutura do Projeto

```
computer monitoring/
│
├── src/
│ └── monitoring.py # Script Python para coleta e envio de dados
│
├── node-red/
│ └── flow.json # Fluxo Node-RED para receber, decodificar e armazenar os dados
│
├── LICENSE # Licença do projeto
├── requirements.txt # Dependências Python
├── README.md # Documentação do projeto
```

---

## Funcionalidades

- Coleta de métricas detalhadas do sistema:
  - CPU, RAM, disco, swap
  - Temperaturas e uso de GPU
  - Latência de rede
  - Processos em execução
  - Eventos de teclado e mouse
  - Estatísticas de rede e disco I/O

- Envio seguro dos dados via MQTT (codificados em Base64 JSON)

- Decodificação, transformação e armazenamento no InfluxDB via fluxo Node-RED

- Visualização e análise de dados em ferramentas compatíveis com InfluxDB

---

## Requisitos

- Python 3.7+
- Node-RED
- InfluxDB 2.x
- Broker MQTT (ex: [broker.emqx.io](https://broker.emqx.io) ou local)

---

## Instalação

1. Clone o repositório:

```
git clone https://github.com/LuisComS8592/computer-monitoring.git
cd computer-monitoring
```

2. Crie e ative ambiente virtual Python (opcional, mas recomendado):

```
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Instale as dependências Python:

```
pip install -r requirements.txt
```

4. Importe o fluxo Node-RED:

- Abra o Node-RED
- Importe o arquivo node-red/flow.json

5. Configure o InfluxDB e o broker MQTT conforme necessário.

## Uso

1. Execute o script de monitoramento:

```
python src/monitoring.py
```

2. O script começará a coletar dados e enviar via MQTT.
3. No Node-RED, o fluxo receberá, decodificará e armazenará os dados no InfluxDB.
4. Use sua ferramenta preferida para consultar e visualizar os dados no InfluxDB.

## Personalização

- Ajuste parâmetros do script Python (tópico MQTT, intervalo de coleta, host MQTT) no monitoring.py.
- Configure o fluxo Node-RED para seu ambiente (broker, bucket do InfluxDB, etc).
- Altere o banco InfluxDB para refletir seu setup.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
