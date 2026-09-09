# Usa uma imagem oficial e pequena do Python 3.10, versao minima pedida no trabalho.
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container.
WORKDIR /app

# Copia primeiro a lista de dependencias para aproveitar o cache do Docker.
COPY requirements.txt .

# Instala apenas a biblioteca cliente do RabbitMQ.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o codigo-fonte do projeto para o container.
COPY src ./src

# Copia o script SQL lido pelo modulo de persistencia.
COPY database ./database

# Permite importar o pacote src ao executar os modulos.
ENV PYTHONPATH=/app

# O comando real e informado para cada servico no docker-compose.yml.
CMD ["python", "-m", "src.gateway"]
