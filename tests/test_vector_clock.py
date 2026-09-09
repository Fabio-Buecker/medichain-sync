# Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
"""Testa as quatro relacoes possiveis entre relogios vetoriais."""

# Importa unittest para disponibilizar suas funções neste módulo.
import unittest

# Importa compare_clocks, increment_clock, merge_clocks de src.vector_clock.
from src.vector_clock import compare_clocks, increment_clock, merge_clocks


# Define a classe VectorClockTest, que agrupa os dados e comportamentos abaixo.
class VectorClockTest(unittest.TestCase):
    # Documenta a finalidade deste módulo, classe ou função; não executa a operação descrita.
    """Confirma as regras de causalidade apresentadas na disciplina."""

    # Define test_increment_and_merge; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_increment_and_merge(self) -> None:
        # Combina os vetores usando o maior contador de cada participante.
        merged = merge_clocks({"a": 2}, {"a": 1, "b": 3})
        # Verifica se o resultado obtido é igual ao esperado.
        self.assertEqual({"a": 2, "b": 3}, merged)
        # Incrementa o contador do participante no vetor.
        self.assertEqual({"a": 3, "b": 3}, increment_clock(merged, "a"))

    # Define test_before; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_before(self) -> None:
        # Compara os vetores para identificar anterioridade, igualdade ou concorrência.
        self.assertEqual("before", compare_clocks({"a": 1}, {"a": 2, "b": 0}))

    # Define test_after; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_after(self) -> None:
        # Compara os vetores para identificar anterioridade, igualdade ou concorrência.
        self.assertEqual("after", compare_clocks({"a": 2, "b": 1}, {"a": 1}))

    # Define test_equal; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_equal(self) -> None:
        # Compara os vetores para identificar anterioridade, igualdade ou concorrência.
        self.assertEqual("equal", compare_clocks({"a": 1}, {"a": 1, "b": 0}))

    # Define test_concurrent; os parâmetros e tipos descrevem suas entradas e seu retorno.
    def test_concurrent(self) -> None:
        # Compara os vetores para identificar anterioridade, igualdade ou concorrência.
        self.assertEqual("concurrent", compare_clocks({"a": 1}, {"b": 1}))


# Executa o ponto de entrada somente quando este módulo é iniciado diretamente.
if __name__ == "__main__":
    # Executa os testes definidos neste arquivo.
    unittest.main()
