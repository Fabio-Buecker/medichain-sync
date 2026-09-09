# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Ponto de entrada TCP concorrente que responde antes do processamento pesado."""

# Importa os para disponibilizar suas funções neste módulo.
import os
# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa threading para disponibilizar suas funções neste módulo.
import threading
# Importa Any de typing.
from typing import Any

# Importa UPDATES_QUEUE, connect_with_retry, prepare_channel, publish_json de src.broker.
from src.broker import UPDATES_QUEUE, connect_with_retry, prepare_channel, publish_json
# Importa env_int de src.config.
from src.config import env_int
# Importa MedicalRecordUpdate de src.models.
from src.models import MedicalRecordUpdate
# Importa receive_json, send_json de src.protocol.
from src.protocol import receive_json, send_json


# Define enqueue_update; os parâmetros e tipos descrevem suas entradas e seu retorno.
def enqueue_update(message: dict[str, Any]) -> MedicalRecordUpdate:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Valida uma atualizacao e a deposita de forma duravel no RabbitMQ."""

    # Valida os dados recebidos do cliente e monta a entidade.
    update = MedicalRecordUpdate.from_client_dict(message)
    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    # Tenta conectar ao RabbitMQ com retentativas limitadas.
    connection = connect_with_retry(rabbitmq_host, attempts=3)
    # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
    try:
        # Abre o canal AMQP e declara as filas usadas pelo projeto.
        channel = prepare_channel(connection)
        # Publica o evento na fila RabbitMQ indicada.
        publish_json(channel, UPDATES_QUEUE, update.to_dict())
    # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
    finally:
        # Fecha o recurso e libera a conexão ou socket.
        connection.close()
    # Devolve update ao código que chamou a função.
    return update


# Define handle_client; os parâmetros e tipos descrevem suas entradas e seu retorno.
def handle_client(client: socket.socket, address: tuple[str, int]) -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Atende um cliente em thread separada para nao bloquear novas conexoes."""

    # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
    try:
        # Define o limite de espera das operações do socket em segundos.
        client.settimeout(10)
        # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
        message = receive_json(client)
        # Calcula a expressão à direita e guarda o resultado em update.
        update = enqueue_update(message)
        # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
        send_json(
            # Fornece client à declaração ou chamada iniciada acima.
            client,
            # Fornece { à declaração ou chamada iniciada acima.
            {
                # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
                "status": "queued",
                # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
                "event_id": update.event_id,
                # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
                "correlation_id": update.correlation_id,
                # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
                "explanation": "Recebido pelo gateway; processamento continua assincronamente.",
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            },
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        )
        # Exibe informações no terminal para acompanhar a execução.
        print(f"[GATEWAY] {address} enfileirou evento {update.event_id}.", flush=True)
    # Trata (ValueError, ConnectionError, TimeoutError, OSError) as error produzida no bloco protegido.
    except (ValueError, ConnectionError, TimeoutError, OSError) as error:
        # Exibe informações no terminal para acompanhar a execução.
        print(f"[GATEWAY] Falha ao atender {address}: {error}", flush=True)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(client, {"status": "error", "explanation": str(error)})
        # Trata OSError produzida no bloco protegido.
        except OSError:
            # Não executa outra ação neste tratamento; o fluxo segue para a limpeza.
            pass
    # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
    finally:
        # Fecha o recurso e libera a conexão ou socket.
        client.close()


# Define run_gateway; os parâmetros e tipos descrevem suas entradas e seu retorno.
def run_gateway() -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Abre o Socket TCP e cria uma thread daemon para cada cliente conectado."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    # Calcula a expressão à direita e guarda o resultado em port.
    port = env_int("GATEWAY_PORT", 5000)
    # Cria um socket IPv4 de fluxo TCP.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar o endereço do socket após seu encerramento.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Associa o socket ao endereço e à porta de escuta.
    server.bind((host, port))
    # Habilita a aceitação de conexões com a fila de espera indicada.
    server.listen(50)
    # Exibe informações no terminal para acompanhar a execução.
    print(f"[GATEWAY] Escutando em {host}:{port}.", flush=True)

    # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
    try:
        # Repete o bloco enquanto True for verdadeiro.
        while True:
            # Aguarda uma conexão e retorna o socket do cliente e seu endereço.
            client, address = server.accept()
            # Prepara uma thread para executar a função indicada.
            thread = threading.Thread(target=handle_client, args=(client, address), daemon=True)
            # Inicia a execução da thread ou componente.
            thread.start()
    # Trata KeyboardInterrupt produzida no bloco protegido.
    except KeyboardInterrupt:
        # Exibe informações no terminal para acompanhar a execução.
        print("[GATEWAY] Encerramento solicitado.", flush=True)
    # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
    finally:
        # Fecha o recurso e libera a conexão ou socket.
        server.close()


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa run_gateway() para continuar a operação desta função.
    run_gateway()
