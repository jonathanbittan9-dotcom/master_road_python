"""
11_system_design.py

Section 11: System Design
    - Rate limiting at scale (token bucket)
    - LRU cache (bounded memory, evicts least-recently-used)
    - Retry with exponential backoff
    - Circuit breaker (fail fast instead of hammering a dead dependency)
    - Capacity estimation (notes)

These are small, runnable versions of concepts that show up in real
system design interviews and real production incidents alike.

Run: python 11_system_design.py
"""

import random
import time
from collections import OrderedDict


# ---------------------------------------------------------------------------
# Token Bucket rate limiter — smoother than the fixed-window limiter in
# 09_security.py, allows brief bursts without allowing sustained abuse
# ---------------------------------------------------------------------------
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate   # tokens added per second
        self.last_refill = time.time()

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        # New words in this line:
        #   min(a, b)  -> built-in function: returns the SMALLER of its
        #        arguments — used here as a "cap": the bucket can refill,
        #        but never past its own capacity
        self.last_refill = now

    def allow(self) -> bool:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


def demo_token_bucket():
    print("\n--- Token Bucket Rate Limiter ---")
    bucket = TokenBucket(capacity=3, refill_rate=1)   # 3 burst, refills 1/sec

    for i in range(5):
        print(f"request {i + 1}: {'allowed' if bucket.allow() else 'BLOCKED'}")
    print("(waiting 1s for a token to refill...)")
    time.sleep(1)
    print(f"request 6: {'allowed' if bucket.allow() else 'BLOCKED'}")


# ---------------------------------------------------------------------------
# LRU Cache — bounded size, evicts the least-recently-used entry
# ---------------------------------------------------------------------------
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._store = OrderedDict()
        # New words in this line:
        #   OrderedDict()  -> a dict that remembers INSERTION order (regular
        #        dicts do too, since Python 3.7, but OrderedDict adds extra
        #        methods for REORDERING, used below) and lets you move
        #        entries around

    def get(self, key):
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        # New words in this line:
        #   .move_to_end(key)  -> moves that key to t+he END of the
        #        ordering, without changing its value. Used here to mean
        #        "this was just used, so it's no longer the
        #        least-recently-used entry."
        return self._store[key]

    def put(self, key, value):
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = value
        if len(self._store) > self.capacity:
            evicted_key, _ = self._store.popitem(last=False)
            # New words in this line:
            #   .popitem(last=False)  -> removes and returns the FIRST
            #        (oldest) item instead of the default last=True (most
            #        recent). Since .move_to_end() keeps recently-used keys
            #        at the end, the item still at the front is, by
            #        definition, the least recently used.
            print(f"  evicted: {evicted_key}")


def demo_lru_cache():
    print("\n--- LRU Cache ---")

    cache = LRUCache(capacity=3)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    cache.get("a")          # "a" is now most-recently-used
    cache.put("d", 4)       # capacity exceeded -> evicts "b" (least recently used)

    for key in ["a", "b", "c", "d"]:
        print(f"{key}: {cache.get(key)}")
    # Python's functools.lru_cache decorator does this automatically for
    # function results — worth knowing this is what's happening underneath.


# ---------------------------------------------------------------------------
# Retry with exponential backoff
# ---------------------------------------------------------------------------
def unreliable_call(success_on_attempt: int, attempt_counter: list):
    attempt_counter[0] += 1
    if attempt_counter[0] < success_on_attempt:
        raise ConnectionError(f"simulated failure on attempt {attempt_counter[0]}")
    return "success"


def retry_with_backoff(fn, max_attempts=5, base_delay=0.1):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except ConnectionError as e:
            if attempt == max_attempts:
                raise
                # New words in this line:
                #   raise (with no exception after it)  -> re-raises
                #        whichever exception is currently being handled — used
                #        here to give up and let the caller see the failure once
                #        max_attempts is reached, instead of retrying forever
            delay = base_delay * (2 ** (attempt - 1))   # 0.1s, 0.2s, 0.4s, 0.8s...
            jitter = random.uniform(0, delay * 0.1)
            # New words in this line:
            #   random.uniform(a, b)  -> a random FLOAT between a and b
            #        (vs. random.randint from testlearn.py, which only
            #        produces whole-number integers). Adding a little
            #        randomness ("jitter") avoids many clients retrying in lockstep
            print(f"  attempt {attempt} failed ({e}), retrying in {delay + jitter:.2f}s")
            time.sleep(delay + jitter)


def demo_retry_backoff():
    print("\n--- Retry with Exponential Backoff ---")
    counter = [0]
    result = retry_with_backoff(lambda: unreliable_call(success_on_attempt=3, attempt_counter=counter))
    print("final result:", result)


# ---------------------------------------------------------------------------
# Circuit Breaker — stop hammering a dependency that's already down
# ---------------------------------------------------------------------------
class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, failure_threshold=3, recovery_timeout=1.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = self.CLOSED
        self.opened_at = None

    def call(self, fn):
        if self.state == self.OPEN:
            if time.time() - self.opened_at >= self.recovery_timeout:
                self.state = self.HALF_OPEN   # try one test request
            else:
                raise RuntimeError("circuit OPEN — failing fast without calling the dependency")

        try:
            result = fn()
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = self.OPEN
                self.opened_at = time.time()
            raise
        else:
            # New words in this line:
            #   else (on a try block)  -> runs ONLY if the try block finished
            #        with NO exception at all — different from `finally`
            #        (core_language_mastery.py), which runs regardless.
            #        Here it means "only reset failure tracking if the call
            #        actually succeeded."
            self.failures = 0
            self.state = self.CLOSED
            return result


