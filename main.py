import aiohttp
import asynctest
import json

async def logs(cont, name):
    conn = aiohttp.UnixConnector(path="/var/run/docker.sock")
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(f"http://xx/containers/{cont}/logs?follow=1&stdout=1") as resp:
            async for line in resp.content:
                print(name, line)

class TestLogs(asynctest.TestCase):
    async def test_logs_output(self):
        # arrange
        cont = "abc123"
        name = "container1"
        logs_output = b"Log line 1\nLog line 2\n"
        conn = asynctest.mock.Mock()
        session = asynctest.mock.Mock()
        resp = asynctest.mock.Mock()
        resp.content = asynctest.mock.Mock()
        resp.content.__aiter__.return_value = iter([logs_output])
        session.get.return_value = asynctest.mock.Mock(__aenter__=lambda s: resp)
        conn.__aenter__.return_value = session
        # act
        await logs(cont, name, conn)
        # assert
        session.get.assert_called_with(f"http://xx/containers/{cont}/logs?follow=1&stdout=1")
        resp.content.__aiter__.assert_called()
        print_mock = asynctest.mock.patch("builtins.print")
        print_mock.assert_called_with(name, logs_output)
        
    async def test_logs_http_error(self):
        # arrange
        cont = "abc123"
        name = "container1"
        conn = asynctest.mock.Mock()
        session = asynctest.mock.Mock()
        session.get.side_effect = aiohttp.ClientError
        conn.__aenter__.return_value = session
        # assert
        with self.assertRaises(aiohttp.ClientError):
            # act
            await logs(cont, name, conn)

TestLogs.test_logs_output()
TestLogs.test_logs_http_error()