import http.client
import json
import sys
import threading
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from simulated_api import create_server


class SimulatedAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        raw_body = response.read()
        connection.close()
        return response.status, json.loads(raw_body.decode("utf-8"))

    def post_json(self, payload):
        body = json.dumps(payload)
        return self.request(
            "POST",
            "/ask",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Content-Length": str(len(body.encode("utf-8"))),
            },
        )

    def test_health_returns_ok(self):
        status, payload = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ok"})

    def test_known_question_returns_mock_answer(self):
        status, payload = self.post_json({"question": "What is Python?"})
        self.assertEqual(status, 200)
        self.assertEqual(
            payload,
            {"answer": "Python is a programming language.", "source": "mock"},
        )

    def test_malformed_json_returns_bad_request(self):
        status, payload = self.request(
            "POST",
            "/ask",
            body="{not valid json",
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(payload, {"error": "Malformed JSON"})

    def test_unknown_route_returns_not_found(self):
        status, payload = self.request("GET", "/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(payload, {"error": "Unknown endpoint"})

    def test_empty_question_is_invalid(self):
        status, payload = self.post_json({"question": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(
            payload,
            {"error": "Question must be a non-empty string"},
        )

    def test_unknown_question_uses_safe_fallback(self):
        status, payload = self.post_json({"question": "Where is Mars?"})
        self.assertEqual(status, 200)
        self.assertEqual(payload["source"], "mock")
        self.assertIn("not in the simulated answer dictionary", payload["answer"])


if __name__ == "__main__":
    unittest.main()
