"""Small local HTTP API used for Stage 1 of the SBN AI API project."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HOST = "127.0.0.1"
PORT = 8000

ANSWERS = {
    "what is python?": "Python is a programming language.",
    "what is an api?": "An API allows different software applications to communicate.",
    "what is json?": "JSON is a text format for storing and exchanging structured data.",
}


class SimulatedAIHandler(BaseHTTPRequestHandler):
    def send_json(self, status_code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.send_json(200, {"status": "ok"})
            return
        self.send_json(404, {"error": "Unknown endpoint"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/ask":
            self.send_json(404, {"error": "Unknown endpoint"})
            return

        content_length = self.headers.get("Content-Length")
        if content_length is None:
            self.send_json(400, {"error": "Request body is required"})
            return

        try:
            length = int(content_length)
            body = self.rfile.read(length)
            request_data = json.loads(body.decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(400, {"error": "Malformed JSON"})
            return

        if not isinstance(request_data, dict):
            self.send_json(400, {"error": "JSON body must be an object"})
            return

        question = request_data.get("question")
        if not isinstance(question, str) or not question.strip():
            self.send_json(400, {"error": "Question must be a non-empty string"})
            return

        normalized_question = question.strip().lower()
        answer = ANSWERS.get(
            normalized_question,
            "That question is not in the simulated answer dictionary.",
        )
        self.send_json(200, {"answer": answer, "source": "mock"})

    def do_PUT(self):
        self.send_json(405, {"error": "Method not allowed"})

    def do_DELETE(self):
        self.send_json(405, {"error": "Method not allowed"})

    def log_message(self, format_string, *args):
        print("%s - %s" % (self.address_string(), format_string % args))


def create_server(host=HOST, port=PORT):
    return ThreadingHTTPServer((host, port), SimulatedAIHandler)


def main():
    server = create_server()
    print("Simulated AI API listening at http://%s:%d" % (HOST, PORT))
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping simulated AI API.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
