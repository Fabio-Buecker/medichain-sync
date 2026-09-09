# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Funcoes pequenas para conectar e publicar mensagens no RabbitMQ."""

# Adia a avaliação das anotações de tipos para evitar dependências em tempo de definição.
from __future__ import annotations

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa time para disponibilizar suas funções neste módulo.
import time
# Importa Any de typing.
from typing import Any

# Importa pika para disponibilizar suas funções neste módulo.
import pika


# Nomeia a fila de atualizações recebidas pelo gateway.
UPDATES_QUEUE = "medichain.updates"
# Nomeia a fila de resultados que aguardam consolidação pelo líder.
PROCESSED_QUEUE = "medichain.processed"


# Define connect_with_retry; os parâmetros e tipos descrevem suas entradas e seu retorno.
def connect_with_retry(host: str, attempts: int = 20) -> pika.BlockingConnection:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Tenta conectar algumas vezes porque o broker pode ainda estar iniciando."""

    # Calcula a expressão à direita e guarda o resultado em last_error: Exception | None.
    last_error: Exception | None = None
    # Repete o bloco para cada attempt encontrado em range(1, attempts + 1).
    for attempt in range(1, attempts + 1):
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Configura o endereço do RabbitMQ e o heartbeat AMQP de 30 segundos.
            parameters = pika.ConnectionParameters(host=host, heartbeat=30)
            # Devolve pika.BlockingConnection(parameters) ao código que chamou a função.
            return pika.BlockingConnection(parameters)
        # Trata pika.exceptions.AMQPError as error produzida no bloco protegido.
        except pika.exceptions.AMQPError as error:
            # Calcula a expressão à direita e guarda o resultado em last_error.
            last_error = error
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[BROKER] Tentativa {attempt}/{attempts} falhou: {error}", flush=True)
            # Pausa esta thread pelo intervalo informado.
            time.sleep(2)
    # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
    raise ConnectionError(f"Nao foi possivel conectar ao RabbitMQ: {last_error}")


# Define prepare_channel; os parâmetros e tipos descrevem suas entradas e seu retorno.
def prepare_channel(connection: pika.BlockingConnection) -> pika.adapters.blocking_connection.BlockingChannel:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Cria as filas duraveis e pede uma mensagem por worker de cada vez."""

    # Abre um canal lógico AMQP sobre a conexão RabbitMQ.
    channel = connection.channel()
    # Declara uma fila durável; a durabilidade também depende da configuração do broker.
    channel.queue_declare(queue=UPDATES_QUEUE, durable=True)
    # Declara uma fila durável; a durabilidade também depende da configuração do broker.
    channel.queue_declare(queue=PROCESSED_QUEUE, durable=True)
    # Configura prefetch no canal; basic_get não usa esse limite para distribuir mensagens.
    channel.basic_qos(prefetch_count=1)
    # Devolve channel ao código que chamou a função.
    return channel


# Define publish_json; os parâmetros e tipos descrevem suas entradas e seu retorno.
def publish_json(
    # Declara channel: pika.adapters.blocking_connection.BlockingChannel como campo tipado ou parâmetro da estrutura em definição.
    channel: pika.adapters.blocking_connection.BlockingChannel,
    # Declara queue_name: str como campo tipado ou parâmetro da estrutura em definição.
    queue_name: str,
    # Declara message: dict[str, Any] como campo tipado ou parâmetro da estrutura em definição.
    message: dict[str, Any],
# Fecha os parâmetros e informa o tipo de retorno da função.
) -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Publica JSON persistente para que a fila sobreviva a reinicios do broker."""

    # Serializa os dados em texto JSON.
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    # Monta os metadados AMQP, incluindo persistência, ID e correlação.
    properties = pika.BasicProperties(
        # Fornece o argumento nomeado content_type à chamada em andamento.
        content_type="application/json",
        # Fornece o argumento nomeado delivery_mode à chamada em andamento.
        delivery_mode=pika.DeliveryMode.Persistent,
        # Fornece o argumento nomeado message_id à chamada em andamento.
        message_id=str(message.get("event_id", "")),
        # Fornece o argumento nomeado correlation_id à chamada em andamento.
        correlation_id=str(message.get("correlation_id", "")),
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    )
    # Envia a mensagem ao RabbitMQ com os parâmetros abaixo.
    channel.basic_publish(
        # Fornece o argumento nomeado exchange à chamada em andamento.
        exchange="",
        # Fornece o argumento nomeado routing_key à chamada em andamento.
        routing_key=queue_name,
        # Fornece o argumento nomeado body à chamada em andamento.
        body=body,
        # Fornece o argumento nomeado properties à chamada em andamento.
        properties=properties,
        # Fornece o argumento nomeado mandatory à chamada em andamento.
        mandatory=True,
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    )