def demo_circuit_breaker():
    print("\n--- Circuit Breaker ---")

    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.3)

    def always_fails():
        raise ConnectionError("downstream service is down")

    for i in range(4):
        try:
            breaker.call(always_fails)
        except ConnectionError:
            print(f"call {i + 1}: real failure (state={breaker.state})")
        except RuntimeError as e:
            print(f"call {i + 1}: {e} (state={breaker.state})")
    # After failure_threshold real failures, the breaker trips OPEN and
    # subsequent calls fail INSTANTLY without even trying the dependency —
    # this is what protects a struggling downstream service from being
    # hammered by retries while it's trying to recover.


# ---------------------------------------------------------------------------
# Idempotency keys — making retries safe for actions with side effects
# ---------------------------------------------------------------------------
class PaymentProcessor:
    """
    The retry_with_backoff() function above is only safe to retry blindly
    for READ operations. Retrying a PAYMENT is dangerous: if the first
    attempt actually succeeded but the response got lost on the way back
    (network blip), a naive retry charges the customer TWICE for one order.
    """
    def __init__(self):
        self._processed: dict[str, str] = {}   # idempotency_key -> result

    def charge(self, idempotency_key: str, amount: float) -> str:
        if idempotency_key in self._processed:
            # We've seen this EXACT request before — return the same result
            # instead of charging again. The caller can't tell the
            # difference between "first successful attempt" and "safely
            # replayed retry" — which is the whole point.
            return self._processed[idempotency_key] + " (replayed, not re-charged)"

        result = f"Charged ${amount:.2f}"
        self._processed[idempotency_key] = result
        return result


def demo_idempotency_key():
    print("\n--- Idempotency Keys ---")

    processor = PaymentProcessor()
    key = "order-482-attempt"   # in real code: a UUID the CLIENT generates
    # once per logical action, and resends unchanged on every retry of that
    # SAME action — a fresh key would defeat the whole mechanism.

    print("first attempt:", processor.charge(key, 49.99))
    print("network blip -> client retries with the SAME key:")
    print("second attempt:", processor.charge(key, 49.99))
    print("a genuinely NEW order uses a NEW key:")
    print("different order:", processor.charge("order-483-attempt", 19.99))
    # Real APIs (Stripe, for example) implement exactly this: pass an
    # Idempotency-Key header, and the server stores request+response pairs
    # keyed by it for a window of time (e.g. 24h), replaying the stored
    # response for any duplicate instead of re-executing the action.


# ---------------------------------------------------------------------------
# Load balancing strategies (notes — routing traffic across many servers)
# ---------------------------------------------------------------------------
def demo_load_balancing_notes():
    print("\n--- Load Balancing Strategies (notes) ---")
    print("""
A load balancer sits in front of multiple identical server instances and
decides which one handles each incoming request.

Round robin:
    Request 1 -> server A, request 2 -> server B, request 3 -> server C,
    request 4 -> server A again... Simple, and fine when every request
    costs roughly the same amount of work.

Least connections:
    Send each new request to whichever server currently has the FEWEST
    active requests in flight. Better than round robin when request cost
    varies a lot — round robin can't tell it just sent 3 expensive requests
    in a row to the same unlucky server.

Weighted (round robin or least-connections):
    Some servers get proportionally more traffic than others — useful when
    instances aren't identical (a bigger machine can take more), or during
    a canary deploy (see 08_devops/08_deployment_notes.py) where the new
    version should only get a small weighted slice of traffic at first.

IP hash / consistent hashing:
    The SAME client (by IP, session id, or similar) always routes to the
    SAME server, as long as that server stays healthy. Needed for "sticky
    sessions" when server-side state isn't shared across instances (e.g.
    an in-memory cache per server) — this course's TTLCache in
    05_databases.py, if run on multiple servers without a shared Redis
    behind it, is exactly the kind of per-instance state that would need
    this.

This is also what the health_check() route from 08_devops is FOR: a load
balancer only routes to instances that report healthy, tying load
balancing and zero-downtime deploys together.
""")


# ---------------------------------------------------------------------------
# Capacity estimation (notes — pure back-of-envelope math, no code needed)
# ---------------------------------------------------------------------------
def demo_capacity_estimation():
    print("\n--- Capacity Estimation (notes) ---")
    print("""
Example: "How many servers do we need for the leaderboard page?"

  - Assume 10,000 daily active users, each loads the leaderboard ~5x/day
      -> 50,000 requests/day -> ~0.6 req/sec average
  - Traffic isn't flat — assume peak is 10x average -> ~6 req/sec at peak
  - Each request takes ~50ms server time -> one server handles ~20 req/sec
  - 6 req/sec peak comfortably fits on ONE server, with room to spare

This kind of rough math is the actual point of system design interviews —
not perfect precision, but showing you'd catch a 100x miscalculation
before provisioning (or under-provisioning) real infrastructure.
""")


if __name__ == "__main__":
    demo_token_bucket()
    demo_lru_cache()
    demo_retry_backoff()
    demo_circuit_breaker()
    demo_idempotency_key()
    demo_load_balancing_notes()
    demo_capacity_estimation()
