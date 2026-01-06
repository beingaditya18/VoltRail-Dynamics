# VoltRail Dynamics: Hybrid Fleet Optimization Engine

VoltRail Dynamics is a full-stack industrial logistics platform designed to manage real-time telemetry and optimize stabling/induction for hybrid trainsets. It features a high-concurrency Flask backend with a decoupled service architecture and a reactive dashboard built with React and Tailwind CSS.



##  Key Features

* **Asynchronous Optimization**: Trigger complex induction algorithms via a non-blocking Job Queue (UUID-tracked).
* **Real-time Telemetry**: Monitoring of mileage, delay status, and stabling bay logistics.
* **Enterprise Patterns**: Implements Singleton Repository and Service Layer patterns for high maintainability.
* **Reactive UI**: A modern React dashboard featuring custom hooks for API polling and live status updates.
* **Heuristic Solver**: A weighted-sum optimization engine for balancing shunt costs, maintenance hours, and stabling capacity.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | React 18, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.10+, Flask, UUID Management |
| **Data Handling** | Singleton Repository Pattern |
| **State Management** | Custom React Hooks + Polling Logic |

---

##  Architecture

The system is built on the **Separation of Concerns** principle:

1.  **The Repository Layer**: Manages the in-memory state of the fleet (simulating a high-performance cache or DB).
2.  **The Service Layer**: Handles the business logic and the hand-off to the optimization solver.
3.  **The Controller (API) Layer**: Purely RESTful endpoints returning standardized JSON responses.
4.  **The Frontend Hook**: A polling mechanism that tracks the lifecycle of an optimization job from `PENDING` to `SUCCESS`.



##  Getting Started

### 1. Backend Setup
bash
cd backend
pip install flask flask-cors
python app.py
