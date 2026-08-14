"""
17_observability_and_monitoring.py

Section 17: Observability & Monitoring
    - The three pillars: logs, metrics, traces
    - Metrics: counters, gauges, histograms (and why percentiles beat averages)
    - Distributed tracing: correlating ONE request across multiple services
    - SLIs, SLOs, and error budgets
    - Alerting: symptom-based vs. cause-based, avoiding pager fatigue

Why this gets its own file, separate from 08_devops's logging and
12_debugging_tooling.py's debugger/traceback work: those two are about
understanding ONE thing that already broke, on a machine you can inspect.
Observability is about ANSWERING QUESTIONS YOU DIDN'T ANTICIPATE, across a
system with many moving parts, in production, from data collected before
you knew you'd need it — a genuinely different skill, and one that shows
up constantly in senior/staff-level work (on-call rotations, incident
response, capacity planning) that pure coding ability doesn't cover.

Run: python 17_observability_and_monitoring.py
"""

import random
import time
import uuid


# ---------------------------------------------------------------------------
# The Three Pillars of Observability
# ---------------------------------------------------------------------------
THREE_PILLARS_NOTES = """
Logs   - discrete, timestamped EVENTS with detail ("user 42 borrowed '1984'
         at 14:03:01, took 12ms"). Best for answering "what exactly
         happened, in this ONE case?" Expensive to store/search at volume,
         which is why you don't log every metric-worthy event this way.
         (This course's 08_devops structured-JSON-logging section is this
         pillar.)

Metrics - numeric measurements AGGREGATED over time ("average request
         latency was 45ms over the last 5 minutes"). Cheap to store even
         at huge volume, because you're keeping numbers, not full event
         detail — but you lose the ability to ask "which SPECIFIC request
         was slow?" once it's aggregated. Best for "is the system healthy
         RIGHT NOW, and is it trending the wrong way?"

Traces  - the path of ONE request as it moves through multiple services
         ("checkout -> auth service (8ms) -> payment service (120ms) ->
         database (4ms)"). Best for "which specific HOP in a multi-service
         request was slow?" — something neither logs nor metrics alone can
         answer once a request touches more than one process.

None of the three replaces the others. A real incident usually goes:
metrics show something's wrong (error rate spiked) -> traces show WHERE in
the request path it's happening -> logs show the exact detail of what went
wrong at that specific point.
"""


def demo_three_pillars():
    print("\n--- The Three Pillars of Observability ---")
    print(THREE_PILLARS_NOTES)


