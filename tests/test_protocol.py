# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Testa se o framing separa corretamente mensagens enviadas pelo TCP."""

# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa unittest para disponibilizar suas funções neste módulo.
import unittest

# Importa receive_json, send_json de src.protocol.
from src.protocol import receive_json, send_json


# Define a classe ProtocolTest, que agrupa os dados e comportamentos abaixo.
class ProtocolTest(unittest.TestCase):
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Usa socketpair para testar localmente sem abrir uma porta real."""

    # Define test_round_trip; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_round_trip(self) -> None:
        # Cria dois sockets conectados para testar a troca de bytes.
        sender, receiver = socket.socketpair()
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Calcula a expressão à direita e guarda o resultado em expected.
            expected = {"patient_id": "paciente_001", "value": "acao"}
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(sender, expected)
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            self.assertEqual(expected, receive_json(receiver))
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            sender.close()
            # Fecha o recurso e libera a conexão ou socket.
            receiver.close()

    # Define test_two_messages_do_not_mix; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_two_messages_do_not_mix(self) -> None:
        # Cria dois sockets conectados para testar a troca de bytes.
        sender, receiver = socket.socketpair()
        # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
        try:
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(sender, {"number": 1})
            # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
            send_json(sender, {"number": 2})
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            self.assertEqual({"number": 1}, receive_json(receiver))
            # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
            self.assertEqual({"number": 2}, receive_json(receiver))
        # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
        finally:
            # Fecha o recurso e libera a conexão ou socket.
            sender.close()
            # Fecha o recurso e libera a conexão ou socket.
            receiver.close()


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa os testes definidos neste arquivo.
    unittest.main()
