# Samsung EnnovateX 2025 AI Challenge Submission

**Problem Statement** - Classify User Application Traffic at the Network in a Multi-UE Connected Scenario

**Team name** - GadaSoftwares

**Team members (Names)** - [Swayam Kohli (Leader)](https://github.com/SwayamKohli), [Mahak Singh](https://github.com/Mahak0205), [Archit Sahay](https://github.com/arcfr), [Maitreyi Jha](https://github.com/Maitreyi-Jha)

**Demo Video Link** - [https://youtu.be/wdI0Zr8693M](https://youtu.be/wdI0Zr8693M)

---

## Project Artefacts

### Technical Documentation
All technical details are in the `docs/` folder:
- `approach.md`: Solution approach and novelty
- `architecture.md`: System architecture and component flow
- `installation.md`: Step-by-step setup guide
- `user_guide.md`: Dashboard navigation and interaction
- `features.md`: Key features and screenshots

### Source Code
The complete project source code is in the `src/` folder:
- `src/backend/`: FastAPI server, ML inference, QoS engine
- `src/frontend/`: React + Vite dashboard, real-time UI, multi-UE monitoring

### Models Used
None (we used only self-developed models)

### Models Published
- **CATO Multi-Class Traffic Classifier**  
  🤗 [https://huggingface.co/ArcFR/Network_Traffic_Classifer/tree/main](https://huggingface.co/ArcFR/Network_Traffic_Classifer/tree/main)

### Datasets Used
- `Samsung_dataset.csv` – Public dataset provided for training (used internally)
- `website_testing.csv` – Real-world encrypted traffic flows for testing
- 🔗 https://www.kaggle.com/datasets/jsrojas/ip-network-traffic-flows-labeled-with-87-apps
- 🔗 https://www.kaggle.com/datasets/kimdaegyeom/5g-traffic-datasets/data

### Attribution
This project was built entirely from scratch during the hackathon. No existing open-source project was used as a base. All components — including the machine learning model, QoS engine, backend API, and frontend dashboard — were developed in-house by Team GadaSoftware.

The solution strictly uses:
- Open-source libraries (MIT/Apache 2.0 licensed): scikit-learn, FastAPI, React, Vite
- Public datasets: `Samsung_dataset.csv`, `website_testing.csv`
- Self-developed code and models

No third-party APIs, cloud services, or proprietary tools were used.
