# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Worker concorrente: consome, carimba, e quando lider consolida os eventos."""

# Adia a avaliação das anotações de tipos para evitar dependências em tempo de definição.
from __future__ import annotations

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa os para disponibilizar suas funções neste módulo.
import os
# Importa threading para disponibilizar suas funções neste módulo.
import threading
# Importa time para disponibilizar suas funções neste módulo.
import time

# Importa pika para disponibilizar suas funções neste módulo.
import pika

# Importa ( de src.broker.
from src.broker import (
    # Fornece PROCESSED_QUEUE à declaração ou chamada iniciada acima.
    PROCESSED_QUEUE,
    # Fornece UPDATES_QUEUE à declaração ou chamada iniciada acima.
    UPDATES_QUEUE,
    # Fornece connect_with_retry à declaração ou chamada iniciada acima.
    connect_with_retry,
    # Fornece prepare_channel à declaração ou chamada iniciada acima.
    prepare_channel,
    # Fornece publish_json à declaração ou chamada iniciada acima.
    publish_json,
# Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
)
# Importa env_float, env_int, load_peers de src.config.
from src.config import env_float, env_int, load_peers
# Importa BullyElection de src.election.
from src.election import BullyElection
# Importa MedicalRecordUpdate de src.models.
from src.models import MedicalRecordUpdate
# Importa ReplicatedStorage de src.storage.
from src.storage import ReplicatedStorage
# Importa increment_clock, merge_clocks de src.vector_clock.
from src.vector_clock import increment_clock, merge_clocks


