# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Entidades do dominio e validacao das mensagens trocadas pelo sistema."""

# Importa asdict, dataclass, field de dataclasses.
from dataclasses import asdict, dataclass, field
# Importa datetime, timezone de datetime.
from datetime import datetime, timezone
# Importa Any de typing.
from typing import Any
# Importa uuid4 de uuid.
from uuid import uuid4


# Define utc_now_text; os parâmetros e tipos descrevem suas entradas e seu retorno.
def utc_now_text() -> str:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Gera um horario apenas para observacao humana, nunca para causalidade."""

    # Devolve datetime.now(timezone.utc).isoformat() ao código que chamou a função.
    return datetime.now(timezone.utc).isoformat()


# Define validate_clock; os parâmetros e tipos descrevem suas entradas e seu retorno.
def validate_clock(value: object, field_name: str) -> dict[str, int]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Confirma que um relogio e um mapa de nomes para inteiros nao negativos."""

    # Executa este ramo quando not isinstance(value, dict) for verdadeiro.
    if not isinstance(value, dict):
        # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
        raise ValueError(f"{field_name} deve ser um objeto JSON.")
    # Calcula a expressão à direita e guarda o resultado em clock: dict[str, int].
    clock: dict[str, int] = {}
    # Repete o bloco para cada node, counter encontrado em value.items().
    for node, counter in value.items():
        # Executa este ramo quando not isinstance(node, str) or not isinstance(counter, int) or counter < 0 for verdadeiro.
        if not isinstance(node, str) or not isinstance(counter, int) or counter < 0:
            # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
            raise ValueError(f"{field_name} possui um contador invalido.")
        # Copia o contador validado para o vetor que será devolvido.
        clock[node] = counter
    # Devolve clock ao código que chamou a função.
    return clock


