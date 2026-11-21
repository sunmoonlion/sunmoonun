"""The two publication jobs have distinct identities and no resident credential mount."""

import unittest
from pathlib import Path

import yaml
from jinja2 import ChainableUndefined
from jinja2.nativetypes import NativeEnvironment

ROOT = Path(__file__).resolve().parents[3] / "gitops/components/app-platform"


class FunctionPublishIdentities(unittest.TestCase):
    def test_release_stage_is_bound_to_its_own_publisher(self):
        renderer = NativeEnvironment(undefined=ChainableUndefined)
        clients = set()
        for app in ("knowbase", "knowbench"):
            component = ROOT / (app + "-app") / (app + "-backend")
            key = app + "_backend_deployment"
            cfg = yaml.safe_load((component / "config.yaml").read_text())[key]
            [client] = [
                c for c in cfg["service_clients"] if c["relation"] == "function-publish"
            ]
            self.assertEqual(
                (client["target"], client["scope"], client["roles"]),
                ("knowbench", "knowbench:function-publish", []),
            )
            clients.add(client["client_id"])
            if app == "knowbench":
                self.assertEqual(
                    {
                        r["caller"]
                        for r in cfg["service_receivers"]
                        if r["enabled"] and r["relation"] == "function-publish"
                    },
                    {"knowbase", "knowbench"},
                )
            stages = {
                s["name"]: s
                for s in yaml.safe_load((component / "stage.yaml").read_text())[
                    "stages"
                ]
            }
            identity = app + "-knowbench-function-publish-identity"
            runtime = stages[app + "-runtime"]
            context = {
                key: cfg,
                app + "_deployment": {"enabled": True},
                "knowbench_agent_releases": {"enabled": False},
            }
            for enabled in (True, False):
                client["enabled"] = enabled
                self.assertEqual(
                    renderer.from_string(stages[identity]["enabled"]).render(context),
                    enabled,
                )
                self.assertEqual(
                    identity
                    in renderer.from_string(runtime["dependsOn"]).render(context),
                    enabled,
                )
                resources = renderer.from_string(runtime["resources"]).render(context)
                self.assertEqual(
                    "knowbench-function-publish-service.sops.yaml" in resources, enabled
                )
        self.assertEqual(len(clients), 2)
