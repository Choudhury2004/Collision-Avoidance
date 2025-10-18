import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# --- 1. SIMULATION PARAMETERS (HIGHER TRAFFIC LOAD) ---
SIMULATION_TIME_MS = 10000
PACKET_TRANSMISSION_TIME_MS = 10
AVG_CAR_ARRIVAL_RATE_PER_HOUR = 30
PROB_EVENT_PER_MS = AVG_CAR_ARRIVAL_RATE_PER_HOUR / (60 * 60 * 1000)

# CSMA/CA specific parameters
DIFS_MS = 2
MAX_BACKOFF_SLOTS = 5

# --- 2. CORE COMPONENT CLASSES ---

class SensorNode:
    """Represents a single parking spot sensor."""
    def __init__(self, id, protocol):
        self.id = id
        self.protocol = protocol
        self.packet_buffer = None  # Holds the packet to be sent
        self.backoff_counter = 0
        self.wait_time = 0 # For CSMA DIFS

    def generate_packet(self):
        """A car arrives or leaves, creating a new packet if buffer is empty."""
        if self.packet_buffer is None and np.random.rand() < PROB_EVENT_PER_MS:
            # Packet is just represented by the time it was generated
            self.packet_buffer = "PacketData"
            return True
        return False

class Channel:
    """Represents the shared wireless channel."""
    def __init__(self):
        self.is_busy = False
        self.transmission_timer = 0

# --- 3. REWRITTEN SIMULATION ENGINE ---

def run_simulation(num_nodes, protocol):
    """Runs a complete simulation with corrected logic."""
    nodes = [SensorNode(i, protocol) for i in range(num_nodes)]
    channel = Channel()

    successful_transmissions = 0
    total_packets_generated = 0

    for t in range(SIMULATION_TIME_MS):
        transmitting_nodes_this_slot = []

        # --- SENSOR LOGIC ---
        for node in nodes:
            # 1. Generate new packets
            if node.generate_packet():
                total_packets_generated += 1

            # 2. Handle backoff counters
            if node.backoff_counter > 0:
                node.backoff_counter -= 1
                continue # Must wait for backoff to finish

            # 3. Attempt to transmit if there's a packet
            if node.packet_buffer is not None:
                if protocol == 'ALOHA':
                    transmitting_nodes_this_slot.append(node)
                
                elif protocol == 'CSMA/CA':
                    if not channel.is_busy:
                        if node.wait_time < DIFS_MS:
                            node.wait_time += 1
                        else: # DIFS wait is over
                            transmitting_nodes_this_slot.append(node)
                    else: # Channel is busy, so backoff
                        node.backoff_counter = np.random.randint(1, MAX_BACKOFF_SLOTS + 1)

        # --- CHANNEL LOGIC ---
        # Update channel busy state
        if channel.transmission_timer > 0:
            channel.transmission_timer -= 1
        channel.is_busy = channel.transmission_timer > 0

        # Check for transmissions and collisions
        num_transmitting = len(transmitting_nodes_this_slot)
        
        if num_transmitting == 1: # Success
            successful_transmissions += 1
            node = transmitting_nodes_this_slot[0]
            node.packet_buffer = None # Packet sent successfully
            node.wait_time = 0 # Reset CSMA wait time
            channel.is_busy = True
            channel.transmission_timer = PACKET_TRANSMISSION_TIME_MS
        
        elif num_transmitting > 1: # Collision
            for node in transmitting_nodes_this_slot:
                node.wait_time = 0 # Reset CSMA wait time
                # Set a random backoff to try sending the SAME packet again later
                if protocol == 'ALOHA':
                    node.backoff_counter = np.random.randint(1, 20) * PACKET_TRANSMISSION_TIME_MS
                else: # CSMA/CA
                    node.backoff_counter = np.random.randint(1, MAX_BACKOFF_SLOTS + 1)
            channel.is_busy = True
            channel.transmission_timer = PACKET_TRANSMISSION_TIME_MS

    if total_packets_generated == 0: return 1.0
    return successful_transmissions / total_packets_generated

# --- 4. MAIN EXECUTION AND VISUALIZATION ---

if __name__ == "__main__":
    node_counts = np.arange(10, 401, 20)
    aloha_pdr = []
    csma_pdr = []

    print("Running ALOHA simulations (high traffic)...")
    for n in tqdm(node_counts):
        aloha_pdr.append(run_simulation(n, 'ALOHA'))

    print("\nRunning CSMA/CA simulations (high traffic)...")
    for n in tqdm(node_counts):
        csma_pdr.append(run_simulation(n, 'CSMA/CA'))

    # Plotting the results
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))
    plt.plot(node_counts, aloha_pdr, 'o-', label='Pure ALOHA', color='r')
    plt.plot(node_counts, csma_pdr, 's-', label='CSMA/CA', color='b')

    plt.title('Network Performance: ALOHA vs. CSMA/CA in a Busy Parking Garage', fontsize=16)
    plt.xlabel('Number of Parking Spot Sensors', fontsize=12)
    plt.ylabel('Packet Delivery Ratio (PDR)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.ylim(0, 1.1)
    plt.xlim(0, max(node_counts) + 20)
    plt.show()

