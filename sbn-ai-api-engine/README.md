# SBN AI API Communication Engine - Stage 1

Student: Ann

This folder contains a local simulated API for Module 01, Part 2, Stage 1. It uses only the Python standard library. The server has no AI model behind it: it returns fixed answers or a clear simulated fallback.

## API endpoints

| Method | Endpoint | Success response |
|---|---|---|
| GET | `/health` | `200 {"status":"ok"}` |
| POST | `/ask` | `200 {"answer":"...","source":"mock"}` |

The `/ask` body must be a JSON object containing a non-empty string named `question`.

## Run

From the repository root:

```powershell
python sbn-ai-api-engine/simulated_api.py
```

The server listens at `http://127.0.0.1:8000`.

## Stage 1 HTTP interactions

Open a second terminal and run:

```powershell
curl.exe http://127.0.0.1:8000/health

curl.exe -X POST http://127.0.0.1:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"question":"What is Python?"}'

curl.exe -X POST http://127.0.0.1:8000/ask `
  -H "Content-Type: application/json" `
  --data-raw '{not valid json'

curl.exe http://127.0.0.1:8000/unknown
```

PowerShell uses backticks for line continuation. `curl.exe --data-raw '{not valid json'` sends a POST request with raw malformed JSON and is useful for this HTTP laboratory.

## Run tests

From the repository root:

```powershell
python -m unittest discover -s sbn-ai-api-engine/tests -v
```

## Concepts

- **GET** requests information from a server and has no request body in this application.
- **POST** submits a request body. `/ask` uses POST so the question can be sent as JSON.
- **JSON** is a structured text format. `Content-Type: application/json` tells the server how to interpret the body.
- **HTTP status codes** summarize request outcomes. `200` means success, `400` means malformed or invalid input, `404` means an unknown route, and `405` means an unsupported HTTP method.

## Evidence

Typical results are:

```text
GET /health -> HTTP 200
{"status":"ok"}

POST /ask -> HTTP 200
{"answer":"Python is a programming language.","source":"mock"}

POST /ask with malformed JSON -> HTTP 400
{"error":"Malformed JSON"}

GET /unknown -> HTTP 404
{"error":"Unknown endpoint"}
```
