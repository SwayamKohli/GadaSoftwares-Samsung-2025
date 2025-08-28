"""
QoS Engine: Maps multi-class traffic to QoS policies.
"""

from typing import Dict

QOS_PROFILES: Dict[str, Dict[str, str]] = {
    "Web and Browsing": {
        "latency": "medium",
        "jitter": "medium",
        "priority": "low_to_medium",
        "bandwidth": "best_effort"
    },
    "Video": {
        "latency": "medium",
        "jitter": "medium",
        "priority": "medium",
        "bandwidth": "high"
    },
    "Texting / Email": {
        "latency": "high",
        "jitter": "high",
        "priority": "low",
        "bandwidth": "low"
    },
    "Social Media": {
        "latency": "medium",
        "jitter": "medium",
        "priority": "medium",
        "bandwidth": "medium"
    },
    "System / Software Services": {
        "latency": "low",
        "jitter": "low",
        "priority": "high",
        "bandwidth": "low"
    },
    "Cloud / File Sharing": {
        "latency": "high",
        "jitter": "high",
        "priority": "low",
        "bandwidth": "high"
    },
    "Video Conferencing": {
        "latency": "low",
        "jitter": "low",
        "priority": "high",
        "bandwidth": "guaranteed"
    },
    "Networking": {
        "latency": "low",
        "jitter": "low",
        "priority": "high",
        "bandwidth": "low"
    },
    "Audio": {
        "latency": "low",
        "jitter": "low",
        "priority": "high",
        "bandwidth": "medium"
    },
    "Gaming": {
        "latency": "very_low",
        "jitter": "very_low",
        "priority": "very_high",
        "bandwidth": "medium"
    }
}

def get_qos_for_label(label: str) -> Dict[str, str]:
    normalized = label.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    
    mapping = {
        "webandbrowsing": "Web and Browsing",
        "video": "Video",
        "texting/email": "Texting / Email",
        "textingemail": "Texting / Email",
        "socialmedia": "Social Media",
        "system/software": "System / Software Services",
        "systemsoftware": "System / Software Services",
        "cloudfilesharing": "Cloud / File Sharing",
        "cloudfiling": "Cloud / File Sharing",
        "videoconferencing": "Video Conferencing",
        "networking": "Networking",
        "audio": "Audio",
        "gaming": "Gaming"
    }
    
    key = mapping.get(normalized, label)
    return QOS_PROFILES.get(key, {
        "latency": "medium",
        "jitter": "medium",
        "priority": "medium",
        "bandwidth": "best_effort"
    })

def get_all_qos() -> Dict[str, Dict[str, str]]:
    return QOS_PROFILES.copy()