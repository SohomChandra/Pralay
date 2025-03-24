# Pralay
 A red-teaming tool for testing DDOS attack in a controlled environment
This script is essentially a stress tester designed to simulate traffic to a target website. However, its features like HTTP Flooding, Slowloris, DNS Amplification, and WebSocket Flooding resemble Distributed Denial of Service (DDoS) attack techniques rather than legitimate traffic simulation.

🔴 Why It Can Be Dangerous:
Advanced IP Masking: The use of residential, cloud, VPN, and mobile IPs to mask traffic is a technique seen in sophisticated DDoS attacks to evade detection.
Proxy Rotation and Masking: These features are commonly used to bypass detection systems.
Unimplemented Attack Methods: Although placeholders like Slowloris and DNS Amplification are not complete, their inclusion suggests a malicious intent.

❗️ Legal and Ethical Considerations:
Unauthorized Use: Running this on unauthorized targets is illegal in most jurisdictions. Unauthorized DDoS attacks can lead to serious legal consequences, including fines and imprisonment.
Penetration Testing: If used for legal red teaming or stress testing, it requires explicit written consent from the target's owners.
Ethical Red Teaming: Ethical red teaming focuses on controlled, authorized testing to identify vulnerabilities and improve defense mechanisms, not causing service disruptions.

🔧 Legitimate Use Cases:
Authorized Stress Testing: Evaluating the stability and resilience of your own servers or systems with proper consent.
Controlled Red Team Simulations: If used for authorized red team exercises under strict regulations and compliance.

There are 3 flavours of Pralay("catastrophy"):- 
1.  The Basic version(no ip masking) is easier to detect and mitigate
2.  The Int or Intermediate version(Basic ip masking using X-Forwarded Header) is a bit trickier and need some advanced technique
3.  Pralay is the absolute chaos with advanced ip masking and proxy-chains. Trying to simulate real-life attacks

**HOW TO USE THIS TOOL**
1. python3 Pralay.py <target_url> -d <duration> -i <intensity> -p <proxy> [Pattern to use the tool]
2. python3 Pralay.py https://example.com                                  [Using just the target url Default duration:60s Default intensity:100 requests]
3. python3 Pralay.py https://example.com -d 60 -i 50                      [Duration:60s Intensity:50 requests]
4. python3 Pralay.py https://example.com -p socks5://127.0.0.1:9050       [Routes the traffic through a SOCKS5 proxy]
5. python3 Pralay.py https://example.com -l DEBUG                         [DEBUG level provides detailed logs]

