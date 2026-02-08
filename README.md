**# Hirschberg–Sinclair Leader Election Algorithm

This repository contains a Python implementation of the **Hirschberg–Sinclair (HS) leader election algorithm** for a distributed system with a **ring topology**.

The implementation simulates a real distributed environment using **threads and message queues**, providing detailed logs of every step of the algorithm.

---

## Problem Description

**Goal:**  
Elect a single leader in a distributed ring network where:

- Each process has a **unique identifier (ID)**
- Processes do **not know the total number of processes (N)**
- Communication is possible in **both directions** (left and right)
- The system may be **asynchronous**

The Hirschberg–Sinclair algorithm improves message complexity compared to simple leader election algorithms by working in **phases with exponentially increasing radius**.

---

## Algorithm Overview (Hirschberg–Sinclair)

- The algorithm runs in phases `k = 0, 1, 2, ...`
- In phase `k`, each active process sends its ID:
  - to the left and right
  - up to distance `2^k`
- Message handling rules:
  - A message with a **smaller ID** is killed
  - A message with a **larger ID** is forwarded
  - If a process receives its **own ID back from both directions**, it proceeds to the next phase
- Eventually, only the process with the **maximum ID** survives and becomes the leader

**Message complexity:** `O(N log N)`  
**Time complexity:** `O(log N)` phases (under synchronous assumptions)

---

## Implementation Details

- **Language:** Python 3
- **Concurrency model:** `threading.Thread`
- **Communication:** `queue.Queue` (simulating pipes/channels)
- **Topology:** Ring
- **Synchronization:** Asynchronous (random delays per process)
- **Logging:** Detailed logs for:
  - message sending
  - message receiving
  - message killing
  - phase transitions
  - confirmations

Each process:
- runs in its own thread
- knows only its left and right neighbors
- has no global knowledge of the network

---

## How to Run

## 1. Clone the repository
```bash
git clone https://github.com/kkommatt/hs-leader-election.git
cd hs-leader-election
````
## 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
````

## 3. Run the simulation

```bash
python main.py
```

---

## Input

* Number of processes `N`
* Choice of:

  * random unique IDs
  * or manual ID input

---

## Output

* Detailed execution logs (real-time)
* Total number of messages sent
* Clear demonstration of leader election behavior

### Example log output:

```
SEND → 42 | dir=LEFT | phase=1 | dist=2 | returning=False
RECEIVED ← 42 | dir=LEFT | phase=1 | dist=1 | returning=False
KILL message from 17 (smaller ID)
START PHASE 2 (radius=4)
```

---

## License

This project is intended for educational use

