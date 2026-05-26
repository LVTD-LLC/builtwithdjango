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


def _set_sentry_data(target, attributes):
    for key, value in (_clean_attributes(attributes) or {}).items():
        try:
            target.set_data(key, value)
        except Exception:
            pass


@contextmanager
def _safe_sentry_context(context_factory, *, attributes=None):
    sentry_context = None
    span = None

    try:
        sentry_context = context_factory()
        span = sentry_context.__enter__()
        _set_sentry_data(span, attributes)
    except Exception:
        yield None
        return

    try:
        yield span
    except BaseException as error:
        try:
            sentry_context.__exit__(type(error), error, error.__traceback__)
        except Exception:
            pass
        raise
    else:
        try:
            sentry_context.__exit__(None, None, None)
        except Exception:
            pass


@contextmanager
def sentry_span(op, name, *, attributes=None):
    with _safe_sentry_context(
        lambda: sentry_sdk.start_span(op=op, name=name),
        attributes=attributes,
    ) as span:
        yield span


@contextmanager
def sentry_task_transaction(name, *, attributes=None):
    with _safe_sentry_context(
        lambda: sentry_sdk.start_transaction(op="queue.task", name=name),
        attributes=attributes,
    ) as transaction:
        yield transaction
