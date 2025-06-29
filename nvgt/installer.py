# Code originally written by Ivan Soto (ims-productions.com)

import os
import platform
import subprocess
import urllib.request
import tempfile
import shutil
import tarfile


BASE_URL = "https://nvgt.gg"


def get_latest_version():
	with urllib.request.urlopen(f"{BASE_URL}/downloads/latest_version") as response:
		version = response.read().decode('utf-8').strip()
	return version


def download_file(url, path):
	print(f"Downloading: {url}")
	with urllib.request.urlopen(url) as response, open(path, 'wb') as out:
		shutil.copyfileobj(response, out)
	print(f"Downloaded to: {path}")

def install_windows(version):
	url = f"https://github.com/samtupy/nvgt/releases/download/latest/nvgt_{version}.exe"
	with tempfile.TemporaryDirectory() as tmp:
		installer = os.path.join(tmp, f"nvgt_{version}.exe")
		download_file(url, installer)
		subprocess.run([
			installer,
			"/VERYSILENT",
			"/SUPPRESSMSGBOXES",
			"/NORESTART",
			"/DIR=C:\\nvgt"
		], check=True)
		print("NVGT installed on Windows at C:\\nvgt")

def install_mac(version):
	url = f"https://github.com/samtupy/nvgt/releases/download/latest/nvgt_{version}.dmg"
	with tempfile.TemporaryDirectory() as tmp:
		dmg_path = os.path.join(tmp, f"nvgt_{version}.dmg")
		mount_point = "/Volumes/NVGT"
		download_file(url, dmg_path)
		subprocess.run(["hdiutil", "attach", dmg_path, "-mountpoint", mount_point], check=True)
		app_path = "/Applications/NVGT.app"
		if os.path.exists(app_path):
			subprocess.run(["sudo", "rm", "-rf", app_path], check=True)
		subprocess.run(["sudo", "cp", "-R", f"{mount_point}/NVGT.app", "/Applications/"], check=True)
		subprocess.run(["hdiutil", "detach", mount_point], check=True)
		print("NVGT installed in /Applications")
		binary_path = "/Applications/NVGT.app/Contents/MacOS/NVGT"
		if os.path.exists(binary_path):
			subprocess.run(["sudo", "chmod", "+x", binary_path], check=True)
			subprocess.run([binary_path, "--help"], check=True)
		else:
			print("NVGT binary not found inside the app bundle")

def install_linux(version):
	url = f"https://github.com/samtupy/nvgt/releases/download/latest/nvgt_{version}.tar.gz"
	with tempfile.TemporaryDirectory() as tmp:
		archive = os.path.join(tmp, f"nvgt_{version}.tar.gz")
		download_file(url, archive)
		install_dir = "/opt/nvgt"
		os.makedirs(install_dir, exist_ok=True)
		with tarfile.open(archive, "r:gz") as tar:
			tar.extractall(path=install_dir)
		print(f"NVGT installed on Linux at {install_dir}")

def main():
	version = get_latest_version()
	system = platform.system()
	if system == "Windows":
		install_windows(version)
	elif system == "Darwin":
		install_mac(version)
	elif system == "Linux":
		install_linux(version)
	else:
		raise NotImplementedError(f"Unsupported system: {system}")

if __name__ == "__main__":
	main()
