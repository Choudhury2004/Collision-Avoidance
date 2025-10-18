# Collision-Avoidance
This project focuses on implementing and comparing collision handling techniques in an IoT (Internet of Things) communication network.
When multiple IoT devices try to transmit data simultaneously over a shared channel, data collisions occur — leading to packet loss and poor network performance.
To address this, the project simulates two well-known communication protocols:
1. Pure ALOHA – a basic random access method (used as baseline)
2. CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance) – an enhanced method that reduces collisions by checking the channel before transmitting.

🎯 Objectives:
1. Understand how data collisions occur in shared IoT communication channels.
2. Implement and compare Pure ALOHA and CSMA/CA protocols.
3. Demonstrate how collision avoidance improves data transmission efficiency.

🧠 Concept Explanation:
1. Pure ALOHA: Devices transmit data whenever they have data ready, without checking if the channel is free. This often results in high collision rates.
2. CSMA/CA: Devices sense the channel before transmitting. If the channel is busy, they wait for a random time (backoff period) before trying again — effectively avoiding collisions.

iot_collision_avoidance/
├── venv/
├── test.py
├── simulation.py
├── README.md
└── requirements.txt
