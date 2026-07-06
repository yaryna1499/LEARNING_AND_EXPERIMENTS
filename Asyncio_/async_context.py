import asyncio
import socket


class AsyncSocketContextManager:
    """In this example, the __aenter__ method
    creates a new socket and connects to the
    specified host and port, and the __aexit__
    method closes the socket. When you use this
    async context manager in a with statement,
    it will automatically handle the setup and
    teardown of the network socket, ensuring
    that it is properly closed even if an exception occurs."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    async def __aenter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await self.sock.connect((self.host, self.port))
        return self.sock

    async def __aexit__(self, exc_type, exc, tb):
        self.sock.close()


async def main():
    """the same approach:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await sock.connect((host, port))
    finally:
        sock.close()
    """
    host = "example.com"
    port = 8080

    async with AsyncSocketContextManager(host, port) as sock:
        print(f"Connected to {host}:{port} by {sock}")

asyncio.run(main())
