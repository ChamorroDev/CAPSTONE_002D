@echo off
echo Iniciando n8n en Docker...
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
echo n8n se esta ejecutando. Accede a http://localhost:5678
pause