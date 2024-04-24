# UDP-Camera-Stream

A simple UDP-Based camera streaming software that captures an open-cv element and sends it to a target address.
The goal is to implement a camera streamer over a UDP-based transport protocol with minimal overhead for frame sequence.
This software prioritizes minimizing latency and bandwidth over video quality and packet integrity. It is designed for systems with resource budgets where low bandwidth and packet loss is likely to occur.

[sender.py](./sender.py) Listens for a TCP connection containing the target ip and port. Then spawns a process that Captures a video element with open-cv, splits the frame into chunks, and sends the frame segment (prefixed with a sequence number) to the target address via a UDP packet.

[receiver.py](./receiver.py) Given a known sender address, opens a TCP connection that requests a camera stream. On connection, listens on a UDP socket for frame packets, unpacks the frame segment and sequence number, then updates the segment of the frame that the packet is intended to modify.