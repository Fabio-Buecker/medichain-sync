# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Testa a normalizacao de textos copiados para o PowerShell."""

# Importa unittest para disponibilizar suas funções neste módulo.
import unittest

# Importa normalize_copied_text, parse_clock de src.client.
from src.client import normalize_copied_text, parse_clock


# Define a classe ClientTest, que agrupa os dados e comportamentos abaixo.
class ClientTest(unittest.TestCase):
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Confirma que barras acidentais antes de sublinhados nao quebram o JSON."""

    # Define test_normalizes_identifier; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_normalizes_identifier(self) -> None:
        # Verifica se o resultado obtido é igual ao esperado.
        self.assertEqual("paciente_001", normalize_copied_text("paciente\\_001"))

    # Define test_normalizes_clock_json; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_normalizes_clock_json(self) -> None:
        # Calcula a expressão à direita e guarda o resultado em raw_clock.
        raw_clock = '{"clinica\\_a":3,"clinica\\_b":1}'
        # Verifica se o resultado obtido é igual ao esperado.
        self.assertEqual({"clinica_a": 3, "clinica_b": 1}, parse_clock(raw_clock))


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa os testes definidos neste arquivo.
    unittest.main()
