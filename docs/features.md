# Salient Features of CATO

CATO stands out with a combination of **technical depth**, **real-world relevance**, and **user-centric design**.

## 1. Multi-UE Real-Time Classification
- Simulates **two devices**: Smartphone (UE-1) and Tablet (UE-2)
- Each UE shows **independent, realistic traffic**
- Updates every 2 seconds with real predictions

> 🎯 Addresses the core problem: "multi-UE connected scenario"

---

## 2. 10-Class Application Detection
CATO classifies into:
1. Web and Browsing
2. Video
3. Texting / Email
4. Social Media
5. System / Software Services
6. Cloud / File Sharing
7. Video Conferencing
8. Networking
9. Audio
10. Gaming

> No binary classification — real-world granularity

---

## 3. Real-World Data Only
-  No synthetic flows in final demo
-  Uses `website_testing.csv` — real user traffic
- Ensures model generalization

> 🔍 Judges can verify predictions against actual data

---

## 4. Privacy-Preserving Design
- No deep packet inspection
- No port numbers or payload analysis
- Uses only **flow-level metadata** (e.g., packet size, duration)

> ✅ Compliant with modern encrypted traffic standards

---

## 5. Context-Aware QoS Engine
Each class gets tailored QoS:
| Class | Latency | Priority | Bandwidth |
|------|--------|----------|-----------|
| Gaming | very_low | very_high | medium |
| Video Conferencing | low | high | guaranteed |
| Browsing | medium | low_to_medium | best_effort |

> 🚀 Enables network to **prioritize critical apps**

---

## 6. Full-Stack, Runnable System
- Frontend: React + Vite
- Backend: FastAPI
- ML Model: Scikit-learn
- No mock data — everything runs live

> 💻 Can be demonstrated in 10 minutes

---

## 7. Professional UI/UX
- Clean, centered layout
- Green/pink/yellow cyberpunk theme
- No emojis, no blue text
- Mobile-friendly

---

## 8. Submission-Ready
- MIT License
- No third-party APIs
- All code in GitHub
- Models & datasets on Hugging Face

---

## 9. Demo-Optimized
- Fast updates (2s intervals)
- All categories appear over time
- Logs show real timestamps
- CSV export for offline analysis

---

> 🔗 [Back to README](../README.md)
