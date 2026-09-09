# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Operacoes do Relogio Vetorial estudado na Unidade 2."""

# Importa Literal de typing.
from typing import Literal


# Restringe a anotação de retorno às quatro relações possíveis entre vetores.
ClockRelation = Literal["before", "after", "equal", "concurrent"]


# Define merge_clocks; os parâmetros e tipos descrevem suas entradas e seu retorno.
def merge_clocks(first: dict[str, int], second: dict[str, int]) -> dict[str, int]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Combina dois relogios escolhendo o maior contador de cada participante."""

    # Reúne os participantes dos dois vetores; participantes ausentes serão tratados como zero.
    all_nodes = set(first) | set(second)
    # Monta o vetor combinado escolhendo o maior contador por participante; ausentes valem zero.
    return {node: max(first.get(node, 0), second.get(node, 0)) for node in all_nodes}


# Define increment_clock; os parâmetros e tipos descrevem suas entradas e seu retorno.
def increment_clock(clock: dict[str, int], node: str) -> dict[str, int]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Cria uma copia do relogio e registra um novo evento no no informado."""

    # Copia o vetor de entrada para não modificar o dicionário recebido.
    updated = dict(clock)
    # Incrementa o contador deste participante; um participante novo começa em zero.
    updated[node] = updated.get(node, 0) + 1
    # Devolve updated ao código que chamou a função.
    return updated


# Define compare_clocks; os parâmetros e tipos descrevem suas entradas e seu retorno.
def compare_clocks(first: dict[str, int], second: dict[str, int]) -> ClockRelation:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Informa se o primeiro evento ocorreu antes, depois ou concorrentemente."""

    # Reúne os participantes dos dois vetores; participantes ausentes serão tratados como zero.
    all_nodes = set(first) | set(second)
    # Verifica se existe alguma posição em que o primeiro vetor é menor que o segundo.
    first_is_smaller = any(first.get(node, 0) < second.get(node, 0) for node in all_nodes)
    # Verifica se existe alguma posição em que o primeiro vetor é maior que o segundo.
    first_is_greater = any(first.get(node, 0) > second.get(node, 0) for node in all_nodes)

    # Executa este ramo quando first_is_smaller and first_is_greater for verdadeiro.
    if first_is_smaller and first_is_greater:
        # Devolve "concurrent" ao código que chamou a função.
        return "concurrent"
    # Executa este ramo quando first_is_smaller for verdadeiro.
    if first_is_smaller:
        # Devolve "before" ao código que chamou a função.
        return "before"
    # Executa este ramo quando first_is_greater for verdadeiro.
    if first_is_greater:
        # Devolve "after" ao código que chamou a função.
        return "after"
    # Devolve "equal" ao código que chamou a função.
    return "equal"


# Define deterministic_key; os parâmetros e tipos descrevem suas entradas e seu retorno.
def deterministic_key(clock: dict[str, int], event_id: str) -> tuple[int, str, str]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Cria uma chave estavel para desempatar conflitos sem usar relogio fisico."""

    # Ordena os nomes dos participantes e monta um texto estável com os seus contadores.
    ordered_clock = ",".join(f"{node}:{clock[node]}" for node in sorted(clock))
    # Devolve a tupla de desempate: soma dos contadores, vetor ordenado e ID do evento.
    return sum(clock.values()), ordered_clock, event_id
