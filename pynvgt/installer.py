# Multiplatform code originally written by Ivan Soto (ims-productions.com)
# Restructured for PyNVGT

import json
import os
import platform
import re
import subprocess
import urllib.request
import tempfile
import shutil
import tarfile
import ssl
from urllib.request import urljoin
from dataclasses import dataclass
from typing import Optional


BASE_URL = "https://nvgt.gg"
STABLE_DOWNLOAD_URL = BASE_URL
GITHUB_API_URL = "https://api.github.com/repos/samtupy/nvgt/releases/tags/latest"
GITHUB_BASE_URL = "https://github.com/samtupy/nvgt/releases/download/latest"


def _extract_version_from_filename(filename: str) -> str:
	match = re.search(r"nvgt_([0-9]+\.[0-9]+\.[0-9]+_[a-zA-Z0-9_]+)\..*", filename)
	if match:
		return match.group(1)


def _download_file(url: str, path: str) -> None:
	print(f"Downloading: {url}")
	context = ssl.create_default_context()
	request = urllib.request.Request(url)
	with urllib.request.urlopen(request, timeout=30, context=context) as response, open(path, 'wb') as out:
		shutil.copyfileobj(response, out)
	print(f"Downloaded to: {path}")


@dataclass
class NVGTBuild:
	version: str
	is_dev: bool = False
	download_urls: Optional[dict] = None

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
		if self.is_dev and self.download_urls:
			return self.download_urls.get('windows', '')
		return f"{BASE_URL}/downloads/{self.windows_version}"

	@property
	def linux_url(self) -> str:
		if self.is_dev and self.download_urls:
			return self.download_urls.get('linux', '')
		return f"{BASE_URL}/downloads/{self.linux_version}"

	@property
	def macos_url(self) -> str:
		if self.is_dev and self.download_urls:
			return self.download_urls.get('macos', '')
		return f"{BASE_URL}/downloads/{self.macos_version}"

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
	def get_latest(cls, dev: bool = False) -> 'NVGTBuild':
		if dev:
			return cls._get_dev_version()
		else:
			context = ssl.create_default_context()
			request = urllib.request.Request(f"{BASE_URL}/downloads/latest_version")
			with urllib.request.urlopen(request, timeout=30, context=context) as response:
				version = response.read().decode('utf-8').strip()
			return cls(version=version)

	@classmethod
	def _get_dev_version(cls) -> 'NVGTBuild':
		context = ssl.create_default_context()
		request = urllib.request.Request(GITHUB_API_URL)
		with urllib.request.urlopen(request, timeout=30, context=context) as response:
			data = json.loads(response.read().decode('utf-8'))
			# Extract version and download URLs from assets
			version = None
			download_urls = {}
			for asset in data['assets']:
				name = asset['name']
				# we have to extract the version number from the name of the file
				# because we can't count on tag names
				version = _extract_version_from_filename(name)
				if name.endswith('.exe'):
					download_urls['windows'] = asset['browser_download_url']
				elif name.endswith('.tar.gz'):
					download_urls['linux'] = asset['browser_download_url']
				elif name.endswith('.dmg'):
					download_urls['macos'] = asset['browser_download_url']
			return cls(version=version, is_dev=True, download_urls=download_urls)

	def install_windows(self) -> None:
		with tempfile.TemporaryDirectory() as tmp:
			installer = os.path.join(tmp, self.windows_version)
			_download_file(self.windows_url, installer)
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
			_download_file(self.macos_url, dmg_path)
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
			_download_file(self.linux_url, archive)
			os.makedirs(self.linux_install_path, exist_ok=True)
			with tarfile.open(archive, "r:gz") as tar:
				tar.extractall(path=self.linux_install_path)
			print(f"NVGT installed on Linux at {self.linux_install_path}")

	def install_for_platform(self, platform_name: Optional[str] = None) -> None:
		if platform_name is None:
			platform_name = platform.system()
		platform_name = platform_name.lower()
		if platform_name == "windows":
			self.install_windows()
		elif platform_name == "darwin":
			self.install_macos()
		elif platform_name == "linux":
			self.install_linux()
		else:
			raise NotImplementedError(f"Unsupported system: {platform_name}")

	def uninstall_windows(self, path: Optional[str] = None) -> None:
		install_path = path or self.windows_install_path
		uninstaller = os.path.join(install_path, "unins000.exe")
		if not os.path.isdir(install_path):
			print(f"NVGT installation not found at {install_path}")
			return
		if os.path.exists(uninstaller):
			print("Running uninstaller")
			subprocess.run([
				uninstaller,
				"/VERYSILENT",
				"/SUPPRESSMSGBOXES",
				"/NORESTART"
			], check=True)
		# Even if unins000 was executed, the directory may have been left behind, so clean it up
		if os.path.exists(install_path):
			shutil.rmtree(install_path)
		print(f"NVGT uninstalled from Windows at {install_path}")

	def uninstall_macos(self, path: Optional[str] = None) -> None:
		install_path = path or self.macos_install_path
		if os.path.exists(install_path):
			subprocess.run(["sudo", "rm", "-rf", install_path], check=True)
			print(f"NVGT uninstalled from macOS at {install_path}")
		else:
			print(f"NVGT installation not found at {install_path}")

	def uninstall_linux(self, path: Optional[str] = None) -> None:
		install_path = path or self.linux_install_path
		if os.path.exists(install_path):
			shutil.rmtree(install_path)
			print(f"NVGT uninstalled from Linux at {install_path}")
		else:
			print(f"NVGT installation not found at {install_path}")

	def uninstall_for_platform(self, platform_name: Optional[str] = None, path: Optional[str] = None) -> None:
		if platform_name is None:
			platform_name = platform.system()
		platform_name = platform_name.lower()
		if platform_name == "windows":
			self.uninstall_windows(path)
		elif platform_name == "darwin":
			self.uninstall_macos(path)
		elif platform_name == "linux":
			self.uninstall_linux(path)
		else:
			raise NotImplementedError(f"Unsupported system: {platform_name}")


def install_nvgt(dev=False):
	build = NVGTBuild.get_latest(dev=dev)
	build.install_for_platform()
