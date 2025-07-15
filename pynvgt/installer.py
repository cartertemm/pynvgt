# Code originally written by Ivan Soto (ims-productions.com)

import os
import platform
import subprocess
import urllib.request
import tempfile
import shutil
import tarfile
from dataclasses import dataclass
from typing import Optional


BASE_URL = "https://nvgt.gg"
GITHUB_BASE_URL = "https://github.com/samtupy/nvgt/releases/download/latest"


@dataclass
class NVGTBuild:
	version: str

	@property
	def windows_version(self) -> str:
		return f"nvgt_{self.version}.exe"

	@property
	def linux_version(self) -> str:
		return f"nvgt_{self.version}.tar.gz"

	@property
	def macos_version(self) -> str:
		return f"nvgt_{self.version}.dmg"

	@property
	def windows_url(self) -> str:
		return f"{GITHUB_BASE_URL}/{self.windows_version}"

	@property
	def linux_url(self) -> str:
		return f"{GITHUB_BASE_URL}/{self.linux_version}"

	@property
	def macos_url(self) -> str:
		return f"{GITHUB_BASE_URL}/{self.macos_version}"

	@property
	def windows_install_path(self) -> str:
		return "C:\\nvgt"

	@property
	def linux_install_path(self) -> str:
		return "/opt/nvgt"

	@property
	def macos_install_path(self) -> str:
		return "/Applications/NVGT.app"

	@property
	def macos_binary_path(self) -> str:
		return f"{self.macos_install_path}/Contents/MacOS/NVGT"

	@classmethod
	def get_latest(cls) -> 'NVGTBuild':
		with urllib.request.urlopen(f"{BASE_URL}/downloads/latest_version") as response:
			version = response.read().decode('utf-8').strip()
		return cls(version=version)

	def download_file(self, url: str, path: str) -> None:
		print(f"Downloading: {url}")
		with urllib.request.urlopen(url) as response, open(path, 'wb') as out:
			shutil.copyfileobj(response, out)
		print(f"Downloaded to: {path}")

	def install_windows(self) -> None:
		with tempfile.TemporaryDirectory() as tmp:
			installer = os.path.join(tmp, self.windows_version)
			self.download_file(self.windows_url, installer)
			subprocess.run([
				installer,
				"/VERYSILENT",
				"/SUPPRESSMSGBOXES",
				"/NORESTART",
				f"/DIR={self.windows_install_path}"
			], check=True)
			print(f"NVGT installed on Windows at {self.windows_install_path}")
	def install_macos(self) -> None:
		with tempfile.TemporaryDirectory() as tmp:
			dmg_path = os.path.join(tmp, self.macos_version)
			mount_point = "/Volumes/NVGT"
			self.download_file(self.macos_url, dmg_path)
			subprocess.run(["hdiutil", "attach", dmg_path, "-mountpoint", mount_point], check=True)
			if os.path.exists(self.macos_install_path):
				subprocess.run(["sudo", "rm", "-rf", self.macos_install_path], check=True)
			subprocess.run(["sudo", "cp", "-R", f"{mount_point}/NVGT.app", "/Applications/"], check=True)
			subprocess.run(["hdiutil", "detach", mount_point], check=True)
			print(f"NVGT installed at {self.macos_install_path}")
			if os.path.exists(self.macos_binary_path):
				subprocess.run(["sudo", "chmod", "+x", self.macos_binary_path], check=True)
				subprocess.run([self.macos_binary_path, "--help"], check=True)
			else:
				print("NVGT binary not found inside the app bundle")

	def install_linux(self) -> None:
		with tempfile.TemporaryDirectory() as tmp:
			archive = os.path.join(tmp, self.linux_version)
			self.download_file(self.linux_url, archive)
			os.makedirs(self.linux_install_path, exist_ok=True)
			with tarfile.open(archive, "r:gz") as tar:
				tar.extractall(path=self.linux_install_path)
			print(f"NVGT installed on Linux at {self.linux_install_path}")

	def install_for_platform(self, platform_name: Optional[str] = None) -> None:
		if platform_name is None:
			platform_name = platform.system()
		if platform_name == "Windows":
			self.install_windows()
		elif platform_name == "Darwin":
			self.install_macos()
		elif platform_name == "Linux":
			self.install_linux()
		else:
			raise NotImplementedError(f"Unsupported system: {platform_name}")


def install_nvgt():
	build = NVGTBuild.get_latest()
	build.install_for_platform()
