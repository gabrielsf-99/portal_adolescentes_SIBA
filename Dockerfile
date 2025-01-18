# Usar imagem base do Python
FROM python:3.9-slim

# Configurar o diretório de trabalho no container
WORKDIR /app

# Copiar os arquivos necessários
COPY requirements.txt requirements.txt
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Flask (5000)
EXPOSE 5000

# Comando para rodar o servidor Flask
CMD ["python", "app.py"]

