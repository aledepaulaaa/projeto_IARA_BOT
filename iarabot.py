import os
import time
import logging
import requests
import schedule
from dotenv import load_dotenv

# --- Configuração Inicial ---
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura um sistema de logging para exibir informações de forma organizada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Pega as configurações do ambiente
BASE_URL = os.getenv('BASE_URL')
CRON_SECRET = os.getenv('CRON_SECRET')

# Validação inicial para garantir que as variáveis foram carregadas
if not BASE_URL or not CRON_SECRET:
    logging.error("Erro Crítico: As variáveis de ambiente BASE_URL e CRON_SECRET não foram definidas.")
    exit()

# --- Função Principal de Gatilho ---

def trigger_api_endpoint(path: str):
    """
    Função genérica para fazer uma requisição GET a um endpoint da API.
    Ela adiciona o cabeçalho de autorização e loga o resultado.
    """
    full_url = f"{BASE_URL}{path}"
    headers = {
        'Authorization': f'Bearer {CRON_SECRET}'
    }
    
    try:
        logging.info(f"Disparando tarefa para: {full_url}")
        # Adiciona um timeout de 60 segundos para evitar que a requisição fique presa
        response = requests.get(full_url, headers=headers, timeout=60)
        
        # Verifica se a requisição foi bem-sucedida (código de status 2xx)
        if response.ok:
            logging.info(f"Sucesso! Endpoint {path} respondeu com status {response.status_code}.")
        else:
            logging.warning(f"Aviso! Endpoint {path} respondeu com erro: Status {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro de conexão ao tentar acessar {full_url}: {e}")

# --- Definição das Tarefas (Jobs) ---
# Cada função corresponde a um cron job do seu vercel.json

def job_eventos_proximos():
    trigger_api_endpoint("/api/planner/verificarplanner?modo=eventos_proximos")

def job_whatsapp_eventos_proximos():
    trigger_api_endpoint("/api/whatsapp/enviarlembrete?modo=eventos_proximos_whatsapp")

def job_resumo_matinal():
    trigger_api_endpoint("/api/planner/verificarplanner?modo=resumo_matinal")

def job_eventos_futuros():
    trigger_api_endpoint("/api/planner/verificarplanner?modo=eventos_futuros")

def job_verificar_organizadores():
    trigger_api_endpoint("/api/organizadorprojetos/verificarorganizadores")

def job_limpeza_cache():
    trigger_api_endpoint("/api/planner/limpeza?tipo=cache_antigo")

def job_limpeza_tokens():
    trigger_api_endpoint("/api/planner/limpeza?tipo=tokens_inativos")

    

# --- Agendamento das Tarefas ---

logging.info("Iniciando o agendador de tarefas do IaraBot...")

# IMPORTANTE: O schedule da Vercel usa o fuso horário UTC.
# Se sua máquina estiver em UTC-3 (Horário de Brasília), ajuste os horários.
# Ex: "0 11 * * *" (11:00 UTC) se torna "08:00" no horário local de Brasília.
# Estou usando os horários convertidos para BRT (UTC-3).

# Tarefa 1: Roda a cada 2 minutos
schedule.every(2).minutes.do(job_eventos_proximos)

# Tarefa 2: Roda a cada 2 minutos
schedule.every(2).minutes.do(job_whatsapp_eventos_proximos)

# Tarefa 2: Roda todo dia às 08:00 (equivalente a 11:00 UTC)
schedule.every().day.at("08:00").do(job_resumo_matinal)

# Tarefa 3: Roda a cada 15 minutos
schedule.every(15).minutes.do(job_eventos_futuros)

# Tarefa 4: Roda todo dia às 10:00 (equivalente a 13:00 UTC)
schedule.every().day.at("10:00").do(job_verificar_organizadores)

# Tarefa 5: Roda todo dia às 09:00 (equivalente a 12:00 UTC)
schedule.every().day.at("09:00").do(job_limpeza_cache)

# Tarefa 6: Roda todo dia às 10:00 (equivalente a 13:00 UTC)
schedule.every().day.at("10:00").do(job_limpeza_tokens)


logging.info("Agendamentos configurados. O bot está no ar.")
print("---")
print("✅ IaraBot está rodando. Pressione CTRL+C para parar.")
print("---")


# --- Loop de Execução ---

try:
    while True:
        # Executa as tarefas que estão pendentes de acordo com o agendamento
        schedule.run_pending()
        # Espera 1 segundo antes de checar novamente para não sobrecarregar o processador
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Parando o IaraBot... Até mais!")