from __future__ import annotations
import numpy as np
from typing import List, Dict


FEATURE_ORDER = [
    "duration_s",
    "packets",
    "bytes",
    "avg_pkt_size",
    "flow_iat_mean_ms",
    "flow_iat_std_ms",
    "burstiness",
    "down_up_ratio",
    "protocol_udp",   # 1 for UDP, 0 otherwise
    "dport",          # destination port
]


def generate_flows(n: int = 50, seed: int = 42) -> List[Dict[str, float]]:
    rng = np.random.default_rng(seed)
    flows: List[Dict[str, float]] = []

    for _ in range(n):
        is_rt = rng.uniform() < 0.5

        if is_rt:
            # Real-time-ish: small packets, higher packet rate, low IAT & jitter
            duration_s = rng.uniform(1, 60)
            packets = rng.integers(200, 1200)
            avg_pkt_size = rng.uniform(60, 300)
            bytes_ = packets * avg_pkt_size
            flow_iat_mean_ms = rng.uniform(1, 15)
            flow_iat_std_ms = rng.uniform(0.5, 5)
            burstiness = rng.uniform(0.05, 0.3)
            down_up_ratio = rng.uniform(0.6, 1.6)
            protocol_udp = 1
            dport = int(rng.choice([5060, 3478, 16384, 5004, 4000]))
            label = "Real-Time"
        else:
            # Non-real-time-ish: larger packets, bursty, higher IAT & jitter
            duration_s = rng.uniform(5, 1800)
            packets = rng.integers(20, 3000)
            avg_pkt_size = rng.uniform(400, 1400)
            bytes_ = packets * avg_pkt_size
            flow_iat_mean_ms = rng.uniform(20, 500)
            flow_iat_std_ms = rng.uniform(10, 300)
            burstiness = rng.uniform(0.3, 1.0)
            down_up_ratio = rng.uniform(1.0, 5.0)
            protocol_udp = 0
            dport = int(rng.choice([80, 443, 21, 22, 25, 8080]))
            label = "Non-Real-Time"

        flows.append({
            "label": label,
            "features": {
                "duration_s": float(duration_s),
                "packets": int(packets),
                "bytes": float(bytes_),
                "avg_pkt_size": float(avg_pkt_size),
                "flow_iat_mean_ms": float(flow_iat_mean_ms),
                "flow_iat_std_ms": float(flow_iat_std_ms),
                "burstiness": float(burstiness),
                "down_up_ratio": float(down_up_ratio),
                "protocol_udp": int(protocol_udp),
                "dport": int(dport),
            }
        })

    return flows
