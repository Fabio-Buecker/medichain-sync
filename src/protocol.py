# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Protocolo TCP com framing: 4 bytes de tamanho seguidos por um JSON."""

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa struct para disponibilizar suas funções neste módulo.
import struct
# Importa Any de typing.
from typing import Any


# Reserva quatro bytes para o tamanho da mensagem no cabeçalho TCP.
HEADER_SIZE = 4
# Limita cada mensagem a um milhão de bytes para evitar alocações excessivas.
MAX_MESSAGE_SIZE = 1_000_000


# Define _receive_exactly; os parâmetros e tipos descrevem suas entradas e seu retorno.
def _receive_exactly(connection: socket.socket, size: int) -> bytes:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le exatamente a quantidade pedida, mesmo que o TCP fragmente os bytes."""

    # Cria um buffer mutável para acumular fragmentos recebidos do TCP.
    received = bytearray()
    # Repete o bloco enquanto len(received) < size for verdadeiro.
    while len(received) < size:
        # Recebe até a quantidade solicitada de bytes do fluxo TCP.
        part = connection.recv(size - len(received))
        # Executa este ramo quando not part for verdadeiro.
        if not part:
            # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
            raise ConnectionError("A conexao terminou antes da mensagem completa.")
        # Acrescenta o fragmento recebido ao buffer de bytes.
        received.extend(part)
    # Converte o buffer acumulado em uma sequência imutável de bytes.
    return bytes(received)


# Define send_json; os parâmetros e tipos descrevem suas entradas e seu retorno.
def send_json(connection: socket.socket, message: dict[str, Any]) -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Serializa o dicionario, envia o tamanho e depois envia o conteudo."""

    # Serializa os dados em texto JSON.
    body = json.dumps(message, ensure_ascii=False).encode("utf-8")
    # Executa este ramo quando len(body) > MAX_MESSAGE_SIZE for verdadeiro.
    if len(body) > MAX_MESSAGE_SIZE:
        # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
        raise ValueError("Mensagem maior que o limite de 1 MB.")
    # Codifica o tamanho do JSON em quatro bytes, inteiro sem sinal e ordem de rede.
    header = struct.pack("!I", len(body))
    # Envia todos os bytes, inclusive quando são necessárias várias escritas.
    connection.sendall(header + body)


# Define receive_json; os parâmetros e tipos descrevem suas entradas e seu retorno.
def receive_json(connection: socket.socket) -> dict[str, Any]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le o cabecalho de tamanho e reconstrui um unico objeto JSON."""

    # Recebe exatamente os quatro bytes que indicam o tamanho da mensagem.
    header = _receive_exactly(connection, HEADER_SIZE)
    # Decodifica o inteiro de quatro bytes do cabeçalho para saber quantos bytes faltam ler.
    body_size = struct.unpack("!I", header)[0]
    # Executa este ramo quando body_size > MAX_MESSAGE_SIZE for verdadeiro.
    if body_size > MAX_MESSAGE_SIZE:
        # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
        raise ValueError("Mensagem maior que o limite de 1 MB.")
    # Recebe exatamente a quantidade de bytes declarada no cabeçalho.
    body = _receive_exactly(connection, body_size)
    # Converte o JSON recebido em estruturas de dados Python.
    decoded = json.loads(body.decode("utf-8"))
    # Executa este ramo quando not isinstance(decoded, dict) for verdadeiro.
    if not isinstance(decoded, dict):
        # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
        raise ValueError("A raiz da mensagem deve ser um objeto JSON.")
    # Devolve decoded ao código que chamou a função.
    return decoded
