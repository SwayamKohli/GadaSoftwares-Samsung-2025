"""
Generate synthetic flow data with features matching the trained model.
"""

import numpy as np
from typing import List, Dict, Any
import random

FEATURE_NAMES = [
    'Source.Port',
    'Destination.Port',
    'Flow.Duration',
    'Total.Fwd.Packets',
    'Total.Backward.Packets',
    'Flow.Packets.s',
    'Fwd.Packet.Length.Max',
    'Flow.IAT.Max',
    'Bwd.Packet.Length.Max',
    'Init_Win_bytes_forward',
    'Init_Win_bytes_backward',
    'Timestamp_Formatted'
]

# Common ports
WEB_PORTS = [80, 443, 8080]
VOIP_PORTS = [5060, 5061]
MEDIA_PORTS = [1935, 8081, 554]  # RTMP, RTSP
GAMING_PORTS = [3074, 27015, 3478]  # Xbox, Steam, STUN
EMAIL_PORTS = [25, 465, 587, 110, 995, 143, 993]


def generate_flow(is_real_time: bool, seed: int = None) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)

    if is_real_time:
        # Real-Time: VoIP, Gaming, Video Calls
        dest_port = random.choice(VOIP_PORTS + GAMING_PORTS + [1935])
        flow_duration = rng.uniform(1, 120)  # short to medium
        fwd_packets = rng.integers(5, 500)
        bwd_packets = rng.integers(5, 500)
        flow_packets_s = (fwd_packets + bwd_packets) / flow_duration
        fwd_pkt_max = rng.uniform(60, 500)
        bwd_pkt_max = rng.uniform(60, 500)
        flow_iat_max = rng.uniform(1, 50)  # low max IAT
        init_win_fwd = rng.integers(2000, 32768)
        init_win_bwd = rng.integers(2000, 32768)
        label = "Real-Time"
    else:
        # Non-Real-Time: Browsing, Email, Streaming, Reels
        dest_port = random.choice(WEB_PORTS + EMAIL_PORTS + [8080])
        flow_duration = rng.uniform(10, 1800)  # longer
        fwd_packets = rng.integers(10, 2000)
        bwd_packets = rng.integers(5, 1000)
        flow_packets_s = (fwd_packets + bwd_packets) / flow_duration
        fwd_pkt_max = rng.uniform(400, 1500)
        bwd_pkt_max = rng.uniform(60, 1400)
        flow_iat_max = rng.uniform(50, 2000)  # higher max IAT
        init_win_fwd = rng.integers(4000, 65535)
        init_win_bwd = rng.integers(4000, 65535)
        label = "Non-Real-Time"

    # Random source port
    src_port = rng.integers(1024, 65535)

    # Current timestamp
    timestamp = 1672531200 + rng.integers(0, 3600 * 24 * 30)  # ~30 days

    features = {
        'Source.Port': int(src_port),
        'Destination.Port': int(dest_port),
        'Flow.Duration': float(flow_duration),
        'Total.Fwd.Packets': int(fwd_packets),
        'Total.Backward.Packets': int(bwd_packets),
        'Flow.Packets.s': float(flow_packets_s),
        'Fwd.Packet.Length.Max': float(fwd_pkt_max),
        'Flow.IAT.Max': float(flow_iat_max),
        'Bwd.Packet.Length.Max': float(bwd_pkt_max),
        'Init_Win_bytes_forward': int(init_win_fwd),
        'Init_Win_bytes_backward': int(init_win_bwd),
        'Timestamp_Formatted': int(timestamp)
    }

    return {
        "label": label,
        "features": features
    }


def generate_flows(n: int = 20, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate n synthetic flows, balanced between Real-Time and Non-Real-Time.
    """
    rng = np.random.default_rng(seed)
    flows = []

    for i in range(n):
        is_rt = rng.choice([True, False])  # Balanced
        flow = generate_flow(is_rt, seed=seed + i)
        flows.append(flow)

    return flows