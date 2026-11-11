"""Exercise the rendered identity reconciler against a synthetic Casdoor API."""

import copy
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml
from test_signup import render_identity

ORIGIN = "https://identity.example.test"
DEFINITIONS = {
    s: {
        "name": "test-" + s,
        "client_id": "client-" + s,
        "origin": "https://" + s + ".example.test",
    }
    for s in ("admin", "web")
}


class Casdoor:
    def __init__(self):
        self.objects = {
            "application": {"admin/app-built-in": {"cert": "test-cert"}},
            "organization": {},
            "role": {},
        }
        self.writes = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def request(self, method, path, json=None, params=None):
        if path == "/api/login":
            data = "ok"
        else:
            operation, kind = path.removeprefix("/api/").split("-", 1)
            if kind == "applications":
                data = list(self.objects["application"].values())
            elif operation == "get":
                data = self.objects[kind].get(params["id"])
            else:
                self.writes.append((path, copy.deepcopy(json)))
                self.objects[kind][json["owner"] + "/" + json["name"]] = copy.deepcopy(
                    json
                )
                data = "Affected"
        return SimpleNamespace(
            status_code=200, json=lambda: {"status": "ok", "data": copy.deepcopy(data)}
        )

    def get(self, path):
        data = (
            {"keys": [{"kid": "test"}]}
            if path.endswith("/jwks")
            else {
                "issuer": ORIGIN,
                "code_challenge_methods_supported": ["S256"],
                "authorization_endpoint": ORIGIN + "/authorize",
                "token_endpoint": ORIGIN + "/token",
                "jwks_uri": ORIGIN + "/jwks",
            }
        )
        return SimpleNamespace(status_code=200, json=lambda: data)


class BrowserLifetime(unittest.TestCase):
    def setUp(self):
        source = list(yaml.safe_load_all(render_identity("tpl")))[0]["data"][
            "provision.py"
        ]
        self.module = {"__name__": "test_reconciler"}
        with patch.dict(sys.modules, {"httpx": SimpleNamespace(Client=None)}):
            exec(compile(source, "<rendered-provision>", "exec"), self.module)
        self.api = Casdoor()

    def run_reconciler(self):
        env = {
            "CASDOOR_ORIGIN": ORIGIN,
            "CASDOOR_INTERNAL_ENDPOINT": ORIGIN,
            "CASDOOR_ORGANIZATION": "built-in",
            "CASDOOR_USER_ORGANIZATION": "sunmoonai",
            "BROWSER_CLIENTS": json.dumps(DEFINITIONS),
        }
        values = {
            "/run/app/clients.json": {
                "web_secret": "synthetic-web",
                "admin_secret": "synthetic-admin",
            },
            "/run/admin/init_data.json": {
                "users": [
                    {"owner": "built-in", "name": "admin", "password": "synthetic"}
                ]
            },
        }
        with (
            patch.dict(os.environ, env, clear=True),
            patch.object(Path, "read_text", lambda p: json.dumps(values[str(p)])),
            patch.object(self.module["httpx"], "Client", return_value=self.api),
            redirect_stdout(io.StringIO()),
        ):
            self.module["run"]()

    def test_migrates_both_lifetimes_and_is_idempotent(self):
        self.run_reconciler()
        web = self.api.objects["application"]["admin/test-web"]
        self.assertEqual(web["expireInHours"], 24)
        self.assertEqual(
            self.api.objects["application"]["admin/test-admin"]["expireInHours"], 24
        )
        web["expireInHours"] = 12
        self.api.objects["application"]["admin/test-admin"]["expireInHours"] = 1
        before = copy.deepcopy(self.api.objects)
        self.api.writes.clear()
        self.run_reconciler()
        before["application"]["admin/test-web"]["expireInHours"] = 24
        before["application"]["admin/test-admin"]["expireInHours"] = 24
        self.assertEqual(self.api.objects, before)
        self.assertEqual(
            [path for path, _ in self.api.writes], ["/api/update-application"] * 2
        )
        self.api.writes.clear()
        self.run_reconciler()
        self.assertEqual(self.api.writes, [])

    def test_unrelated_drift_stops_instead_of_overwriting_identity(self):
        self.run_reconciler()
        web = self.api.objects["application"]["admin/test-web"]
        web.update(expireInHours=12, clientSecret="unexpected-secret")
        self.api.writes.clear()
        with self.assertRaisesRegex(RuntimeError, "explicit migration required"):
            self.run_reconciler()
        self.assertEqual(self.api.writes, [])
        self.assertEqual(web["expireInHours"], 12)

    def test_admin_lifetime_change_preserves_security_boundaries(self):
        self.run_reconciler()
        admin = self.api.objects["application"]["admin/test-admin"]
        self.assertFalse(admin["enableSigninSession"])
        self.assertFalse(admin["enableAutoSignin"])
        self.assertFalse(admin["enableSignUp"])
        for field, value in [("clientSecret", "unexpected-secret"), ("organization", "sunmoonai"),
                             ("grantTypes", ["client_credentials"])]:
            original = copy.deepcopy(admin)
            admin.update(expireInHours=1, **{field: value})
            self.api.writes.clear()
            with self.subTest(field=field), self.assertRaisesRegex(RuntimeError, "explicit migration required"):
                self.run_reconciler()
            self.assertEqual(self.api.writes, [])
            admin.clear()
            admin.update(original)

    def test_unrecognized_admin_lifetime_is_not_silently_changed(self):
        self.run_reconciler()
        admin = self.api.objects["application"]["admin/test-admin"]
        admin["expireInHours"] = 2
        self.api.writes.clear()
        with self.assertRaisesRegex(RuntimeError, "explicit migration required"):
            self.run_reconciler()
        self.assertEqual(self.api.writes, [])


if __name__ == "__main__":
    unittest.main()
