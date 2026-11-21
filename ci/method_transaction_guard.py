"""Pytest plugin for formal-method service integration tests in the three backends."""

from contextvars import ContextVar
from weakref import ref

import httpx
import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session


@pytest.fixture(autouse=True)
def guard_method_http(monkeypatch):
    # Track transactions in the flow that opened them, including SQLAlchemy
    # autobegin on SELECT. Sibling requests can use separate sessions concurrently.
    transactions = ContextVar("method_test_transactions", default=())

    def live():
        return [
            tx for pointer in transactions.get() if (tx := pointer()) and tx.is_active
        ]

    def opened(session, transaction):
        if transaction.parent is None:
            transactions.set(tuple(ref(tx) for tx in (*live(), transaction)))

    send = httpx.AsyncClient.send

    async def checked(client, request, **options):
        assert not live(), "Cross-service HTTP while a SQLAlchemy transaction is open"
        return await send(client, request, **options)

    event.listen(Session, "after_transaction_create", opened)
    monkeypatch.setattr(httpx.AsyncClient, "send", checked)
    try:
        yield
    finally:
        event.remove(Session, "after_transaction_create", opened)