# Aplica dataclass para gerar o construtor e outros métodos a partir dos campos declarados.
@dataclass(frozen=True)
# Define a classe Clinic, que agrupa os dados e comportamentos abaixo.
class Clinic:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Entidade 1: posto de saude que produz atualizacoes."""

    # Declara clinic_id: str como campo tipado ou parâmetro da estrutura em definição.
    clinic_id: str
    # Declara name: str como campo tipado ou parâmetro da estrutura em definição.
    name: str


# Aplica dataclass para gerar o construtor e outros métodos a partir dos campos declarados.
@dataclass
# Define a classe MedicalRecordUpdate, que agrupa os dados e comportamentos abaixo.
class MedicalRecordUpdate:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Entidade 2: evento que altera um campo do prontuario."""

    # Declara event_id: str como campo tipado ou parâmetro da estrutura em definição.
    event_id: str
    # Declara correlation_id: str como campo tipado ou parâmetro da estrutura em definição.
    correlation_id: str
    # Declara clinic_id: str como campo tipado ou parâmetro da estrutura em definição.
    clinic_id: str
    # Declara patient_id: str como campo tipado ou parâmetro da estrutura em definição.
    patient_id: str
    # Declara professional: str como campo tipado ou parâmetro da estrutura em definição.
    professional: str
    # Declara field_name: str como campo tipado ou parâmetro da estrutura em definição.
    field_name: str
    # Declara field_value: str como campo tipado ou parâmetro da estrutura em definição.
    field_value: str
    # Declara clinical_clock: dict[str, int] como campo tipado ou parâmetro da estrutura em definição.
    clinical_clock: dict[str, int]
    # Cria um dicionário novo para cada atualização, evitando compartilhar o vetor entre instâncias.
    processing_clock: dict[str, int] = field(default_factory=dict)
    # Calcula a expressão à direita e guarda o resultado em parent_event_id: str | None.
    parent_event_id: str | None = None
    # Gera o horário informativo no momento de criar cada atualização.
    received_at: str = field(default_factory=utc_now_text)

    # Faz o método receber a classe em cls para construir instâncias.
    @classmethod
    # Define from_client_dict; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def from_client_dict(cls, data: dict[str, Any]) -> "MedicalRecordUpdate":
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Valida os dados do cliente e completa IDs de rastreabilidade ausentes."""

        # Lista os campos textuais obrigatórios para aceitar a atualização.
        required_text = ("clinic_id", "patient_id", "professional", "field_name", "field_value")
        # Repete o bloco para cada name encontrado em required_text.
        for name in required_text:
            # Executa este ramo quando not isinstance(data.get(name), str) or not data[name].strip() for verdadeiro.
            if not isinstance(data.get(name), str) or not data[name].strip():
                # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
                raise ValueError(f"O campo textual '{name}' e obrigatorio.")

        # Gera um identificador aleatório para rastrear o evento.
        event_id = data.get("event_id") or str(uuid4())
        # Usa a correlação fornecida ou o ID do próprio evento quando ela está ausente.
        correlation_id = data.get("correlation_id") or event_id
        # Executa este ramo quando not isinstance(event_id, str) or not isinstance(correlation_id, str) for verdadeiro.
        if not isinstance(event_id, str) or not isinstance(correlation_id, str):
            # Interrompe o fluxo e sinaliza a exceção indicada ao chamador.
            raise ValueError("event_id e correlation_id devem ser textos.")

        # Devolve cls( ao código que chamou a função.
        return cls(
            # Fornece o argumento nomeado event_id à chamada em andamento.
            event_id=event_id,
            # Fornece o argumento nomeado correlation_id à chamada em andamento.
            correlation_id=correlation_id,
            # Fornece o argumento nomeado clinic_id à chamada em andamento.
            clinic_id=data["clinic_id"],
            # Fornece o argumento nomeado patient_id à chamada em andamento.
            patient_id=data["patient_id"],
            # Fornece o argumento nomeado professional à chamada em andamento.
            professional=data["professional"],
            # Fornece o argumento nomeado field_name à chamada em andamento.
            field_name=data["field_name"],
            # Fornece o argumento nomeado field_value à chamada em andamento.
            field_value=data["field_value"],
            # Fornece o argumento nomeado clinical_clock à chamada em andamento.
            clinical_clock=validate_clock(data.get("clinical_clock", {}), "clinical_clock"),
            # Fornece o argumento nomeado processing_clock à chamada em andamento.
            processing_clock=validate_clock(data.get("processing_clock", {}), "processing_clock"),
            # Fornece o argumento nomeado parent_event_id à chamada em andamento.
            parent_event_id=data.get("parent_event_id"),
            # Fornece o argumento nomeado received_at à chamada em andamento.
            received_at=str(data.get("received_at") or utc_now_text()),
        # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
        )

    # Faz o método receber a classe em cls para construir instâncias.
    @classmethod
    # Define from_queue_dict; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def from_queue_dict(cls, data: dict[str, Any]) -> "MedicalRecordUpdate":
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Reutiliza a validacao ao recuperar um evento da fila."""

        # Valida os dados recebidos do cliente e monta a entidade.
        return cls.from_client_dict(data)

    # Define to_dict; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def to_dict(self) -> dict[str, Any]:
        # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
        """Converte a entidade em dicionario serializavel como JSON."""

        # Converte os campos da dataclass em um dicionário.
        return asdict(self)


# Aplica dataclass para gerar o construtor e outros métodos a partir dos campos declarados.
@dataclass(frozen=True)
# Define a classe AuditRecord, que agrupa os dados e comportamentos abaixo.
class AuditRecord:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Entidade 3: registro imutavel do resultado da consolidacao."""

    # Declara event_id: str como campo tipado ou parâmetro da estrutura em definição.
    event_id: str
    # Declara patient_id: str como campo tipado ou parâmetro da estrutura em definição.
    patient_id: str
    # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
    worker_id: int
    # Declara leader_id: int como campo tipado ou parâmetro da estrutura em definição.
    leader_id: int
    # Declara causal_relation: str como campo tipado ou parâmetro da estrutura em definição.
    causal_relation: str
    # Declara decision: str como campo tipado ou parâmetro da estrutura em definição.
    decision: str
    # Declara clinical_clock: dict[str, int] como campo tipado ou parâmetro da estrutura em definição.
    clinical_clock: dict[str, int]
    # Declara processing_clock: dict[str, int] como campo tipado ou parâmetro da estrutura em definição.
    processing_clock: dict[str, int]
