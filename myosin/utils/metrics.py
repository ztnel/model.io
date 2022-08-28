from prometheus_client import Summary, Gauge, Info, Counter


class Metrics:

    active_contexts = Gauge(
        name="myosin_active_contexts",
        documentation="Number of active threads inside state context manager."
    )

    cache_latency = Summary(
        name="myosin_cache_latency",
        documentation="Model caching write latency.",
        labelnames=["model"]
    )

    checkout_latency = Summary(
        name="myosin_checkout_latency",
        documentation="Model checkout latency.",
        labelnames=["model"]
    )

    commit_latency = Summary(
        name="myosin_commit_latency",
        documentation="Model commit latency.",
        labelnames=["model"]
    )

    exc_count = Counter(
        name="myosin_cb_exc_count",
        documentation="Subscription callback exception counter.",
        labelnames=["model"]
    )

    meta = Info(
        name="myosin_meta",
        documentation="Install metadata."
    )
