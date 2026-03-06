FROM python:3.13-slim
RUN apt-get update && apt-get install -y nginx && pip install uv
WORKDIR /usr/src/app
COPY . .
RUN uv sync
# Copia o arquivo de configuração do NGINX.
COPY nginx/nginx.conf /etc/nginx/sites-available/default
# Expõe as portas 80 (para NGINX).
EXPOSE 80
# Inicia o NGINX em segundo plano.
CMD service nginx start && uv run task start