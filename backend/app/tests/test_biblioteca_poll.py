from __future__ import annotations

import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.biblioteca_poll import (
    POLL_SCOPE,
    SecureStartAnalysisResponse,
    _create_poll_token,
    _validate_poll_token,
    router,
)


class BibliotecaPollAuthTests(unittest.TestCase):
    def test_secure_routes_are_registered(self):
        paths = {route.path for route in router.routes}
        self.assertIn("/biblioteca/analisis/iniciar-seguro", paths)
        self.assertIn("/biblioteca/analisis/{run_id}/estado-seguro", paths)

    def test_start_response_contains_poll_token(self):
        payload = SecureStartAnalysisResponse(
            run_id=7,
            status="running",
            reused=True,
            poll_token="token",
        )
        self.assertEqual(payload.run_id, 7)
        self.assertEqual(payload.poll_token, "token")

    def test_poll_token_is_scoped_to_run(self):
        token = _create_poll_token(7)
        claims = _validate_poll_token(7, f"Bearer {token}")
        self.assertEqual(claims["scope"], POLL_SCOPE)
        self.assertEqual(int(claims["run_id"]), 7)

    def test_poll_token_rejects_other_run(self):
        token = _create_poll_token(7)
        with self.assertRaises(HTTPException) as context:
            _validate_poll_token(8, f"Bearer {token}")
        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
