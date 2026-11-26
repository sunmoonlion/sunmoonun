"""Compare two traversal orders of the same DAG against the actual preview."""

from types import SimpleNamespace as Node

from app.application.workbench.formal_method_catalog import connection_preview


def reference(name):
    return Node(method_id=name, version=1, digest=name)


def group(*children):
    steps = [
        Node(inputs={}, always_required=True, candidates=[reference(child)])
        for child in children
    ]
    return Node(procedure=Node(kind="orchestration", steps=steps), access_requirements=[])


def test_preview_depth_depends_on_traversal_order():
    definitions = {"leaf": Node(procedure=Node(kind="tool"), access_requirements=[])}
    definitions["shared"] = group("leaf")
    for level in range(15):
        definitions[str(level)] = group(str(level + 1) if level < 14 else "shared")

    def complete(order):
        definitions["root"] = group(*order)
        versions = {(name, 1, name): value for name, value in definitions.items()}
        return connection_preview(reference("root"), versions)["complete"]

    assert complete(["shared", "0"]) is True
    assert complete(["0", "shared"]) is False
