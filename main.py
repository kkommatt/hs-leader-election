import threading
import queue
import time
import random
import logging

# =====================================
# Logging configuration
# =====================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(message)s",
    datefmt="%H:%M:%S"
)


# =====================================
# Message class
# =====================================
class Message:
    def __init__(self, origin_id, direction, phase, distance, returning=False):
        self.origin_id = origin_id
        self.direction = direction  # 'LEFT' or 'RIGHT'
        self.phase = phase
        self.distance = distance
        self.returning = returning


# =====================================
# Process (Node) class
# =====================================
class Process(threading.Thread):
    def __init__(self, pid, ring_size, stop_event):
        super().__init__(name=f"Process-{pid}")
        self.pid = pid
        self.phase = 0
        self.active = True

        self.left_queue = None
        self.right_queue = None
        self.inbox = queue.Queue()

        self.confirm_left = False
        self.confirm_right = False

        self.running = True
        self.message_counter = 0

        # Only for termination detection (simulation purpose)
        self.ring_size = ring_size
        self.stop_event = stop_event

    def send(self, q, msg):
        q.put(msg)
        self.message_counter += 1
        logging.info(
            f"SEND → {msg.origin_id} | dir={msg.direction} | "
            f"phase={msg.phase} | dist={msg.distance} | returning={msg.returning}"
        )

    def start_phase(self):
        distance = 2 ** self.phase
        logging.info(f"START PHASE {self.phase} (radius={distance})")

        self.send(
            self.left_queue,
            Message(self.pid, "LEFT", self.phase, distance)
        )
        self.send(
            self.right_queue,
            Message(self.pid, "RIGHT", self.phase, distance)
        )

    def handle_message(self, msg):
        logging.info(
            f"RECEIVED ← {msg.origin_id} | dir={msg.direction} | "
            f"phase={msg.phase} | dist={msg.distance} | returning={msg.returning}"
        )

        # Kill smaller ID
        if not msg.returning and msg.origin_id < self.pid:
            logging.info(f"KILL message from {msg.origin_id} (smaller ID)")
            return

        # Confirmation returned to origin
        if msg.origin_id == self.pid and msg.returning:
            if msg.direction == "LEFT":
                self.confirm_left = True
            else:
                self.confirm_right = True

            logging.info("CONFIRMATION received")

            if self.confirm_left and self.confirm_right:
                radius = 2 ** self.phase

                # ===== TERMINATION CONDITION (FIX) =====
                if radius >= self.ring_size:
                    logging.info("RADIUS COVERS ENTIRE RING")
                    logging.info(f"LEADER ELECTED → {self.pid}")
                    self.stop_event.set()
                    self.running = False
                    return

                # Continue to next phase
                self.phase += 1
                self.confirm_left = False
                self.confirm_right = False
                self.start_phase()
            return

        # Forward message
        if not msg.returning:
            msg.distance -= 1
            if msg.distance == 0:
                msg.returning = True

        # Choose direction
        if msg.direction == "LEFT":
            target = self.right_queue if msg.returning else self.left_queue
        else:
            target = self.left_queue if msg.returning else self.right_queue

        self.send(target, msg)

    def run(self):
        time.sleep(random.uniform(0.1, 0.5))
        self.start_phase()

        while self.running and not self.stop_event.is_set():
            try:
                msg = self.inbox.get(timeout=0.5)
                self.handle_message(msg)
            except queue.Empty:
                pass

            time.sleep(random.uniform(0.05, 0.2))


# =====================================
# Network setup
# =====================================
def connect_ring(processes):
    n = len(processes)
    for i, p in enumerate(processes):
        left = processes[(i - 1) % n]
        right = processes[(i + 1) % n]

        p.left_queue = left.inbox
        p.right_queue = right.inbox


# =====================================
# Main execution
# =====================================
def main():
    print("\nHirschberg–Sinclair leader election\n")

    # ---------- N ----------
    while True:
        try:
            N = int(input("Enter number of processes N (>=2): "))
            if N < 2:
                print("N must be at least 2.")
                continue
            break
        except ValueError:
            print("Please enter a valid integer.")

    # ---------- random or manual ----------
    while True:
        choice = input("Generate random IDs? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            break
        print("Please enter 'y' or 'n'.")

    # ---------- IDs ----------
    if choice == "y":
        ids = random.sample(range(1, 10000), N)
    else:
        ids = []
        print("Enter unique positive integer IDs:")
        while len(ids) < N:
            try:
                pid = int(input(f"ID for process {len(ids)}: "))
                if pid <= 0:
                    print("ID must be positive.")
                    continue
                if pid in ids:
                    print("ID must be unique.")
                    continue
                ids.append(pid)
            except ValueError:
                print("Please enter a valid integer.")

    print("\nRing order (clockwise):")
    print(ids, "\n")

    # ---------- start simulation ----------
    stop_event = threading.Event()

    processes = [Process(pid, N, stop_event) for pid in ids]
    connect_ring(processes)

    for p in processes:
        p.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...\n")
        stop_event.set()

    for p in processes:
        p.running = False
        p.join()

    total_messages = sum(p.message_counter for p in processes)
    print(f"\nTotal messages sent: {total_messages}")


if __name__ == "__main__":
    main()
