from contextlib import contextmanager
from time import perf_counter

import sentry_sdk
from sentry_sdk import metrics


def _clean_attributes(attributes):
    if not attributes:
        return None

    return {key: value for key, value in attributes.items() if value is not None}


def sentry_count(name, value=1, *, attributes=None, unit=None):
    try:
        metrics.count(name, value, unit=unit, attributes=_clean_attributes(attributes))
    except Exception:
        pass


def sentry_distribution(name, value, *, attributes=None, unit=None):
    try:
        metrics.distribution(name, value, unit=unit, attributes=_clean_attributes(attributes))
    except Exception:
        pass


@contextmanager
def sentry_duration_metric(name, *, attributes=None, unit="millisecond"):
    start = perf_counter()
    try:
        yield
    finally:
        sentry_distribution(
            name,
            (perf_counter() - start) * 1000,
            unit=unit,
            attributes=attributes,
        )


@contextmanager
def sentry_span(op, name, *, attributes=None):
    with sentry_sdk.start_span(op=op, name=name) as span:
        for key, value in (_clean_attributes(attributes) or {}).items():
            span.set_data(key, value)
        yield span


@contextmanager
def sentry_task_transaction(name, *, attributes=None):
    with sentry_sdk.start_transaction(op="queue.task", name=name) as transaction:
        for key, value in (_clean_attributes(attributes) or {}).items():
            transaction.set_data(key, value)
        yield transaction
