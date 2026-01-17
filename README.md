# Multi-Agent Banking System

Sistema multiagente para operações bancárias utilizando Python, FastAPI, CrewAI e MongoDB.

## Tecnologias

- Python 3.12
- FastAPI
- CrewAI
- MongoDB
- OpenAI

## Requisitos

- Python 3.12+
- MongoDB 7+

## Instalação

1. Clone o repositório

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

## Executando

### Local (Windows)
```bash
run.bat
```

### Local (Linux/Mac)
```bash
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker-compose up -d  # Inicia MongoDB
docker build -t banking-system .
docker run -p 8000:8000 --env-file .env banking-system
```

