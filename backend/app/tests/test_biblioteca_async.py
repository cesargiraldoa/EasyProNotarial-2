from __future__ import annotations

import unittest

from app.api.v1.endpoints.biblioteca_async import (
    AnalysisStatusResponse,
    StartAnalysisResponse,
    _json_object,
    router,
)


class BibliotecaAsyncContractTests(unittest.TestCase):
    def test_async_routes_are_registered(self):
        paths = {route.path for route in router.routes}
        self.assertIn("/biblioteca/analisis/iniciar", paths)
        self.assertIn("/biblioteca/analisis/{run_id}", paths)

    def test_start_response_supports_reused_running_job(self):
        payload = StartAnalysisResponse(run_id=17, status="running", reused=True)
        self.assertEqual(payload.run_id, 17)
        self.assertTrue(payload.reused)

    def test_status_response_returns_completed_review_version(self):
        payload = AnalysisStatusResponse(
            run_id=17,
            status="completed",
            review_document={
                "kind": "case_document",
                "case_id": 1,
                "document_id": 2,
                "version_id": 3,
            },
            stats={"wrapped_suggestions": 20},
        )
        self.assertEqual(payload.review_document["version_id"], 3)
        self.assertEqual(payload.stats["wrapped_suggestions"], 20)

    def test_json_object_rejects_non_object_or_invalid_payloads(self):
        self.assertEqual(_json_object('{"status":"ok"}'), {"status": "ok"})
        self.assertEqual(_json_object("[]"), {})
        self.assertEqual(_json_object("invalid"), {})
        self.assertEqual(_json_object(None), {})


if __name__ == "__main__":
    unittest.main()
