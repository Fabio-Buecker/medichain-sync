# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Testa consolidacao causal, conflitos, idempotencia e replicacao."""

# Importa Path de pathlib.
from pathlib import Path
# Importa tempfile para disponibilizar suas funções neste módulo.
import tempfile
# Importa unittest para disponibilizar suas funções neste módulo.
import unittest

# Importa MedicalRecordUpdate de src.models.
from src.models import MedicalRecordUpdate
# Importa ReplicatedStorage de src.storage.
from src.storage import ReplicatedStorage


# Define make_update; os parâmetros e tipos descrevem suas entradas e seu retorno.
def make_update(event_id: str, value: str, clock: dict[str, int]) -> MedicalRecordUpdate:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Cria uma atualizacao minima reutilizada nos cenarios de teste."""

    # Devolve MedicalRecordUpdate( ao código que chamou a função.
    return MedicalRecordUpdate(
        # Fornece o argumento nomeado event_id à chamada em andamento.
        event_id=event_id,
        # Fornece o argumento nomeado correlation_id à chamada em andamento.
        correlation_id="test-correlation",
        # Fornece o argumento nomeado clinic_id à chamada em andamento.
        clinic_id="test-clinic",
        # Fornece o argumento nomeado patient_id à chamada em andamento.
        patient_id="patient-1",
        # Fornece o argumento nomeado professional à chamada em andamento.
        professional="Test Doctor",
        # Fornece o argumento nomeado field_name à chamada em andamento.
        field_name="allergy",
        # Fornece o argumento nomeado field_value à chamada em andamento.
        field_value=value,
        # Fornece o argumento nomeado clinical_clock à chamada em andamento.
        clinical_clock=clock,
        # Fornece o argumento nomeado processing_clock à chamada em andamento.
        processing_clock={"worker_1": 1},
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    )


# Define a classe StorageTest, que agrupa os dados e comportamentos abaixo.
class StorageTest(unittest.TestCase):
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Cria bancos temporarios para nao alterar dados reais da demonstracao."""

    # Define test_replication_conflict_and_causal_resolution; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_replication_conflict_and_causal_resolution(self) -> None:
        # Abre um contexto que organiza o uso e a liberação do recurso indicado.
        with tempfile.TemporaryDirectory() as directory:
            # Calcula a expressão à direita e guarda o resultado em storage.
            storage = ReplicatedStorage(directory)
            # Calcula a expressão à direita e guarda o resultado em first.
            first = make_update("event-a", "Penicillin", {"clinic_a": 1, "clinic_b": 0})
            # Calcula a expressão à direita e guarda o resultado em concurrent.
            concurrent = make_update("event-b", "No allergy", {"clinic_a": 0, "clinic_b": 1})
            # Calcula a expressão à direita e guarda o resultado em resolved.
            resolved = make_update("event-c", "Penicillin confirmed", {"clinic_a": 2, "clinic_b": 1})

            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual(
                # Fornece ("after", "first_update_applied") à declaração ou chamada iniciada acima.
                ("after", "first_update_applied"),
                # Fornece storage.consolidate(first, worker_id=1, leader_id=3) à declaração ou chamada iniciada acima.
                storage.consolidate(first, worker_id=1, leader_id=3),
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )
            # Calcula a expressão à direita e guarda o resultado em relation, decision.
            relation, decision = storage.consolidate(concurrent, worker_id=2, leader_id=3)
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual("concurrent", relation)
            # Verifica se a condição do teste é verdadeira.
            self.assertTrue(decision.startswith("conflict_"))
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual(
                # Fornece ("after", "causal_update_applied") à declaração ou chamada iniciada acima.
                ("after", "causal_update_applied"),
                # Fornece storage.consolidate(resolved, worker_id=3, leader_id=3) à declaração ou chamada iniciada acima.
                storage.consolidate(resolved, worker_id=3, leader_id=3),
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )

            # Calcula a expressão à direita e guarda o resultado em primary.
            primary = storage.read_patient("patient-1")
            # Calcula a expressão à direita e guarda o resultado em replica.
            replica = storage.read_patient("patient-1", replica=True)
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual(primary, replica)
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual("Penicillin confirmed", primary["data"]["allergy"])

    # Define test_duplicate_event_is_ignored; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_duplicate_event_is_ignored(self) -> None:
        # Abre um contexto que organiza o uso e a liberação do recurso indicado.
        with tempfile.TemporaryDirectory() as directory:
            # Calcula a expressão à direita e guarda o resultado em storage.
            storage = ReplicatedStorage(directory)
            # Calcula a expressão à direita e guarda o resultado em update.
            update = make_update("same-event", "Value", {"clinic_a": 1})
            # Executa storage.consolidate(update, worker_id=1, leader_id=3) para continuar a operação desta função.
            storage.consolidate(update, worker_id=1, leader_id=3)
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual(
                # Fornece ("equal", "duplicate_ignored") à declaração ou chamada iniciada acima.
                ("equal", "duplicate_ignored"),
                # Fornece storage.consolidate(update, worker_id=1, leader_id=3) à declaração ou chamada iniciada acima.
                storage.consolidate(update, worker_id=1, leader_id=3),
            # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
            )


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa os testes definidos neste arquivo.
    unittest.main()
