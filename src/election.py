# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Algoritmo do Valentao (Bully) com Socket TCP e heartbeat."""

# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa threading para disponibilizar suas funções neste módulo.
import threading
# Importa time para disponibilizar suas funções neste módulo.
import time
# Importa Any, Callable de typing.
from typing import Any, Callable

# Importa Peer de src.config.
from src.config import Peer
# Importa receive_json, send_json de src.protocol.
from src.protocol import receive_json, send_json


# Define a classe BullyElection, que agrupa os dados e comportamentos abaixo.
class BullyElection:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Elege como lider o maior ID de worker que estiver respondendo."""

    # Define __init__; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def __init__(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
        worker_id: int,
        # Declara peers: dict[int, Peer] como campo tipado ou parâmetro da estrutura em definição.
        peers: dict[int, Peer],
        # Calcula a expressão à direita e guarda o resultado em heartbeat_interval: float.
        heartbeat_interval: float = 1.0,
        # Calcula a expressão à direita e guarda o resultado em heartbeat_failures: int.
        heartbeat_failures: int = 3,
        # Calcula a expressão à direita e guarda o resultado em on_leader_change: Callable[[int | None], None] | None.
        on_leader_change: Callable[[int | None], None] | None = None,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> None:
        # Guarda o ID deste worker, usado na eleição e no registro dos eventos.
        self.worker_id = worker_id
        # Guarda os endereços dos workers conhecidos na rede.
        self.peers = peers
        # Guarda o intervalo entre verificações de disponibilidade do líder.
        self.heartbeat_interval = heartbeat_interval
        # Guarda quantas falhas seguidas levam a iniciar nova eleição.
        self.heartbeat_failures = heartbeat_failures
        # Guarda a função que será avisada quando o líder mudar.
        self.on_leader_change = on_leader_change
        # Guarda o líder conhecido; None representa uma eleição sem resultado.
        self._leader_id: int | None = None
        # Cria uma trava para proteger dados compartilhados entre threads.
        self._state_lock = threading.Lock()
        # Cria uma trava para proteger dados compartilhados entre threads.
        self._election_lock = threading.Lock()
        # Cria um sinal compartilhado para controlar o encerramento.
        self._stop_event = threading.Event()

    # Permite consultar o método como um atributo.
    @property
    # Define leader_id; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def leader_id(self) -> int | None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Devolve o lider atual com leitura protegida contra concorrencia local."""

        # Mantém a trava adquirida durante este bloco e a libera automaticamente ao sair.
        with self._state_lock:
            # Devolve self._leader_id ao código que chamou a função.
            return self._leader_id

    # Permite consultar o método como um atributo.
    @property
    # Define is_leader; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def is_leader(self) -> bool:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Indica se este proprio worker e o coordenador atual."""

        # Devolve self.leader_id == self.worker_id ao código que chamou a função.
        return self.leader_id == self.worker_id

    # Define start; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def start(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Inicia o servidor de coordenacao, o heartbeat e a primeira eleicao."""

        # Prepara uma thread para executar a função indicada.
        server_thread = threading.Thread(target=self._serve, daemon=True)
        # Prepara uma thread para executar a função indicada.
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        # Inicia a execução da thread ou componente.
        server_thread.start()
        # Inicia a execução da thread ou componente.
        heartbeat_thread.start()
        # Prepara uma thread para executar a função indicada.
        threading.Thread(target=self._delayed_first_election, daemon=True).start()

    # Define stop; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def stop(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Sinaliza o encerramento das threads auxiliares."""

        # Ativa o sinal que faz as threads auxiliares encerrarem seus laços.
        self._stop_event.set()

    # Define _delayed_first_election; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _delayed_first_election(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Espera a porta abrir antes de iniciar a disputa de lideranca."""

        # Pausa esta thread pelo intervalo informado.
        time.sleep(1.0 + self.worker_id * 0.2)
        # Executa este ramo quando self.leader_id is None for verdadeiro.
        if self.leader_id is None:
            # Inicia a disputa de liderança entre este worker e os IDs maiores.
            self.start_election()

    # Define _set_leader; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _set_leader(self, leader_id: int | None) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Atualiza o estado e avisa o worker somente quando houver mudanca."""

        # Mantém a trava adquirida durante este bloco e a libera automaticamente ao sair.
        with self._state_lock:
            # Compara o líder anterior com o recebido para saber se é preciso notificar uma mudança.
            changed = self._leader_id != leader_id
            # Guarda o líder conhecido; None representa uma eleição sem resultado.
            self._leader_id = leader_id
        # Executa este ramo quando changed for verdadeiro.
        if changed:
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[ELEICAO] Worker {self.worker_id}: lider agora e {leader_id}.", flush=True)
            # Executa este ramo quando self.on_leader_change for verdadeiro.
            if self.on_leader_change:
                # Chama a função de notificação para informar a mudança de líder.
                self.on_leader_change(leader_id)

    # Define start_election; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def start_election(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Pergunta aos IDs maiores; sem resposta, declara este no como lider."""

        # Executa este ramo quando not self._election_lock.acquire(blocking=False) for verdadeiro.
        if not self._election_lock.acquire(blocking=False):
            # Encerra esta chamada sem retornar um valor útil.
            return
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Apaga o líder conhecido enquanto uma nova eleição está em andamento.
            self._set_leader(None)
            # Seleciona e ordena apenas os workers com ID maior que este, conforme a regra do Bully.
            higher_ids = sorted(worker_id for worker_id in self.peers if worker_id > self.worker_id)
            # Registra se algum worker de ID maior respondeu à disputa.
            higher_answered = False
            # Repete o bloco para cada higher_id encontrado em higher_ids.
            for higher_id in higher_ids:
                # Calcula a expressão à direita e guarda o resultado em response.
                response = self._request(higher_id, {"type": "ELECTION", "from": self.worker_id})
                # Executa este ramo quando response and response.get("type") == "OK" for verdadeiro.
                if response and response.get("type") == "OK":
                    # Registra se algum worker de ID maior respondeu à disputa.
                    higher_answered = True

            # Executa este ramo quando not higher_answered for verdadeiro.
            if not higher_answered:
                # Registra este worker como líder e anuncia a decisão aos demais.
                self._become_leader()
                # Encerra esta chamada sem retornar um valor útil.
                return

            # Consulta um contador de tempo para medir o timeout, sem ordenar eventos clínicos.
            deadline = time.monotonic() + 3.0
            # Repete o bloco enquanto time.monotonic() < deadline and self.leader_id is None for verdadeiro.
            while time.monotonic() < deadline and self.leader_id is None:
                # Pausa esta thread pelo intervalo informado.
                time.sleep(0.1)
            # Executa este ramo quando self.leader_id is None for verdadeiro.
            if self.leader_id is None:
                # Registra este worker como líder e anuncia a decisão aos demais.
                self._become_leader()
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Libera a trava para permitir outra eleição.
            self._election_lock.release()

    # Define _become_leader; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _become_leader(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Assume a lideranca e anuncia a decisao para todos os outros nos."""

        # Executa self._set_leader(self.worker_id) para continuar a operação desta função.
        self._set_leader(self.worker_id)
        # Repete o bloco para cada peer_id encontrado em sorted(self.peers).
        for peer_id in sorted(self.peers):
            # Executa este ramo quando peer_id != self.worker_id for verdadeiro.
            if peer_id != self.worker_id:
                # Declara self._request(peer_id, {"type": "COORDINATOR", "leader_id": self.worker_id}) como campo tipado ou parâmetro da estrutura em definição.
                self._request(peer_id, {"type": "COORDINATOR", "leader_id": self.worker_id})

    # Define _serve; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _serve(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Aceita mensagens de eleicao em uma porta TCP exclusiva do worker."""

        # Obtém o host e a porta do worker selecionado para a comunicação.
        peer = self.peers[self.worker_id]
        # Cria um socket IPv4 de fluxo TCP.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reutilizar o endereço do socket após seu encerramento.
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Associa o socket ao endereço e à porta de escuta.
        server.bind(("0.0.0.0", peer.port))
        # Habilita a aceitação de conexões com a fila de espera indicada.
        server.listen(10)
        # Define o limite de espera das operações do socket em segundos.
        server.settimeout(1.0)
        # Exibe informações no terminal para acompanhar a execução.
        print(f"[ELEICAO] Worker {self.worker_id} ouvindo na porta {peer.port}.", flush=True)

        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Repete o bloco enquanto not self._stop_event.is_set() for verdadeiro.
            while not self._stop_event.is_set():
                # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
                try:
                    # Aguarda uma conexão e retorna o socket do cliente e seu endereço.
                    client, _ = server.accept()
                # Trata socket.timeout produzida no bloco protegido.
                except socket.timeout:
                    # Pula o restante desta iteração e volta à próxima passagem do laço.
                    continue
                # Prepara uma thread para executar a função indicada.
                threading.Thread(target=self._handle_peer, args=(client,), daemon=True).start()
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            server.close()

    # Define _handle_peer; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _handle_peer(self, client: socket.socket) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Responde PING, ELECTION ou registra o COORDINATOR anunciado."""

        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Define o limite de espera das operações do socket em segundos.
            client.settimeout(2.0)
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            message = receive_json(client)
            # Lê o tipo da mensagem para escolher entre heartbeat, eleição ou anúncio de líder.
            message_type = message.get("type")

            # Executa este ramo quando message_type == "PING" for verdadeiro.
            if message_type == "PING":
                # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                send_json(client, {"type": "PONG", "worker_id": self.worker_id})
            # Executa este ramo quando message_type == "ELECTION" for verdadeiro.
            elif message_type == "ELECTION":
                # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                send_json(client, {"type": "OK", "worker_id": self.worker_id})
                # Escolhe reafirmar a liderança atual ou iniciar uma eleição.
                next_action = self._become_leader if self.is_leader else self.start_election
                # Prepara uma thread para executar a função indicada.
                threading.Thread(target=next_action, daemon=True).start()
            # Executa este ramo quando message_type == "COORDINATOR" for verdadeiro.
            elif message_type == "COORDINATOR":
                # Converte o ID do coordenador anunciado em número inteiro.
                proposed_leader = int(message["leader_id"])
                # Executa este ramo quando proposed_leader < self.worker_id for verdadeiro.
                if proposed_leader < self.worker_id:
                    # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                    send_json(client, {"type": "REJECTED", "worker_id": self.worker_id})
                    # Prepara uma thread para executar a função indicada.
                    threading.Thread(target=self.start_election, daemon=True).start()
                # Executa o caso alternativo quando a condição anterior não foi satisfeita.
                else:
                    # Executa self._set_leader(proposed_leader) para continuar a operação desta função.
                    self._set_leader(proposed_leader)
                    # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                    send_json(client, {"type": "ACK"})
            # Executa o caso alternativo quando a condição anterior não foi satisfeita.
            else:
                # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                send_json(client, {"type": "ERROR", "explanation": "Tipo desconhecido."})
        # Trata (ConnectionError, OSError, ValueError, KeyError) as error produzida no bloco protegido.
        except (ConnectionError, OSError, ValueError, KeyError) as error:
            # Exibe informações no terminal para acompanhar a execução.
            print(f"[ELEICAO] Mensagem de coordenacao invalida: {error}", flush=True)
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            client.close()

    # Define _request; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _request(self, peer_id: int, message: dict[str, Any]) -> dict[str, Any] | None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Envia uma mensagem curta a outro worker e trata falha parcial."""

        # Obtém o host e a porta do worker selecionado para a comunicação.
        peer = self.peers[peer_id]
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Abre um contexto que organiza o uso e a liberação do recurso indicado.
            with socket.create_connection((peer.host, peer.port), timeout=1.0) as connection:
                # Define o limite de espera das operações do socket em segundos.
                connection.settimeout(1.0)
                # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
                send_json(connection, message)
                # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
                return receive_json(connection)
        # Trata (ConnectionError, OSError, TimeoutError) produzida no bloco protegido.
        except (ConnectionError, OSError, TimeoutError):
            # Devolve None ao código que chamou a função.
            return None

    # Define _heartbeat_loop; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _heartbeat_loop(self) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Detecta a queda do lider apos falhas consecutivas e dispara nova eleicao."""

        # Zera o contador de falhas consecutivas do heartbeat.
        failures = 0
        # Repete o bloco enquanto not self._stop_event.wait(self.heartbeat_interval) for verdadeiro.
        while not self._stop_event.wait(self.heartbeat_interval):
            # Consulta quem é o líder atualmente reconhecido pelo algoritmo local.
            leader_id = self.leader_id
            # Executa este ramo quando leader_id is None for verdadeiro.
            if leader_id is None:
                # Prepara uma thread para executar a função indicada.
                threading.Thread(target=self.start_election, daemon=True).start()
                # Pula o restante desta iteração e volta à próxima passagem do laço.
                continue
            # Executa este ramo quando leader_id == self.worker_id for verdadeiro.
            if leader_id == self.worker_id:
                # Zera o contador de falhas consecutivas do heartbeat.
                failures = 0
                # Pula o restante desta iteração e volta à próxima passagem do laço.
                continue

            # Calcula a expressão à direita e guarda o resultado em response.
            response = self._request(leader_id, {"type": "PING", "from": self.worker_id})
            # Executa este ramo quando response and response.get("type") == "PONG" for verdadeiro.
            if response and response.get("type") == "PONG":
                # Zera o contador de falhas consecutivas do heartbeat.
                failures = 0
                # Pula o restante desta iteração e volta à próxima passagem do laço.
                continue

            # Acrescenta o valor indicado ao contador failures.
            failures += 1
            # Exibe informações no terminal para acompanhar a execução.
            print(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"[HEARTBEAT] Worker {self.worker_id}: falha {failures}/{self.heartbeat_failures} "
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"ao contatar lider {leader_id}.",
                # Fornece o argumento nomeado flush à chamada em andamento.
                flush=True,
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
            # Executa este ramo quando failures >= self.heartbeat_failures for verdadeiro.
            if failures >= self.heartbeat_failures:
                # Zera o contador de falhas consecutivas do heartbeat.
                failures = 0
                # Prepara uma thread para executar a função indicada.
                threading.Thread(target=self.start_election, daemon=True).start()
