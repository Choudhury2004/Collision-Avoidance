import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# --- 1. SIMULATION PARAMETERS (REAL-WORLD VALUES) ---
SIMULATION_TIME_MS = 10000  # We will simulate 10 seconds of activity
PACKET_TRANSMISSION_TIME_MS = 10  # Time it takes for a sensor to send one message
AVG_CAR_ARRIVAL_RATE_PER_HOUR = 2 # On average, a car arrives/leaves a spot twice per hour
PROB_EVENT_PER_MS = AVG_CAR_ARRIVAL_RATE_PER_HOUR / (60 * 60 * 1000) # Probability of a car event in any given millisecond

# CSMA/CA specific parameters
DIFS_MS = 2  # A short waiting period before transmitting
MAX_BACKOFF_SLOTS = 5 # Maximum random wait time if channel is busy

# --- 2. CORE COMPONENT CLASSES ---

class SensorNode:
    """Represents a single parking spot sensor."""
    def __init__(self, id, protocol):
        self.id = id
        self.protocol = protocol
        self.has_packet_to_send = False
        self.backoff_counter = 0
        self.wait_time = 0

    def check_for_event(self):
        """Simulates a car arriving or leaving."""
        if not self.has_packet_to_send and np.random.rand() < PROB_EVENT_PER_MS:
            self.has_packet_to_send = True

class Channel:
    """Represents the shared wireless channel."""
    def __init__(self):
        self.is_busy = False
        self.transmitting_nodes = []
        self.transmission_timer = 0

    def check_for_collision(self):
        """Checks if a collision occurred in the previous time slot."""
        if len(self.transmitting_nodes) == 1:
            return "SUCCESS"
        elif len(self.transmitting_nodes) > 1:
            return "COLLISION"
        return "IDLE"

# --- 3. SIMULATION ENGINE ---

def run_simulation(num_nodes, protocol):
    """Runs a complete simulation for a given number of sensors and protocol."""
    nodes = [SensorNode(i, protocol) for i in range(num_nodes)]
    channel = Channel()
    
    successful_transmissions = 0
    collisions = 0

    # Main simulation loop, iterating millisecond by millisecond
    for t in range(SIMULATION_TIME_MS):
        
        # Reset channel state for the new time slot
        channel.transmitting_nodes = []

        # --- SENSOR LOGIC (The heart of the simulation) ---
        for node in nodes:
            node.check_for_event()

            if node.has_packet_to_send:
                if protocol == 'ALOHA':
                    # ALOHA: Transmit immediately if you have a packet
                    channel.transmitting_nodes.append(node)
                
                elif protocol == 'CSMA/CA':
                    if channel.is_busy:
                        # If channel is busy, set a random backoff counter
                        if node.backoff_counter == 0:
                           node.backoff_counter = np.random.randint(1, MAX_BACKOFF_SLOTS + 1) * PACKET_TRANSMISSION_TIME_MS
                    else:
                        if node.backoff_counter > 0:
                            node.backoff_counter -= 1
                        else:
                            # If channel is free and backoff is done, wait for DIFS
                            if node.wait_time < DIFS_MS:
                                node.wait_time += 1
                            else:
                                # After DIFS, transmit
                                channel.transmitting_nodes.append(node)

        # --- CHANNEL LOGIC ---
        outcome = channel.check_for_collision()
        
        if outcome == "SUCCESS":
            successful_transmissions += 1
            node_id = channel.transmitting_nodes[0].id
            nodes[node_id].has_packet_to_send = False
            if protocol == 'CSMA/CA':
                nodes[node_id].wait_time = 0
            
            channel.is_busy = True
            channel.transmission_timer = PACKET_TRANSMISSION_TIME_MS

        elif outcome == "COLLISION":
            collisions += 1
            for node in channel.transmitting_nodes:
                if protocol == 'CSMA/CA':
                    # On collision, reset and set a new random backoff
                    node.wait_time = 0
                    node.backoff_counter = np.random.randint(1, MAX_BACKOFF_SLOTS + 1) * PACKET_TRANSMISSION_TIME_MS
            
            channel.is_busy = True
            channel.transmission_timer = PACKET_TRANSMISSION_TIME_MS
        
        # Update channel busy state
        if channel.transmission_timer > 0:
            channel.transmission_timer -= 1
            if channel.transmission_timer == 0:
                channel.is_busy = False

    total_packets_generated = successful_transmissions + collisions
    if total_packets_generated == 0:
        return 1.0 # Perfect PDR if no packets were even generated
        
    packet_delivery_ratio = successful_transmissions / total_packets_generated
    return packet_delivery_ratio

# --- 4. MAIN EXECUTION AND VISUALIZATION ---

if __name__ == "__main__":
    node_counts = np.arange(50, 801, 50) # Simulate for 50 to 800 sensors
    aloha_pdr = []
    csma_pdr = []

    print("Running ALOHA simulations...")
    for n in tqdm(node_counts):
        aloha_pdr.append(run_simulation(n, 'ALOHA'))

    print("\nRunning CSMA/CA simulations...")
    for n in tqdm(node_counts):
        csma_pdr.append(run_simulation(n, 'CSMA/CA'))

    # Plotting the results
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))
    plt.plot(node_counts, aloha_pdr, 'o-', label='Pure ALOHA', color='r')
    plt.plot(node_counts, csma_pdr, 's-', label='CSMA/CA', color='b')
    
    plt.title('Network Performance: ALOHA vs. CSMA/CA in a Smart Parking Garage', fontsize=16)
    plt.xlabel('Number of Parking Spot Sensors', fontsize=12)
    plt.ylabel('Packet Delivery Ratio (PDR)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.ylim(0, 1.1)
    plt.xlim(0, max(node_counts) + 50)
    plt.show()