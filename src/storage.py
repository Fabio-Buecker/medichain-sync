# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Persistencia consolidada e replicada em dois arquivos SQLite."""

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa Path de pathlib.
from pathlib import Path
# Importa sqlite3 para disponibilizar suas funções neste módulo.
import sqlite3
# Importa threading para disponibilizar suas funções neste módulo.
import threading
# Importa Any de typing.
from typing import Any

# Importa MedicalRecordUpdate de src.models.
from src.models import MedicalRecordUpdate
# Importa compare_clocks, deterministic_key de src.vector_clock.
from src.vector_clock import compare_clocks, deterministic_key


# Localiza database/schema.sql a partir da pasta deste arquivo, independentemente do terminal.
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "database" / "schema.sql"
# Lê o script SQL em UTF-8 para criar as tabelas dos dois bancos.
SCHEMA = SCHEMA_PATH.read_text(encoding="utf-8")


# Define a classe ReplicatedStorage, que agrupa os dados e comportamentos abaixo.
class ReplicatedStorage:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Mantem um banco principal e uma replica com o mesmo conteudo."""

    # Define __init__; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def __init__(self, data_directory: str) -> None:
        # Converte a pasta de dados em um objeto Path para compor caminhos.
        self._data_directory = Path(data_directory)
        # Cria a pasta de dados caso ainda não exista.
        self._data_directory.mkdir(parents=True, exist_ok=True)
        # Monta o caminho do arquivo SQLite principal.
        self.primary_path = self._data_directory / "medichain-primary.db"
        # Monta o caminho do segundo arquivo SQLite usado como cópia.
        self.replica_path = self._data_directory / "medichain-replica.db"
        # Cria uma trava para proteger dados compartilhados entre threads.
        self._write_lock = threading.Lock()
        # Executa self._initialize_file(self.primary_path) para continuar a operação desta função.
        self._initialize_file(self.primary_path)
        # Executa self._initialize_file(self.replica_path) para continuar a operação desta função.
        self._initialize_file(self.replica_path)

    # Define um método estático que não recebe self nem cls implicitamente.
    @staticmethod
    # Define _initialize_file; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _initialize_file(path: Path) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Cria as tabelas no arquivo informado caso ainda nao existam."""

        # Abre uma conexão com o arquivo SQLite.
        connection = sqlite3.connect(path)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Executa o script SQL de criação das tabelas.
            connection.executescript(SCHEMA)
            # Confirma as alterações da transação no banco.
            connection.commit()
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            connection.close()

    # Define um método estático que não recebe self nem cls implicitamente.
    @staticmethod
    # Define _json; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _json(value: object) -> str:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Gera JSON ordenado para facilitar comparacao, testes e explicacao."""

        # Serializa os dados em texto JSON.
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    # Define consolidate; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def consolidate(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara update: MedicalRecordUpdate como campo tipado ou parâmetro da estrutura em definição.
        update: MedicalRecordUpdate,
        # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
        worker_id: int,
        # Declara leader_id: int como campo tipado ou parâmetro da estrutura em definição.
        leader_id: int,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> tuple[str, str]:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Compara relogios, decide o estado e grava principal e replica juntos."""

        # Mantém a trava adquirida durante este bloco e a libera automaticamente ao sair.
        with self._write_lock:
            # Devolve self._consolidate_while_locked(update, worker_id, leader_id) ao código que chamou a função.
            return self._consolidate_while_locked(update, worker_id, leader_id)

    # Define _consolidate_while_locked; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _consolidate_while_locked(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara update: MedicalRecordUpdate como campo tipado ou parâmetro da estrutura em definição.
        update: MedicalRecordUpdate,
        # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
        worker_id: int,
        # Declara leader_id: int como campo tipado ou parâmetro da estrutura em definição.
        leader_id: int,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> tuple[str, str]:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Executa a secao critica protegida pelo Lock contra race condition local."""

        # Abre uma conexão com o arquivo SQLite.
        connection = sqlite3.connect(self.primary_path, timeout=10)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Anexa o arquivo réplica à conexão principal para escrever em ambos na transação.
            connection.execute("ATTACH DATABASE ? AS replica", (str(self.replica_path),))
            # Inicia uma transação SQLite e solicita imediatamente a trava de escrita.
            connection.execute("BEGIN IMMEDIATE")

            # Executa a instrução SQL com os parâmetros fornecidos.
            duplicate = connection.execute(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                "SELECT decision FROM main.audit_log WHERE event_id = ?",
                # Fornece (update.event_id,) à declaração ou chamada iniciada acima.
                (update.event_id,),
            # Obtém a primeira linha do resultado SQL, ou None.
            ).fetchone()
            # Executa este ramo quando duplicate for verdadeiro.
            if duplicate:
                # Confirma as alterações da transação no banco.
                connection.commit()
                # Devolve "equal", "duplicate_ignored" ao código que chamou a função.
                return "equal", "duplicate_ignored"

            # Executa a instrução SQL com os parâmetros fornecidos.
            current = connection.execute(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                "SELECT data_json, clinical_clock_json, last_event_id "
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                "FROM main.record_state WHERE patient_id = ?",
                # Fornece (update.patient_id,) à declaração ou chamada iniciada acima.
                (update.patient_id,),
            # Obtém a primeira linha do resultado SQL, ou None.
            ).fetchone()

            # Recebe a relação causal, a decisão, o estado escolhido e o evento anterior.
            relation, decision, next_data, current_event_id = self._decide(update, current)
            # Inicia a chamada de self._write_both_copies com os argumentos das linhas seguintes.
            self._write_both_copies(
                # Fornece connection à declaração ou chamada iniciada acima.
                connection,
                # Fornece update à declaração ou chamada iniciada acima.
                update,
                # Fornece worker_id à declaração ou chamada iniciada acima.
                worker_id,
                # Fornece leader_id à declaração ou chamada iniciada acima.
                leader_id,
                # Fornece relation à declaração ou chamada iniciada acima.
                relation,
                # Fornece decision à declaração ou chamada iniciada acima.
                decision,
                # Fornece next_data à declaração ou chamada iniciada acima.
                next_data,
                # Fornece current_event_id à declaração ou chamada iniciada acima.
                current_event_id,
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
            # Confirma as alterações da transação no banco.
            connection.commit()
            # Devolve relation, decision ao código que chamou a função.
            return relation, decision
        # Trata Exception produzida no bloco protegido.
        except Exception:
            # Desfaz alterações ainda não confirmadas da transação.
            connection.rollback()
            # Propaga novamente a exceção atual depois de desfazer a transação.
            raise
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
            try:
                # Executa a instrução SQL com os parâmetros fornecidos.
                connection.execute("DETACH DATABASE replica")
            # Trata sqlite3.Error produzida no bloco protegido.
            except sqlite3.Error:
                # Não executa outra ação neste tratamento; o fluxo segue para a limpeza.
                pass
            # Fecha o recurso e libera a conexão ou socket.
            connection.close()

    # Define _decide; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _decide(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara update: MedicalRecordUpdate como campo tipado ou parâmetro da estrutura em definição.
        update: MedicalRecordUpdate,
        # Declara current: tuple[str, str, str] | None como campo tipado ou parâmetro da estrutura em definição.
        current: tuple[str, str, str] | None,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> tuple[str, str, dict[str, Any], str]:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Aplica a regra causal e um desempate deterministico para concorrencia."""

        # Executa este ramo quando current is None for verdadeiro.
        if current is None:
            # Devolve "after", "first_update_applied", {update.field_name: update.field_value}, "" ao código que chamou a função.
            return "after", "first_update_applied", {update.field_name: update.field_value}, ""

        # Separa os campos consultados no banco: dados, vetor e último evento.
        data_json, clock_json, current_event_id = current
        # Converte o JSON recebido em estruturas de dados Python.
        current_data: dict[str, Any] = json.loads(data_json)
        # Converte o JSON recebido em estruturas de dados Python.
        current_clock: dict[str, int] = json.loads(clock_json)
        # Compara os vetores para identificar anterioridade, igualdade ou concorrência.
        relation = compare_clocks(update.clinical_clock, current_clock)

        # Executa este ramo quando relation == "after" for verdadeiro.
        if relation == "after":
            # Copia os campos do prontuário atual antes de aplicar o novo valor.
            updated_data = dict(current_data)
            # Atualiza apenas o campo indicado no evento recebido.
            updated_data[update.field_name] = update.field_value
            # Devolve relation, "causal_update_applied", updated_data, current_event_id ao código que chamou a função.
            return relation, "causal_update_applied", updated_data, current_event_id

        # Executa este ramo quando relation == "before" for verdadeiro.
        if relation == "before":
            # Devolve relation, "obsolete_update_kept_only_in_audit", current_data, current_event_id ao código que chamou a função.
            return relation, "obsolete_update_kept_only_in_audit", current_data, current_event_id

        # Calcula a chave de desempate estável do evento.
        incoming_key = deterministic_key(update.clinical_clock, update.event_id)
        # Calcula a chave de desempate estável do evento.
        current_key = deterministic_key(current_clock, current_event_id)
        # Executa este ramo quando incoming_key > current_key for verdadeiro.
        if incoming_key > current_key:
            # Copia os campos do prontuário atual antes de aplicar o novo valor.
            updated_data = dict(current_data)
            # Atualiza apenas o campo indicado no evento recebido.
            updated_data[update.field_name] = update.field_value
            # Devolve relation, "conflict_incoming_won", updated_data, current_event_id ao código que chamou a função.
            return relation, "conflict_incoming_won", updated_data, current_event_id
        # Devolve relation, "conflict_existing_won", current_data, current_event_id ao código que chamou a função.
        return relation, "conflict_existing_won", current_data, current_event_id

    # Define _write_both_copies; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def _write_both_copies(
        # Recebe a própria instância; permite acessar os atributos deste objeto.
        self,
        # Declara connection: sqlite3.Connection como campo tipado ou parâmetro da estrutura em definição.
        connection: sqlite3.Connection,
        # Declara update: MedicalRecordUpdate como campo tipado ou parâmetro da estrutura em definição.
        update: MedicalRecordUpdate,
        # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
        worker_id: int,
        # Declara leader_id: int como campo tipado ou parâmetro da estrutura em definição.
        leader_id: int,
        # Declara relation: str como campo tipado ou parâmetro da estrutura em definição.
        relation: str,
        # Declara decision: str como campo tipado ou parâmetro da estrutura em definição.
        decision: str,
        # Declara next_data: dict[str, Any] como campo tipado ou parâmetro da estrutura em definição.
        next_data: dict[str, Any],
        # Declara existing_event_id: str como campo tipado ou parâmetro da estrutura em definição.
        existing_event_id: str,
    # Fecha os parâmetros e informa o tipo de retorno da função.
    ) -> None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Repete as mesmas escritas nos esquemas main e replica da transacao."""

        # Identifica as decisões que permitem gravar uma nova visão consolidada do prontuário.
        changes_state = decision in {"first_update_applied", "causal_update_applied", "conflict_incoming_won"}
        # Repete o bloco para cada schema encontrado em ("main", "replica").
        for schema in ("main", "replica"):
            # Executa este ramo quando changes_state for verdadeiro.
            if changes_state:
                # Executa a instrução SQL com os parâmetros fornecidos.
                connection.execute(
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    f"INSERT INTO {schema}.record_state "
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    "(patient_id, data_json, clinical_clock_json, last_event_id) VALUES (?, ?, ?, ?) "
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    "ON CONFLICT(patient_id) DO UPDATE SET "
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    "data_json=excluded.data_json, "
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    "clinical_clock_json=excluded.clinical_clock_json, "
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    "last_event_id=excluded.last_event_id",
                    # Inicia a chamada de  com os argumentos das linhas seguintes.
                    (
                        # Fornece update.patient_id à declaração ou chamada iniciada acima.
                        update.patient_id,
                        # Fornece self._json(next_data) à declaração ou chamada iniciada acima.
                        self._json(next_data),
                        # Fornece self._json(update.clinical_clock) à declaração ou chamada iniciada acima.
                        self._json(update.clinical_clock),
                        # Fornece update.event_id à declaração ou chamada iniciada acima.
                        update.event_id,
                    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
                    ),
                # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
                )

            # Executa a instrução SQL com os parâmetros fornecidos.
            connection.execute(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                f"INSERT INTO {schema}.audit_log VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                # Inicia a chamada de  com os argumentos das linhas seguintes.
                (
                    # Fornece update.event_id à declaração ou chamada iniciada acima.
                    update.event_id,
                    # Fornece update.patient_id à declaração ou chamada iniciada acima.
                    update.patient_id,
                    # Fornece worker_id à declaração ou chamada iniciada acima.
                    worker_id,
                    # Fornece leader_id à declaração ou chamada iniciada acima.
                    leader_id,
                    # Fornece relation à declaração ou chamada iniciada acima.
                    relation,
                    # Fornece decision à declaração ou chamada iniciada acima.
                    decision,
                    # Fornece self._json(update.clinical_clock) à declaração ou chamada iniciada acima.
                    self._json(update.clinical_clock),
                    # Fornece self._json(update.processing_clock) à declaração ou chamada iniciada acima.
                    self._json(update.processing_clock),
                # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
                ),
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )

            # Executa este ramo quando relation in {"concurrent", "equal"} for verdadeiro.
            if relation in {"concurrent", "equal"}:
                # Executa a instrução SQL com os parâmetros fornecidos.
                connection.execute(
                    # Fornece esta parte do texto ou argumento à operação iniciada acima.
                    f"INSERT INTO {schema}.conflicts VALUES (?, ?, ?, ?, ?)",
                    # Inicia a chamada de  com os argumentos das linhas seguintes.
                    (
                        # Fornece update.event_id à declaração ou chamada iniciada acima.
                        update.event_id,
                        # Fornece update.patient_id à declaração ou chamada iniciada acima.
                        update.patient_id,
                        # Fornece existing_event_id à declaração ou chamada iniciada acima.
                        existing_event_id,
                        # Fornece update.field_value à declaração ou chamada iniciada acima.
                        update.field_value,
                        # Fornece decision à declaração ou chamada iniciada acima.
                        decision,
                    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
                    ),
                # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
                )

    # Define read_patient; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def read_patient(self, patient_id: str, replica: bool = False) -> dict[str, Any] | None:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Le o estado atual do principal ou da replica para testes e demonstracao."""

        # Calcula a expressão à direita e guarda o resultado em path.
        path = self.replica_path if replica else self.primary_path
        # Abre uma conexão com o arquivo SQLite.
        connection = sqlite3.connect(path)
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Executa a instrução SQL com os parâmetros fornecidos.
            row = connection.execute(
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                "SELECT data_json, clinical_clock_json, last_event_id "
                # Fornece esta parte do texto ou argumento à operação iniciada acima.
                "FROM record_state WHERE patient_id = ?",
                # Fornece (patient_id,) à declaração ou chamada iniciada acima.
                (patient_id,),
            # Obtém a primeira linha do resultado SQL, ou None.
            ).fetchone()
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            connection.close()
        # Executa este ramo quando row is None for verdadeiro.
        if row is None:
            # Devolve None ao código que chamou a função.
            return None
        # Devolve { ao código que chamou a função.
        return {
            # Converte o JSON recebido em estruturas de dados Python.
            "data": json.loads(row[0]),
            # Converte o JSON recebido em estruturas de dados Python.
            "clinical_clock": json.loads(row[1]),
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "last_event_id": row[2],
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        }