# Define a classe Worker, que agrupa os dados e comportamentos abaixo.
class Worker:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Une consumo competitivo, relogio vetorial, eleicao e persistencia."""

    # Define __init__; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def __init__(self) -> None:
        # Guarda o ID deste worker, usado na eleição e no registro dos eventos.
        self.worker_id = env_int("WORKER_ID", 1)
        # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
        self.storage = ReplicatedStorage(os.getenv("DATA_DIR", "./data"))
        # Calcula a expressão à direita e guarda o resultado em self._processing_clock: dict[str, int].
        self._processing_clock: dict[str, int] = {}
        # Cria uma trava para proteger dados compartilhados entre threads.
        self._clock_lock = threading.Lock()
        # Calcula a expressão à direita e guarda o resultado em self.election.
        self.election = BullyElection(
            # Fornece o argumento nomeado worker_id à chamada em andamento.
            worker_id=self.worker_id,
            # Fornece o argumento nomeado peers à chamada em andamento.
            peers=load_peers(),
            # Fornece o argumento nomeado heartbeat_interval à chamada em andamento.
            heartbeat_interval=env_float("HEARTBEAT_INTERVAL", 1.0),
            # Fornece o argumento nomeado heartbeat_failures à chamada em andamento.
            heartbeat_failures=env_int("HEARTBEAT_FAILURES", 3),
            # Fornece o argumento nomeado on_leader_change à chamada em andamento.
            on_leader_change=self._show_leader_change,
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        )

    # Define _show_leader_change; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _show_leader_change(self, leader_id: int | None) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Exibe uma evidencia clara da eleicao para a demonstracao."""

        # Escolhe o texto LIDER ou SEGUIDOR para mostrar o papel deste worker no console.
        role = "LIDER" if leader_id == self.worker_id else "SEGUIDOR"
        # Exibe informações no terminal para acompanhar a execução.
        print(f"[WORKER {self.worker_id}] Papel={role}; lider={leader_id}.", flush=True)

    # Define _stamp_processing_event; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _stamp_processing_event(self, update: MedicalRecordUpdate) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Mescla o relogio recebido e incrementa este worker em secao critica."""

        # Forma o nome deste worker para identificar sua posição no vetor.
        worker_name = f"worker_{self.worker_id}"
        # Mantém a trava adquirida durante este bloco e a libera automaticamente ao sair.
        with self._clock_lock:
            # Combina os vetores usando o maior contador de cada participante.
            merged = merge_clocks(self._processing_clock, update.processing_clock)
            # Incrementa o contador do participante no vetor.
            self._processing_clock = increment_clock(merged, worker_name)
            # Copia o vetor local para a mensagem sem compartilhar o mesmo dicionário mutável.
            update.processing_clock = dict(self._processing_clock)

    # Define _process_update; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _process_update(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara channel: pika.adapters.blocking_connection.BlockingChannel como campo tipado ou parâmetro da estrutura em definição.
        channel: pika.adapters.blocking_connection.BlockingChannel,
        # Declara delivery_tag: int como campo tipado ou parâmetro da estrutura em definição.
        delivery_tag: int,
        # Declara body: bytes como campo tipado ou parâmetro da estrutura em definição.
        body: bytes,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Processa uma entrada, publica o resultado e so entao confirma a original."""

        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Converte o JSON recebido em estruturas de dados Python.
            raw_message = json.loads(body.decode("utf-8"))
            # Reconstrói e valida a atualização retirada da fila.
            update = MedicalRecordUpdate.from_queue_dict(raw_message)
            # Mescla o vetor recebido e incrementa o contador deste worker sob proteção da trava.
            self._stamp_processing_event(update)
            # Converte a atualização em um dicionário para transmissão.
            processed = update.to_dict()
            # Acrescenta ao resultado o ID do worker que fez o processamento.
            processed["processed_by"] = self.worker_id
            # Publica o evento na fila RabbitMQ indicada.
            publish_json(channel, PROCESSED_QUEUE, processed)
            # Confirma ao RabbitMQ que esta entrega foi concluída.
            channel.basic_ack(delivery_tag=delivery_tag)
            # Exibe informações no terminal para acompanhar a execução.
            print(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"[WORKER {self.worker_id}] Processou {update.event_id}; "
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"vetor={update.processing_clock}.",
                # Fornece o argumento nomeado flush à chamada em andamento.
                flush=True,
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
        # Trata Exception as error produzida no bloco protegido.
        except Exception as error:
            # Recusa a entrega e solicita que a mensagem volte à fila.
            channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[WORKER {self.worker_id}] Erro; mensagem recolocada: {error}", flush=True)

    # Define _consolidate_if_leader; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _consolidate_if_leader(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara channel: pika.adapters.blocking_connection.BlockingChannel como campo tipado ou parâmetro da estrutura em definição.
        channel: pika.adapters.blocking_connection.BlockingChannel,
        # Declara delivery_tag: int como campo tipado ou parâmetro da estrutura em definição.
        delivery_tag: int,
        # Declara body: bytes como campo tipado ou parâmetro da estrutura em definição.
        body: bytes,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Persiste o resultado apenas enquanto este worker for o lider eleito."""

        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Converte o JSON recebido em estruturas de dados Python.
            raw_message = json.loads(body.decode("utf-8"))
            # Reconstrói e valida a atualização retirada da fila.
            update = MedicalRecordUpdate.from_queue_dict(raw_message)
            # Recupera o ID do worker de origem para registrar a autoria na auditoria.
            source_worker_id = int(raw_message["processed_by"])
            # Consulta quem é o líder atualmente reconhecido pelo algoritmo local.
            leader_id = self.election.leader_id
            # Executa este ramo quando leader_id != self.worker_id for verdadeiro.
            if leader_id != self.worker_id:
                # Recusa a entrega e solicita que a mensagem volte à fila.
                channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
                # Encerra esta chamada sem retornar um valor útil.
                return

            # Recebe a relação causal e a decisão devolvidas pela consolidação.
            relation, decision = self.storage.consolidate(
                # Fornece o argumento nomeado update à chamada em andamento.
                update=update,
                # Fornece o argumento nomeado worker_id à chamada em andamento.
                worker_id=source_worker_id,
                # Fornece o argumento nomeado leader_id à chamada em andamento.
                leader_id=leader_id,
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
            # Confirma ao RabbitMQ que esta entrega foi concluída.
            channel.basic_ack(delivery_tag=delivery_tag)
            # Exibe informações no terminal para acompanhar a execução.
            print(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"[LIDER {self.worker_id}] Consolidou {update.event_id}; "
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"relacao={relation}; decisao={decision}; clinico={update.clinical_clock}.",
                # Fornece o argumento nomeado flush à chamada em andamento.
                flush=True,
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
        # Trata Exception as error produzida no bloco protegido.
        except Exception as error:
            # Recusa a entrega e solicita que a mensagem volte à fila.
            channel.basic_nack(delivery_tag=delivery_tag, requeue=True)
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[LIDER {self.worker_id}] Falha; mensagem recolocada: {error}", flush=True)

    # Define run; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def run(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Mantem o worker ativo e reconecta ao broker depois de falha de comunicacao."""

        # Inicia a execução da thread ou componente.
        self.election.start()
        # Exibe informações no terminal para acompanhar a execução.
        print(f"[WORKER {self.worker_id}] Iniciado.", flush=True)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Repete o bloco enquanto True for verdadeiro.
            while True:
                # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
                try:
                    # Mantém o laço de busca e processamento até ocorrer uma falha de conexão.
                    self._consume_until_connection_fails()
                # Trata (pika.exceptions.AMQPError, ConnectionError, OSError) as error produzida no bloco protegido.
                except (pika.exceptions.AMQPError, ConnectionError, OSError) as error:
                    # Exibe informações no terminal para acompanhar a execução.
                    print(f"[WORKER {self.worker_id}] RabbitMQ indisponivel: {error}", flush=True)
                    # Pausa esta thread pelo intervalo informado.
                    time.sleep(2)
        # Trata KeyboardInterrupt produzida no bloco protegido.
        except KeyboardInterrupt:
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[WORKER {self.worker_id}] Encerramento solicitado.", flush=True)
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Solicita o encerramento do componente.
            self.election.stop()

    # Define _consume_until_connection_fails; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _consume_until_connection_fails(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Busca uma mensagem por vez para repartir a carga entre os tres workers."""

        # Tenta conectar ao RabbitMQ com retentativas limitadas.
        connection = connect_with_retry(self.rabbitmq_host)
        # Abre o canal AMQP e declara as filas usadas pelo projeto.
        channel = prepare_channel(connection)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Repete o bloco enquanto True for verdadeiro.
            while True:
                # Marca que esta passagem do laço ainda não encontrou nenhuma tarefa.
                did_work = False
                # Busca uma entrega na fila sem confirmação automática.
                method, _, body = channel.basic_get(queue=UPDATES_QUEUE, auto_ack=False)
                # Executa este ramo quando method for verdadeiro.
                if method:
                    # Marca que uma tarefa foi encontrada para evitar a espera de ociosidade.
                    did_work = True
                    # Processa a entrega recebida e confirma ou devolve sua mensagem à fila.
                    self._process_update(channel, method.delivery_tag, body)

                # Executa este ramo quando self.election.is_leader for verdadeiro.
                if self.election.is_leader:
                    # Busca uma entrega na fila sem confirmação automática.
                    method, _, body = channel.basic_get(queue=PROCESSED_QUEUE, auto_ack=False)
                    # Executa este ramo quando method for verdadeiro.
                    if method:
                        # Marca que uma tarefa foi encontrada para evitar a espera de ociosidade.
                        did_work = True
                        # Verifica novamente a liderança e consolida o resultado recebido.
                        self._consolidate_if_leader(channel, method.delivery_tag, body)

                # Executa este ramo quando not did_work for verdadeiro.
                if not did_work:
                    # Atende eventos da conexão AMQP e heartbeats enquanto aguarda trabalho.
                    connection.process_data_events(time_limit=0.2)
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Executa este ramo quando connection.is_open for verdadeiro.
            if connection.is_open:
                # Fecha o recurso e libera a conexão ou socket.
                connection.close()


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa Worker().run() para continuar a operação desta função.
    Worker().run()
