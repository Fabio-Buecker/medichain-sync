# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Mostra os dados consolidados e prova que principal e replica coincidem."""

# Importa json para disponibilizar suas funções neste módulo.
import json
# Importa os para disponibilizar suas funções neste módulo.
import os
# Importa Path de pathlib.
from pathlib import Path
# Importa sqlite3 para disponibilizar suas funções neste módulo.
import sqlite3


# Define read_database; os parâmetros e tipos descrevem suas entradas e seu retorno.
def read_database(path: Path) -> dict[str, list[dict[str, object]]]:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Le as tres tabelas e devolve colunas nomeadas para facilitar a defesa."""

    # Calcula a expressão à direita e guarda o resultado em result: dict[str, list[dict[str, object]]].
    result: dict[str, list[dict[str, object]]] = {}
    # Abre uma conexão com o arquivo SQLite.
    connection = sqlite3.connect(path)
    # Inicia um bloco cujas falhas serão tratadas por except ou cuja limpeza ocorrerá em finally.
    try:
        # Faz o SQLite retornar linhas acessíveis pelos nomes das colunas.
        connection.row_factory = sqlite3.Row
        # Repete o bloco para cada table encontrado em ("record_state", "audit_log", "conflicts").
        for table in ("record_state", "audit_log", "conflicts"):
            # Executa a instrução SQL com os parâmetros fornecidos.
            rows = connection.execute(f"SELECT * FROM {table} ORDER BY rowid").fetchall()
            # Converte as linhas desta tabela em dicionários para exibição como JSON.
            result[table] = [dict(row) for row in rows]
    # Executa a limpeza ao sair do bloco, mesmo se houver erro ou retorno antecipado.
    finally:
        # Fecha o recurso e libera a conexão ou socket.
        connection.close()
    # Devolve result ao código que chamou a função.
    return result


# Define main; os parâmetros e tipos descrevem suas entradas e seu retorno.
def main() -> None:
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Imprime as copias e uma comparacao booleana entre elas."""

    # Lê a variável de ambiente, usando o padrão se ela estiver ausente.
    data_directory = Path(os.getenv("DATA_DIR", "./data"))
    # Lê o conteúdo das tabelas do banco principal.
    primary = read_database(data_directory / "medichain-primary.db")
    # Lê o conteúdo das tabelas do banco réplica.
    replica = read_database(data_directory / "medichain-replica.db")
    # Serializa os dados em texto JSON.
    print(json.dumps({"primary": primary, "replica": replica}, ensure_ascii=False, indent=2))
    # Exibe informações no terminal para acompanhar a execução.
    print(f"COPIAS_IDENTICAS={primary == replica}")


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa main() para continuar a operação desta função.
    main()
