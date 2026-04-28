# server-postify

Backend simple de Postify hecho con FastAPI.

## Requisitos

- Python 3.10 o superior
- pip

## Instalacion

Desde la raiz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn
```

## Correr el servidor

```bash
uvicorn main:app --reload
```

El servidor queda disponible en:

```text
http://127.0.0.1:8000
```

Para probar que esta vivo, abre esa URL en el navegador o ejecuta:

```bash
curl http://127.0.0.1:8000
```

La respuesta esperada por ahora es:

```json
{"message":"Hello World"}
```

## Documentacion interactiva

FastAPI genera automaticamente estas rutas:

```bash
fastapi dev
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Estructura actual

```text
server-postify/
├── main.py
├── README.md
└── .gitignore
```

## Notas

- No subas `.venv/`, `__pycache__/`, archivos `.env` ni caches locales.
- Si agregas dependencias nuevas, conviene crear un `requirements.txt` con:

```bash
pip freeze > requirements.txt
```
