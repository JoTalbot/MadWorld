import concurrent.futures
import sys
import time
import urllib.request

host = sys.argv[1]
duration = int(sys.argv[2])
workers = int(sys.argv[3])
url = f"http://{host}:8000/health/ready"
end = time.monotonic() + duration
latencies = []
errors = 0

def one():
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            response.read()
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status}")
        return (time.perf_counter() - start) * 1000, None
    except Exception as exc:
        return None, str(exc)

with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
    while time.monotonic() < end:
        batch = list(pool.map(lambda _: one(), range(workers)))
        for latency, error in batch:
            if error is None:
                latencies.append(latency)
            else:
                errors += 1

total = len(latencies) + errors
latencies.sort()
def pct(p):
    if not latencies:
        return None
    index = int((len(latencies) - 1) * p / 100)
    return round(latencies[index], 3)

print(f"CAPACITY_REQUESTS={total}")
print(f"CAPACITY_SUCCESS={len(latencies)}")
print(f"CAPACITY_ERRORS={errors}")
print(f"CAPACITY_RPS={total/duration:.3f}")
print(f"LATENCY_P50_MS={pct(50)}")
print(f"LATENCY_P95_MS={pct(95)}")
print(f"LATENCY_P99_MS={pct(99)}")
print(f"ERROR_RATE={errors/total if total else 1:.6f}")
