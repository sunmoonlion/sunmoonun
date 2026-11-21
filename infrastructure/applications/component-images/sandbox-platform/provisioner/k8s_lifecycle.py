"""Stop one observed Pod without acting on a replacement or deleting metering evidence."""


def stopping_or_done(pod):
    return pod.get("spec", {}).get("activeDeadlineSeconds") == 1 or pod.get(
        "status", {}
    ).get("phase") in ("Succeeded", "Failed")


async def expire_pod(kube, pod, *, absent_ok):
    if stopping_or_done(pod):
        return
    name = pod["metadata"]["name"]
    uid = pod["metadata"]["uid"]
    response = await kube.client.patch(
        kube.path("pods", name),
        headers={"Content-Type": "application/json-patch+json"},
        json=[
            {"op": "test", "path": "/metadata/uid", "value": uid},
            {"op": "add", "path": "/spec/activeDeadlineSeconds", "value": 1},
        ],
    )
    if response.status_code in (404, 409, 422):
        current = await kube.get("pods", name)
        if (current is None and absent_ok) or (
            current and current["metadata"]["uid"] == uid and stopping_or_done(current)
        ):
            return
    response.raise_for_status()
