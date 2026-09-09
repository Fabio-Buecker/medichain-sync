# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Envia tres eventos que demonstram conflito e resolucao causal."""

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa os para disponibilizar suas funções neste módulo.
import os
# Importa time para disponibilizar suas funções neste módulo.
import time

# Importa send_update de src.client.
from src.client import send_update


# Define main; os parâmetros e tipos descrevem suas entradas e seu retorno.
def main() -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Executa um roteiro deterministico para a apresentacao do grupo."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    gateway_host = os.getenv("GATEWAY_HOST", "127.0.0.1")
    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    gateway_port = int(os.getenv("GATEWAY_HOST_PORT", "15000"))

    # Monta os três eventos fictícios usados na demonstração de conflito e resolução.
    events = [
        # Fornece { à declaração ou chamada iniciada acima.
        {
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "event_id": "evento-clinica-a-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "correlation_id": "demo-paciente-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinic_id": "clinica_a",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "patient_id": "paciente_001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "professional": "Dra. Ana",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_name": "alergia",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_value": "Penicilina",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinical_clock": {"clinica_a": 1, "clinica_b": 0},
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        },
        # Fornece { à declaração ou chamada iniciada acima.
        {
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "event_id": "evento-clinica-b-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "correlation_id": "demo-paciente-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinic_id": "clinica_b",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "patient_id": "paciente_001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "professional": "Dr. Bruno",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_name": "alergia",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_value": "Sem alergias conhecidas",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinical_clock": {"clinica_a": 0, "clinica_b": 1},
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        },
        # Fornece { à declaração ou chamada iniciada acima.
        {
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "event_id": "evento-clinica-a-002",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "correlation_id": "demo-paciente-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "parent_event_id": "evento-clinica-b-001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinic_id": "clinica_a",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "patient_id": "paciente_001",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "professional": "Dra. Ana",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_name": "alergia",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "field_value": "Penicilina - confirmado apos revisao",
            # Define este campo da mensagem com o valor indicado à direita dos dois-pontos.
            "clinical_clock": {"clinica_a": 2, "clinica_b": 1},
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        },
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    ]

    # Repete o bloco para cada event encontrado em events.
    for event in events:
        # Envia a atualização ao gateway e aguarda a resposta de recebimento.
        response = send_update(gateway_host, gateway_port, event)
        # Serializa os dados em texto JSON.
        print(json.dumps(response, ensure_ascii=False))
        # Pausa esta thread pelo intervalo informado.
        time.sleep(0.5)

    # Exibe informações no terminal para acompanhar a execução.
    print("Demo enviada. Aguarde a fila e consulte os logs dos workers.")


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa main() para continuar a operação desta função.
    main()
