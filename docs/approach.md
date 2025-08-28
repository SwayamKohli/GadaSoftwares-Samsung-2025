# Approach: How CATO Solves Multi-UE Traffic Classification

## Problem Statement
> *"Classify User Application Traffic at the Network in a Multi-UE Connected Scenario"*

Modern networks handle diverse traffic from multiple users (UEs), each running different applications — from video streaming to gaming, browsing to video calls. Without visibility into **application type**, networks cannot apply **differentiated QoS policies**, leading to poor user experience under congestion.

Traditional DPI (Deep Packet Inspection) fails with **encrypted traffic**, and rule-based systems lack adaptability.

## Our Solution: CATO
**CATO (Classification of Application Traffic Online)** is an **AI-powered, privacy-preserving traffic classifier** that:
- Classifies encrypted traffic into **10 real-world application categories**
- Operates in **real-time** using only flow-level metadata
- Recommends **context-aware QoS policies**
- Simulates **multi-UE scenarios** (Smartphone + Tablet)
- Uses **real-world CSV data**, not synthetic flows

### Why This Approach is Unique
| Feature | CATO Advantage |
|--------|----------------|
| **Privacy-Preserving** | No packet payload inspection — only flow features like packet size, duration, rate |
| **Multi-UE Simulation** | Two independent UEs with device-appropriate behavior (gaming on phone, cloud on tablet) |
| **Real-World Testing** | Uses `website_testing.csv` — not synthetic data — ensuring real-world accuracy |
| **End-to-End System** | Full stack: React frontend, FastAPI backend, ML model, QoS engine |
| **Scalable & Edge-Ready** | Lightweight Random Forest model suitable for edge deployment |

### Technical Uniqueness
- **No Port or Payload Analysis**: Uses only 9 flow features (e.g., `Flow.Duration`, `Init_Win_bytes_forward`)
- **Balanced Multi-Class Model**: Trained on `Samsung_dataset.csv`, validated on `website_testing.csv`
- **Dynamic QoS Engine**: Maps each class to tailored policies (latency, jitter, bandwidth)
- **No Overfitting**: Uses `class_weight='balanced'` to handle imbalanced real-world data

This approach ensures **high accuracy**, **low latency**, and **real-world deployability** — exactly what 5G/6G networks need.

> 🔗 [Back to README](../README.md)
