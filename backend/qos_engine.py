"""
QoS Engine: Maps traffic class to QoS policy.
"""

from typing import Dict

QOS_PROFILES: Dict[str, Dict[str, str]] = {
    "Real-Time": {
        "latency": "low",
        "jitter": "low",
        "priority": "high",
        "bandwidth": "guaranteed"
    },
    "Non-Real-Time": {
        "latency": "medium_to_high",
        "jitter": "medium",
        "priority": "low_to_medium",
        "bandwidth": "best_effort"
    }
}

def _normalize(label: str) -> str:
    key = label.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    if key in {"realtime", "realtimes", "rt"}:
        return "Real-Time"
    return "Non-Real-Time"

def get_qos_for_label(label: str) -> Dict[str, str]:
    return QOS_PROFILES[_normalize(label)]

def get_all_qos() -> Dict[str, Dict[str, str]]:
    return QOS_PROFILES.copy()