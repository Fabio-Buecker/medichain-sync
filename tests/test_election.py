# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Testa a regra central que impede um ID menor de vencer o Bully."""

# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa unittest para disponibilizar suas funções neste módulo.
import unittest

# Importa Peer de src.config.
from src.config import Peer
# Importa BullyElection de src.election.
from src.election import BullyElection
# Importa receive_json, send_json de src.protocol.
from src.protocol import receive_json, send_json


# Define a classe ElectionTest, que agrupa os dados e comportamentos abaixo.
class ElectionTest(unittest.TestCase):
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Valida mensagens de coordenador sem abrir portas ou iniciar heartbeats."""

    # Define setUp; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def setUp(self) -> None:
        # Calcula a expressão à direita e guarda o resultado em peers.
        peers = {
            # Declara 1: Peer(1, "127.0.0.1", 6001) como campo tipado ou parâmetro da estrutura em definição.
            1: Peer(1, "127.0.0.1", 6001),
            # Declara 2: Peer(2, "127.0.0.1", 6002) como campo tipado ou parâmetro da estrutura em definição.
            2: Peer(2, "127.0.0.1", 6002),
            # Declara 3: Peer(3, "127.0.0.1", 6003) como campo tipado ou parâmetro da estrutura em definição.
            3: Peer(3, "127.0.0.1", 6003),
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        }
        # Calcula a expressão à direita e guarda o resultado em self.election.
        self.election = BullyElection(worker_id=2, peers=peers)
        # Calcula a expressão à direita e guarda o resultado em self.election.start_election.
        self.election.start_election = lambda: None  # type: ignore[method-assign]

    # Define test_rejects_smaller_coordinator; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_rejects_smaller_coordinator(self) -> None:
        # Cria dois sockets conectados para testar a troca de bytes.
        sender, receiver = socket.socketpair()
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(sender, {"type": "COORDINATOR", "leader_id": 1})
            # Executa self.election._handle_peer(receiver) para continuar a operação desta função.
            self.election._handle_peer(receiver)
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            self.assertEqual("REJECTED", receive_json(sender)["type"])
            # Verifica se o resultado é None.
            self.assertIsNone(self.election.leader_id)
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            sender.close()

    # Define test_accepts_larger_coordinator; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_accepts_larger_coordinator(self) -> None:
        # Cria dois sockets conectados para testar a troca de bytes.
        sender, receiver = socket.socketpair()
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(sender, {"type": "COORDINATOR", "leader_id": 3})
            # Executa self.election._handle_peer(receiver) para continuar a operação desta função.
            self.election._handle_peer(receiver)
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            self.assertEqual("ACK", receive_json(sender)["type"])
            # Verifica se o resultado obtido é igual ao esperado.
            self.assertEqual(3, self.election.leader_id)
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            sender.close()


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa os testes definidos neste arquivo.
    unittest.main()
