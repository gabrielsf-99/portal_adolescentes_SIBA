# Usar imagem base do Python
FROM python:3.9-slim

# Instalar dependências do sistema necessárias para o SQLite
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar o diretório de trabalho para o backend
WORKDIR /app/backend

# Copiar os arquivos necessários
COPY requirements.txt requirements.txt
COPY . .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask (5000)
EXPOSE 5000

# Comando para rodar o servidor Flask
CMD ["python", "app.py"]