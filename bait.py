# -*- encoding: utf-8 -*-
"""蜜饵发布模块"""
from hashlib import sha1
from socket import gaierror
from base64 import b64encode
from json import dumps, loads
from urllib.parse import quote
from inspect import isawaitable
from asyncio.events import get_event_loop
from typing import Any, BinaryIO, Dict, Optional, Union

from aiofiles import open as aopen
from aiofiles.threadpool.binary import AsyncBufferedReader
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest


class NetworkError(Exception):
    """网络异常

    这通常是因为当前主机未与互联网连接，或当前网络环境不稳定导致的。
    """


class ConflictError(Exception):
    """文件冲突异常

    文件提交至 GitHub 时，与现存的文件发生冲突"""

    def __init__(self) -> None:
        """构造器"""
        super().__init__("目标路径已存在文件，提交时发生冲突")


class BadCredentialError(Exception):
    """凭证错误异常"""

    def __init__(self) -> None:
        """构造器"""
        super().__init__("GitHub Access Token 无效")


class GitHubPublisher:
    """GitHub 蜜饵发布模块"""

    def __init__(self, token: str, username: Optional[str] = None) -> None:
        """构造器"""
        self._token = token
        self._username = username

    async def verify_token(self) -> bool:
        """确认 Token 是否有效"""
        response = await self.fetch(HTTPRequest("https://api.github.com/user", "GET"))

        if self._username is None:
            self._username = response["login"]

    async def get_content(self, file: Union[BinaryIO, AsyncBufferedReader]) -> Dict[str, str]:
        """取得文件正文"""
        base64 = ""
        hasher = sha1()
        chunk_size = 1023

        chunk = file.read(chunk_size)
        if isawaitable(chunk):
            chunk = await chunk

        while chunk:
            hasher.update(chunk)
            base64 += b64encode(chunk).decode("utf-8")

            chunk = file.read(chunk_size)
            if isawaitable(chunk):
                chunk = await chunk

        return {"content": base64, "sha": hasher.hexdigest()}

    async def publish(self, file: Union[BinaryIO, AsyncBufferedReader], repository: str,
                      filename: str, message: str, name: Optional[str] = None, email: Optional[str] = None) -> None:
        """发布文件至 GitHub"""
        if self._username is None:
            await self.verify_token()

        content = {
            "message": message,
            "committer": {
                "name": name or self._username,
                "email": email or "name@example.com"
            }
        }
        content.update(await self.get_content(file))
        url = f"https://api.github.com/repos/{quote(self._username)}/{quote(repository)}/contents/{quote(filename)}"

        await self.fetch(HTTPRequest(url, "PUT", {
            "Content-Type": "application/json"
        }, body=dumps(content).encode("utf-8")))

    async def delete(self, file: Union[BinaryIO, AsyncBufferedReader], repository: str,
                  filename: str, message: str, name: Optional[str] = None, email: Optional[str] = None) -> None:
        """发布文件至 GitHub"""
        if self._username is None:
            await self.verify_token()

        content = {
            "message": message,
            "committer": {
                "name": name or self._username,
                "email": email or "name@example.com"
            }
        }
        # file_content = await self.get_content(file)
        content["sha"] = "582b02baab5601d86ac6b6831af91d1100a8b53c"
        import pdb;pdb.set_trace()
        url = f"https://api.github.com/repos/{quote(self._username)}/{quote(repository)}/contents/{quote(filename)}"
        await self.fetch(HTTPRequest(url, "DELETE", {
            "Content-Type": "application/json"
        }, body=dumps(content).encode("utf-8"), allow_nonstandard_methods=True))

    async def fetch(self, request: HTTPRequest) -> Dict[str, Any]:
        """请求 GitHub API接口"""
        default_headers = {
            "Accept": "application/json",
            "User-Agent": "dbappsecurity",
            "Authorization": f"token {self._token}"
        }
#         import pdb; pdb.set_trace()
        for key, value in default_headers.items():
            if key not in request.headers:
                request.headers[key] = value

        try:
            response = await AsyncHTTPClient().fetch(request)
            return loads(response.body)
        except gaierror:
            raise NetworkError("域名解析失败")
        except HTTPError as ex:
            if ex.code == 599:
                raise NetworkError("服务器连接或响应超时")
            if ex.code in (401, 403):
                raise BadCredentialError()
            if ex.code == 409:
                raise ConflictError()
            raise


async def main() -> None:
    publisher = GitHubPublisher("453ae8efcc3654319707f8748ac9421a6477bd44", "super1-chen")

    await publisher.verify_token()
#    async with aopen("test.txt", "rb") as file:
 #       await publisher.publish(file, "bait", "README.md", "初始提交")
#    async with aopen("config.ini", "rb") as file:
#        await publisher.publish(file, "bait", "config/config.ini", "初始提交")

    async with aopen("config.ini", "rb") as file:
        await publisher.delete(file, "bait", "README.md", "删除config")

if __name__ == "__main__":
    ioloop = get_event_loop()
    ioloop.run_until_complete(main())
