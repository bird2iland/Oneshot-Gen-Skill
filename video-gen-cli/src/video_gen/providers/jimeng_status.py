import asyncio
import shutil
from dataclasses import dataclass, field
from typing import Optional, Tuple

from video_gen.core.errors import JimengNotInstalledError, JimengNotLoggedInError


@dataclass
class JimengStatus:
    installed: bool = False
    version: Optional[str] = None
    logged_in: bool = False
    user_info: Optional[str] = None
    error: Optional[str] = None


class JimengStatusChecker:
    def __init__(self, cli_path: Optional[str] = None):
        self._cli_path = cli_path
        self._min_version = "1.0.0"

    def _find_jimeng_cli(self) -> Optional[str]:
        if self._cli_path:
            return self._cli_path
        # dreamina 是即梦 CLI 的实际名称
        return shutil.which("dreamina") or shutil.which("jimeng")

    async def _run_command(self, args: list[str]) -> Tuple[int, str, str]:
        cli_path = self._find_jimeng_cli()
        if not cli_path:
            raise JimengNotInstalledError()

        process = await asyncio.create_subprocess_exec(
            cli_path,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            process.returncode or 0,
            stdout.decode("utf-8", errors="ignore"),
            stderr.decode("utf-8", errors="ignore"),
        )

    async def check_installation(self) -> Tuple[bool, Optional[str]]:
        cli_path = self._find_jimeng_cli()
        if not cli_path:
            return False, None

        try:
            returncode, stdout, _ = await self._run_command(["--version"])
            if returncode == 0:
                version = stdout.strip().split()[-1] if stdout.strip() else None
                return True, version
        except JimengNotInstalledError:
            return False, None
        except Exception:
            return False, None

        return False, None

    async def check_login(self) -> Tuple[bool, Optional[str]]:
        try:
            # dreamina 使用 login 命令检查登录状态
            returncode, stdout, stderr = await self._run_command(["login"])
            output = stdout + stderr
            
            # 检测登录成功的标志
            logged_in = (
                "已复用当前" in output or 
                "登录成功" in output or 
                "登录账户信息" in output or
                "user_id" in output
            )
            
            user_info = None
            if logged_in:
                # 提取 user_id
                import re
                user_id_match = re.search(r"user_id[:\s]+(\d+)", output)
                if user_id_match:
                    user_info = f"user_id: {user_id_match.group(1)}"
                    
                credit_match = re.search(r"total_credit[:\s]+(\d+)", output)
                if credit_match and user_info:
                    user_info += f", credit: {credit_match.group(1)}"
                    
            return logged_in, user_info
        except JimengNotInstalledError:
            return False, None
        except Exception:
            return False, None

    async def check_full_status(self) -> JimengStatus:
        status = JimengStatus()

        installed, version = await self.check_installation()
        status.installed = installed
        status.version = version

        if not installed:
            status.error = "Jimeng CLI not found"
            return status

        logged_in, user_info = await self.check_login()
        status.logged_in = logged_in
        status.user_info = user_info

        if not logged_in:
            status.error = "User not logged in"

        return status

    def get_install_guide(self) -> str:
        return """即梦 (Dreamina) Video Generation Tool Installation Guide:

1. Install Dreamina CLI:
   curl -fsSL https://jimeng.jianying.com/cli | bash

2. Verify installation:
   dreamina --version

3. Login to Dreamina:
   dreamina login

4. Check user credit:
   dreamina user_credit

For more information, visit: https://jimeng.jianying.com/docs/cli

Supported models:
  - seedance2.0 (default)
  - seedance2.0fast
  - seedance2.0_vip
  - seedance2.0fast_vip

Supported ratios:
  - 1:1, 3:4, 16:9, 4:3, 9:16, 21:9

Duration range: 4-15 seconds
Maximum images: 9
"""