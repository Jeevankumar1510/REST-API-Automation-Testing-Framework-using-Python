"""
Lightweight API Performance & Load Testing Benchmark.
Simulates concurrent user traffic to measure throughput (RPS) and latency percentiles (P50, P95, P99).

Usage:
    python load_test.py
    python load_test.py --concurrency 10 --requests 100 --endpoint /users
"""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import time
from typing import Dict, List, Tuple
import requests

from config.config import settings


def send_request(url: str, headers: Dict[str, str], timeout: float = 5.0) -> Tuple[int, float]:
    """Execute a single HTTP request and record response code and elapsed time in ms."""
    start = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        duration_ms = (time.perf_counter() - start) * 1000
        return response.status_code, duration_ms
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        return 0, duration_ms


def run_load_test(
    endpoint: str = "/users",
    concurrency: int = 10,
    total_requests: int = 100
) -> None:
    """Run concurrent benchmark against specified endpoint."""
    url = f"{settings.BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Accept": "application/json"}

    print("\n" + "=" * 65)
    print("  ⚡ API PERFORMANCE & CONCURRENCY BENCHMARK")
    print("=" * 65)
    print(f"  Target URL:       {url}")
    print(f"  Total Requests:   {total_requests}")
    print(f"  Concurrent Users: {concurrency}")
    print("=" * 65 + "\n")

    latencies: List[float] = []
    status_codes: Dict[int, int] = {}

    start_bench = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(send_request, url, headers)
            for _ in range(total_requests)
        ]
        for f in as_completed(futures):
            status, duration = f.result()
            latencies.append(duration)
            status_codes[status] = status_codes.get(status, 0) + 1

    total_bench_duration = time.perf_counter() - start_bench
    rps = total_requests / total_bench_duration if total_bench_duration > 0 else 0

    sorted_latencies = sorted(latencies)
    avg_latency = statistics.mean(sorted_latencies)
    median_p50 = statistics.median(sorted_latencies)
    p90 = sorted_latencies[int(len(sorted_latencies) * 0.90)]
    p95 = sorted_latencies[int(len(sorted_latencies) * 0.95)]
    p99 = sorted_latencies[min(int(len(sorted_latencies) * 0.99), len(sorted_latencies) - 1)]

    # Print Formatted Results
    print("📊 BENCHMARK METRICS & SLA RESULTS:")
    print("-" * 65)
    print(f"  Total Execution Time:   {total_bench_duration:.2f} seconds")
    print(f"  Throughput (RPS):       {rps:.2f} req/sec")
    print(f"  Minimum Latency:        {sorted_latencies[0]:.2f} ms")
    print(f"  Average Latency:        {avg_latency:.2f} ms")
    print(f"  Median (P50) Latency:   {median_p50:.2f} ms")
    print(f"  90th Percentile (P90):  {p90:.2f} ms")
    print(f"  95th Percentile (P95):  {p95:.2f} ms")
    print(f"  99th Percentile (P99):  {p99:.2f} ms")
    print(f"  Maximum Latency:        {sorted_latencies[-1]:.2f} ms")
    print("-" * 65)
    print("  STATUS CODE BREAKDOWN:")
    for code, count in sorted(status_codes.items()):
        status_name = "200 OK" if code == 200 else f"HTTP {code}"
        print(f"    • {status_name}: {count} responses ({count / total_requests * 100:.1f}%)")
    print("-" * 65)

    # SLA Assessment
    if p95 <= settings.MAX_RESPONSE_TIME_MS:
        print(f"  ✅ SLA VERIFICATION: PASSED (P95 {p95:.2f}ms <= {settings.MAX_RESPONSE_TIME_MS}ms)\n")
    else:
        print(f"  ⚠️  SLA VERIFICATION: FAILED (P95 {p95:.2f}ms > {settings.MAX_RESPONSE_TIME_MS}ms)\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="REST API Concurrency & Load Benchmark")
    parser.add_argument("--endpoint", default="/users", help="Target API endpoint")
    parser.add_argument("--concurrency", type=int, default=10, help="Number of concurrent workers")
    parser.add_argument("--requests", type=int, default=100, help="Total requests to dispatch")

    args = parser.parse_args()
    run_load_test(
        endpoint=args.endpoint,
        concurrency=args.concurrency,
        total_requests=args.requests
    )