# ---------------------------------------------------------------------------
# Metrics: counters, gauges, histograms
# ---------------------------------------------------------------------------
class MetricsRegistry:
    """
    A tiny in-memory stand-in for what a real metrics client (prometheus_client,
    statsd, Datadog's dogstatsd) gives you — enough to show the SHAPE of the
    three metric types every one of those libraries is built around.
    """
    def __init__(self):
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, by: int = 1):
        # New words in this line:
        #   counter  -> a number that only ever goes UP (or resets to 0 on
        #        restart) — total requests served, total errors, total books
        #        borrowed. You never "decrement" a counter; if a number can
        #        go both up and down, it's a gauge instead (below).
        self._counters[name] = self._counters.get(name, 0) + by

    def set_gauge(self, name: str, value: float):
        # New words in this line:
        #   gauge  -> a number that can go up OR down, representing a
        #        current SNAPSHOT — active connections right now, queue
        #        depth right now, memory used right now. Unlike a counter,
        #        it's meaningful to just look at the current value alone.
        self._gauges[name] = value

    def observe(self, name: str, value: float):
        # New words in this line:
        #   histogram  -> records the full DISTRIBUTION of many
        #        measurements (every request's latency, not just the count
        #        of requests) — enough data to compute percentiles later,
        #        which a plain average can't give you back (see below)
        self._histograms.setdefault(name, []).append(value)

    def summary(self) -> dict:
        histogram_summary = {}
        for name, values in self._histograms.items():
            ordered = sorted(values)
            histogram_summary[name] = {
                "count": len(ordered),
                "avg": sum(ordered) / len(ordered),
                "p50": ordered[len(ordered) // 2],
                "p99": ordered[min(int(len(ordered) * 0.99), len(ordered) - 1)],
                # New words in this line:
                #   p50 / p99 ("50th/99th percentile")  -> p50 is the MEDIAN:
                #        half of all measurements were faster, half slower.
                #        p99 is "99% of requests were AT LEAST this fast" —
                #        i.e. the slowest 1%. Percentiles matter because an
                #        AVERAGE hides outliers: if 99 requests take 10ms and
                #        1 takes 5000ms, the average (~59ms) looks fine while
                #        1% of your real users are having a terrible time —
                #        p99 is what actually surfaces that.
            }
        return {"counters": self._counters, "gauges": self._gauges, "histograms": histogram_summary}


def demo_metrics():
    print("\n--- Metrics: counters, gauges, histograms ---")

    metrics = MetricsRegistry()
    for _ in range(50):
        metrics.increment("http_requests_total")
        latency = random.uniform(0.01, 0.05)
        if random.random() < 0.05:
            latency += random.uniform(0.3, 0.8)   # simulate an occasional slow request
        metrics.observe("request_duration_seconds", latency)
    metrics.increment("http_requests_total", by=0)   # counters can be incremented by more than 1 too
    metrics.set_gauge("active_connections", 12)

    summary = metrics.summary()
    print("counters:", summary["counters"])
    print("gauges:  ", summary["gauges"])
    h = summary["histograms"]["request_duration_seconds"]
    print(f"latency  -> avg={h['avg']:.3f}s  p50={h['p50']:.3f}s  p99={h['p99']:.3f}s  (n={h['count']})")
    print("Notice p99 >> avg — that's the occasional slow request an average alone would hide.")
    # In a real app: a route decorated to call metrics.increment()/.observe()
    # on every request, exposed at GET /metrics in Prometheus's text format,
    # scraped periodically by a Prometheus server, graphed in Grafana.


# ---------------------------------------------------------------------------
# Distributed Tracing — correlating ONE request across multiple services
# ---------------------------------------------------------------------------
class TraceContext:
    """A stand-in for what OpenTelemetry (the real, vendor-neutral standard
    for this) hands you automatically, per request."""
    def __init__(self, trace_id: str | None = None, parent_span_id: str | None = None):
        self.trace_id = trace_id or uuid.uuid4().hex[:16]
        # New words in this line:
        #   uuid.uuid4()  -> generates a random, effectively-unique 128-bit
        #        id — used here as a trace id, since it needs to stay
        #        distinct across every request the whole system handles,
        #        potentially from many machines at once
        #   .hex[:16]      -> the id as a hex string, trimmed to 16
        #        characters purely so the printed output below stays readable
        self.parent_span_id = parent_span_id

    def child_span(self) -> "TraceContext":
        # New words in this line:
        #   "TraceContext" (quoted return type)  -> same forward-reference
        #        idea as 04_software_architecture.py's Money.add() — needed
        #        because TraceContext refers to its OWN type before its own
        #        class body has finished being defined
        return TraceContext(trace_id=self.trace_id, parent_span_id=uuid.uuid4().hex[:8])
        # New words in this line:
        #   child_span()  -> the SAME trace_id (this whole request is still
        #        one story), but a NEW span_id — a "span" is one HOP within
        #        that story (one service's piece of the work). This is how
        #        five separate services, logging independently, can later be
        #        reassembled into one connected timeline: they all share a
        #        trace_id, and each span's parent_span_id says which hop
        #        called it.


def call_database(ctx: TraceContext):
    span_id = uuid.uuid4().hex[:8]
    print(f"  [trace={ctx.trace_id} span={span_id} parent={ctx.parent_span_id}] querying database...")
    time.sleep(0.01)


def call_payment_service(ctx: TraceContext):
    span_id = uuid.uuid4().hex[:8]
    print(f"  [trace={ctx.trace_id} span={span_id} parent={ctx.parent_span_id}] charging card...")
    time.sleep(0.01)


def handle_checkout_request():
    root_ctx = TraceContext()   # a brand-new trace_id: this is where the story begins
    print(f"[trace={root_ctx.trace_id}] received checkout request")
    call_database(root_ctx.child_span())
    call_payment_service(root_ctx.child_span())


def demo_tracing():
    print("\n--- Distributed Tracing ---")
    handle_checkout_request()
    print("""
In a REAL distributed system, call_database() and call_payment_service()
would be separate services on separate machines — the trace_id travels
between them inside an HTTP header (the W3C "traceparent" header is the
actual standard), not as a plain function argument like this simplified
demo. A tracing backend (Jaeger, Honeycomb, Datadog APM) then groups every
span sharing one trace_id into a single connected timeline, so "why was
this ONE checkout slow?" doesn't mean manually cross-referencing
timestamps across five different services' independent log files by hand.
""")


# ---------------------------------------------------------------------------
# SLIs, SLOs, and Error Budgets
# ---------------------------------------------------------------------------
def demo_slo_and_error_budget():
    print("\n--- SLIs, SLOs, and Error Budgets ---")
    print("""
SLI (Service Level Indicator) - an actual MEASURED number, e.g. "99.94% of
    requests succeeded this month" — this comes straight from the metrics
    covered above.
SLO (Service Level Objective)  - the TARGET you commit to internally, e.g.
    "99.9% success rate over any 30-day window."
SLA (Service Level Agreement)  - an SLO with a CONTRACTUAL consequence
    attached if you miss it (a refund, a credit) — usually only exists
    with external paying customers; most internal services have SLOs, not SLAs.
""")

    total_requests = 1_000_000
    slo_target = 0.999
    allowed_failures = total_requests * (1 - slo_target)
    print(f"error budget for a {slo_target:.1%} SLO across {total_requests:,} requests: "
          f"{allowed_failures:.0f} failures allowed")

    failures_so_far = 750
    budget_remaining_pct = (1 - failures_so_far / allowed_failures) * 100
    print(f"if {failures_so_far} failures have already happened this month: "
          f"{budget_remaining_pct:.0f}% of the error budget remains")
    print("""
The payoff: "can we ship this risky feature this week?" stops being a vibe
and becomes a number. Burned through 90% of this month's error budget
already? That's a concrete, quantified reason to freeze risky changes and
stabilize — not a hunch, and not something one engineer has to argue for
from authority alone.
""")


# ---------------------------------------------------------------------------
# Alerting: symptom-based vs. cause-based, avoiding pager fatigue
# ---------------------------------------------------------------------------
def demo_alerting_notes():
    print("\n--- Alerting ---")
    print("""
Symptom-based alert: "error rate > 5% for 5 minutes" — fires on USER-VISIBLE
    impact. This is what should page a human at 3am: something is actually
    broken for real users, right now.

Cause-based alert: "CPU > 90%" — fires on a possible CONTRIBUTING factor,
    not confirmed impact. High CPU with normal error rates and normal
    latency might be totally fine (the system doing its job under load).
    Useful as a DASHBOARD signal or a low-urgency ticket, not a page.

Rule of thumb: page a human ONLY for things a human must act on RIGHT NOW.
Everything else goes to a dashboard, or a ticket reviewed during business
hours — not someone's phone at 3am.

Why this matters more than it sounds like it should: a system that pages
for "disk at 80%, still 3 days from actually filling up" trains the humans
on-call to treat pages as noise. The first time that happens, they start
silencing/ignoring alerts on instinct — which means the NEXT page, for a
real, currently-broken production incident, gets the same "eh, probably
fine" reaction. Alert fatigue doesn't just cost sleep, it actively
degrades response time to the incidents that matter.
""")


if __name__ == "__main__":
    demo_three_pillars()
    demo_metrics()
    demo_tracing()
    demo_slo_and_error_budget()
    demo_alerting_notes()
