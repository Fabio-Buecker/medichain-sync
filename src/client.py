# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Cliente TCP simples usado por uma clinica para enviar uma atualizacao."""

# Importa argparse para disponibilizar suas funções neste módulo.
import argparse
# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa socket para disponibilizar suas funções neste módulo.
import socket
# Importa Any de typing.
from typing import Any

# Importa receive_json, send_json de src.protocol.
from src.protocol import receive_json, send_json


# Define normalize_copied_text; os parâmetros e tipos descrevem suas entradas e seu retorno.
def normalize_copied_text(value: str) -> str:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Remove a barra que alguns editores inserem antes do sublinhado."""

    # Devolve value.replace("\\_", "_") ao código que chamou a função.
    return value.replace("\\_", "_")


# Define send_update; os parâmetros e tipos descrevem suas entradas e seu retorno.
def send_update(host: str, port: int, update: dict[str, Any]) -> dict[str, Any]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Conecta ao gateway, envia uma mensagem enquadrada e le a resposta."""

    # Abre um contexto que organiza o uso e a liberação do recurso indicado.
    with socket.create_connection((host, port), timeout=5.0) as connection:
        # Define o limite de espera das operações do socket em segundos.
        connection.settimeout(10.0)
        # Envia uma mensagem JSON com cabeçalho de tamanho pelo socket.
        send_json(connection, update)
        # Recebe o cabeçalho de tamanho e reconstrói a mensagem JSON.
        return receive_json(connection)


# Define parse_clock; os parâmetros e tipos descrevem suas entradas e seu retorno.
def parse_clock(raw_clock: str) -> dict[str, int]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Transforma o texto JSON do argumento em um relogio vetorial."""

    # Remove barras copiadas antes de sublinhados antes de interpretar o JSON.
    normalized_clock = normalize_copied_text(raw_clock)
    # Converte o JSON recebido em estruturas de dados Python.
    clock = json.loads(normalized_clock)
    # Executa este ramo quando not isinstance(clock, dict) for verdadeiro.
    if not isinstance(clock, dict):
        # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
        raise ValueError("O relogio deve ser um objeto JSON.")
    # Devolve {str(node): int(counter) for node, counter in clock.items()} ao código que chamou a função.
    return {str(node): int(counter) for node, counter in clock.items()}


# Define main; os parâmetros e tipos descrevem suas entradas e seu retorno.
def main() -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le os argumentos didaticos e monta a atualizacao de prontuario."""

    # Cria o leitor dos argumentos de linha de comando do cliente.
    parser = argparse.ArgumentParser(description="Cliente do MediChain Sync")
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--host", default="127.0.0.1")
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--port", type=int, default=15000)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--clinic", required=True)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--patient", required=True)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--professional", required=True)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--field", required=True)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--value", required=True)
    # Define uma opção aceita na linha de comando.
    parser.add_argument("--clock", required=True, help='Exemplo: {"clinica_a": 1}')
    # Lê e valida as opções digitadas no terminal.
    arguments = parser.parse_args()

    # Calcula a expressão à direita e guarda o resultado em update.
    update = {
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "clinic_id": normalize_copied_text(arguments.clinic),
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "patient_id": normalize_copied_text(arguments.patient),
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "professional": arguments.professional,
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "field_name": arguments.field,
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "field_value": arguments.value,
        # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
        "clinical_clock": parse_clock(arguments.clock),
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    }
    # Envia a atualização ao gateway e aguarda a resposta de recebimento.
    response = send_update(arguments.host, arguments.port, update)
    # Serializa os dados em texto JSON.
    print(json.dumps(response, ensure_ascii=False, indent=2))


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa main() para continuar a operação desta função.
    main()
