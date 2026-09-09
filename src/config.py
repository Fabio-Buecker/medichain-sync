# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Le as configuracoes simples fornecidas por variaveis de ambiente."""

# Importa dataclass de dataclasses.
from dataclasses import dataclass
# Importa os para disponibilizar suas funções neste módulo.
import os


# Aplica dataclass para gerar o construtor e outros métodos a partir dos campos declarados.
@dataclass(frozen=True)
# Define a classe Peer, que agrupa os dados e comportamentos abaixo.
class Peer:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Representa o endereco de coordenacao de um worker."""

    # Declara worker_id: int como campo tipado ou parâmetro da estrutura em definição.
    worker_id: int
    # Declara host: str como campo tipado ou parâmetro da estrutura em definição.
    host: str
    # Declara port: int como campo tipado ou parâmetro da estrutura em definição.
    port: int


# Define env_int; os parâmetros e tipos descrevem suas entradas e seu retorno.
def env_int(name: str, default: int) -> int:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le um numero inteiro do ambiente ou devolve o valor padrao."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    return int(os.getenv(name, str(default)))


# Define env_float; os parâmetros e tipos descrevem suas entradas e seu retorno.
def env_float(name: str, default: float) -> float:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le um numero decimal do ambiente ou devolve o valor padrao."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    return float(os.getenv(name, str(default)))


# Define load_peers; os parâmetros e tipos descrevem suas entradas e seu retorno.
def load_peers() -> dict[int, Peer]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Converte '1:host:porta,2:host:porta' em um dicionario de workers."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    raw_peers = os.getenv(
        # Fornece esta parte do texto ou argumento à operação iniciada acima.
        "WORKER_PEERS",
        # Fornece esta parte do texto ou argumento à operação iniciada acima.
        "1:127.0.0.1:6001,2:127.0.0.1:6002,3:127.0.0.1:6003",
    # Fecha a chamada ou a estrutura de dados iniciada nas linhas anteriores.
    )
    # Calcula a expressão à direita e guarda o resultado em peers: dict[int, Peer].
    peers: dict[int, Peer] = {}
    # Repete o bloco para cada raw_peer encontrado em raw_peers.split(",").
    for raw_peer in raw_peers.split(","):
        # Separa o ID, o endereço e a porta usando os dois-pontos da configuração.
        worker_id_text, host, port_text = raw_peer.split(":")
        # Converte o ID lido como texto em número inteiro.
        worker_id = int(worker_id_text)
        # Associa o ID ao objeto Peer com o endereço do worker.
        peers[worker_id] = Peer(worker_id, host, int(port_text))
    # Devolve peers ao código que chamou a função.
    return peers
