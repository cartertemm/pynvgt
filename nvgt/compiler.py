"""
NVGT Compiler Interface

A Python interface to the Non-Visual Gaming Toolkit (NVGT) compiler
with support for all command line options. Can be used standalone, in CI/CD pipelines, or as part of
larger applications.

This module provides:
- NVGTCompiler: Main compiler interface class
- NVGTCompilerOptions: Configuration dataclass for compilation options
- NVGTPlatform/NVGTWarningLevel: Enums for type safety
- CompilationResult: Structured results from compiler operations
- detect_nvgt_installation: Auto-detection of NVGT installations (checks for a copy on the path, followed by the default location for the platform)
"""

import asyncio
import shutil
import platform
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict


class NVGTPlatform(Enum):
	"""Supported NVGT compilation platforms."""

	AUTO = "auto"
	WINDOWS = "windows"
	LINUX = "linux"
	MAC = "mac"
	ANDROID = "android"


class NVGTWarningLevel(Enum):
	"""NVGT warning handling levels."""

	IGNORE = 0
	PRINT = 1
	TREAT_AS_ERROR = 2


@dataclass
class NVGTResult:
	"""Base class for NVGT operation results."""

	success: bool
	error: Optional[str] = None

	def to_dict(self) -> dict:
		"""Convert to dictionary for JSON serialization."""
		return asdict(self)


@dataclass
class CompilationResult(NVGTResult):
	"""Result of NVGT compilation operation."""

	stdout: str = ""
	stderr: str = ""
	return_code: int = 0
	command: Optional[str] = None

	@classmethod
	def success_result(
		cls, stdout: str, stderr: str, return_code: int, command: str
	) -> "CompilationResult":
		"""Create a successful compilation result."""
		return cls(
			success=return_code == 0,
			stdout=stdout,
			stderr=stderr,
			return_code=return_code,
			command=command,
		)

	@classmethod
	def error_result(cls, error: str, return_code: int = -1) -> "CompilationResult":
		"""Create an error compilation result."""
		return cls(success=False, error=error, return_code=return_code)


@dataclass
class NVGTCompilerOptions:
	"""Configuration options for NVGT compilation."""

	# Compilation modes
	compile_release: bool = False
	compile_debug: bool = False
	run_with_debugger: bool = False
	# Platform and output options
	platform: Optional[NVGTPlatform] = None
	quiet: bool = False
	super_quiet: bool = False
	warning_level: NVGTWarningLevel = NVGTWarningLevel.IGNORE
	# Assets and includes
	assets: List[str] = field(default_factory=list)
	document_assets: List[str] = field(default_factory=list)
	includes: List[str] = field(default_factory=list)
	include_directories: List[str] = field(default_factory=list)
	# Configuration
	config_properties: Dict[str, str] = field(default_factory=dict)
	settings_file: Optional[str] = None
	# Script arguments (passed after --)
	script_args: List[str] = field(default_factory=list)


def detect_nvgt_installation(path: Optional[str] = None) -> Optional[str]:
	"""
	Detect NVGT installation and return path to binary.
	Args:
			path: Optional path to check for NVGT installation
	Returns:
			Path to NVGT binary if found, None otherwise
	"""
	if path:
		# Check provided path
		nvgt_path = Path(path)
		if nvgt_path.is_file() and nvgt_path.exists():
			return str(nvgt_path)
		return None
	# todo: Try to find nvgt in PATH
	## shutil.which will return files of any extension (e.g. nvgt.py). We need to use something else here.
	# nvgt_in_path = shutil.which("nvgt")
	# if nvgt_in_path:
	# return nvgt_in_path
	# Check platform-specific default locations
	system = platform.system().lower()
	if system == "windows":
		default_path = Path("C:/nvgt/nvgt.exe")
		if default_path.exists():
			return str(default_path)
	elif system == "darwin":  # macOS
		default_path = Path("/Applications/NVGT.app/Contents/MacOS/NVGT")
		if default_path.exists():
			return str(default_path)
	return None


async def _run_command(command: str) -> tuple[int, bytes, bytes]:
	"""
	Execute a shell command asynchronously.
	Args:
			command: Command string to execute
	Returns:
			Tuple of (return_code, stdout, stderr)
	"""
	proc = await asyncio.create_subprocess_shell(
		command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
	)
	stdout, stderr = await proc.communicate()
	return (proc.returncode, stdout, stderr)


class NVGTCompiler:
	"""
	An interface to the NVGT compiler.

	This class provides a Python interface to all NVGT compiler features including:
	- Release and debug compilation
	- Cross-platform targeting
	- Asset bundling
	- Script inclusion and debugging
	- Configuration management
	Example:
			compiler = NVGTCompiler()
			result = await compiler.compile_release("mygame.nvgt")
			if result.success:
					print("Compilation successful!")
			else:
					print(f"Error: {result.error}")
	"""

	def __init__(self, nvgt_binary_path: Optional[str] = None):
		"""
		Initialize the NVGT compiler interface.
		Args:
				nvgt_binary_path: Path to NVGT binary. If None, will auto-detect.
		Raises:
				RuntimeError: If NVGT installation cannot be found.
		"""
		self.nvgt_binary = nvgt_binary_path or detect_nvgt_installation()
		if not self.nvgt_binary:
			raise RuntimeError(
				"NVGT installation not found. Please ensure NVGT is installed and accessible."
			)

	def build_command(
		self, script_path: str, options: NVGTCompilerOptions
	) -> List[str]:
		"""
		Build the NVGT command with all specified options.
		Args:
				script_path: Path to the NVGT script file
				options: Compilation options
		Returns:
				List of command arguments
		"""
		cmd = [self.nvgt_binary]
		# Compilation modes (mutually exclusive)
		if options.compile_release:
			cmd.append("-c")
		elif options.compile_debug:
			cmd.append("-C")
		elif options.run_with_debugger:
			cmd.append("-d")
		# Platform selection
		if options.platform:
			cmd.append(f"-p{options.platform.value}")
		# Output options
		if options.super_quiet:
			cmd.append("-Q")
		elif options.quiet:
			cmd.append("-q")
		# Warning level
		if options.warning_level != NVGTWarningLevel.IGNORE:
			cmd.append(f"-w{options.warning_level.value}")
		# Assets
		for asset in options.assets:
			cmd.append(f"-a{asset}")
		# Document assets
		for doc_asset in options.document_assets:
			cmd.append(f"-A{doc_asset}")
		# Includes
		for include in options.includes:
			cmd.append(f"-i{include}")
		# Include directories
		for include_dir in options.include_directories:
			cmd.append(f"-I{include_dir}")
		# Configuration properties
		for name, value in options.config_properties.items():
			cmd.append(f"-s{name}={value}")
		# Settings file
		if options.settings_file:
			cmd.append(f"-S{options.settings_file}")
		# Script file (required)
		cmd.append(script_path)
		# Script arguments
		if options.script_args:
			cmd.append("--")
			cmd.extend(options.script_args)
		return cmd

	async def compile_release(self, script_path: str, **kwargs) -> CompilationResult:
		"""
		Compile script in release mode.
		Args:
				script_path: Path to the NVGT script file
				**kwargs: Additional options (see NVGTCompilerOptions)
		Returns:
				CompilationResult with compilation details
		"""
		options = NVGTCompilerOptions(compile_release=True, **kwargs)
		return await self._execute_command(script_path, options)

	async def compile_debug(self, script_path: str, **kwargs) -> CompilationResult:
		"""
		Compile script in debug mode.
		Args:
				script_path: Path to the NVGT script file
				**kwargs: Additional options (see NVGTCompilerOptions)
		Returns:
				CompilationResult with compilation details
		"""
		options = NVGTCompilerOptions(compile_debug=True, **kwargs)
		return await self._execute_command(script_path, options)

	async def run_script(self, script_path: str, **kwargs) -> CompilationResult:
		"""
		Run script directly (no compilation).
		Args:
				script_path: Path to the NVGT script file
				**kwargs: Additional options (see NVGTCompilerOptions)
		Returns:
				CompilationResult with execution details
		"""
		options = NVGTCompilerOptions(**kwargs)
		return await self._execute_command(script_path, options)

	async def debug_script(self, script_path: str, **kwargs) -> CompilationResult:
		"""
		Run script with the Angelscript debugger.
		Args:
				script_path: Path to the NVGT script file
				**kwargs: Additional options (see NVGTCompilerOptions)
		Returns:
				CompilationResult with debugging session details
		"""
		options = NVGTCompilerOptions(run_with_debugger=True, **kwargs)
		return await self._execute_command(script_path, options)

	async def get_version(self) -> CompilationResult:
		"""
		Get NVGT version information.
		Returns:
				CompilationResult with version information in stdout
		"""
		cmd = [self.nvgt_binary, "-V"]
		try:
			return_code, stdout, stderr = await _run_command(
				" ".join(f'"{arg}"' for arg in cmd)
			)
			return CompilationResult.success_result(
				stdout=stdout.decode("utf-8") if stdout else "",
				stderr=stderr.decode("utf-8") if stderr else "",
				return_code=return_code,
				command=" ".join(cmd),
			)
		except Exception as e:
			return CompilationResult.error_result(f"Failed to get version: {str(e)}")

	async def get_help(self) -> CompilationResult:
		"""
		Get NVGT help information.
		Returns:
				CompilationResult with help text in stdout
		"""
		cmd = [self.nvgt_binary, "-h"]
		try:
			return_code, stdout, stderr = await _run_command(
				" ".join(f'"{arg}"' for arg in cmd)
			)
			return CompilationResult.success_result(
				stdout=stdout.decode("utf-8") if stdout else "",
				stderr=stderr.decode("utf-8") if stderr else "",
				return_code=return_code,
				command=" ".join(cmd),
			)
		except Exception as e:
			return CompilationResult.error_result(f"Failed to get help: {str(e)}")

	async def _execute_command(
		self, script_path: str, options: NVGTCompilerOptions
	) -> CompilationResult:
		"""
		Execute NVGT command with given options.
		Args:
				script_path: Path to the script file
				options: Compilation options
		Returns:
				CompilationResult with execution details
		"""
		# Verify script file exists
		script_file = Path(script_path)
		if not script_file.exists():
			return CompilationResult.error_result(
				f"Script file not found: {script_path}"
			)
		# Build and execute command
		cmd = self.build_command(script_path, options)
		command_str = " ".join(f'"{arg}"' for arg in cmd)
		try:
			return_code, stdout, stderr = await _run_command(command_str)
			return CompilationResult.success_result(
				stdout=stdout.decode("utf-8") if stdout else "",
				stderr=stderr.decode("utf-8") if stderr else "",
				return_code=return_code,
				command=command_str,
			)
		except Exception as e:
			return CompilationResult.error_result(
				f"Failed to execute command: {str(e)}"
			)


# Convenience functions for standalone usage
async def compile_nvgt_release(
	script_path: str, nvgt_binary: Optional[str] = None, **kwargs
) -> CompilationResult:
	"""
	Convenience function to compile an NVGT script in release mode.
	Args:
			script_path: Path to the NVGT script file
			nvgt_binary: Optional path to NVGT binary
			**kwargs: Additional compilation options
	Returns:
			CompilationResult with compilation details
	"""
	compiler = NVGTCompiler(nvgt_binary)
	return await compiler.compile_release(script_path, **kwargs)


async def compile_nvgt_debug(
	script_path: str, nvgt_binary: Optional[str] = None, **kwargs
) -> CompilationResult:
	"""
	Convenience function to compile an NVGT script in debug mode.
	Args:
			script_path: Path to the NVGT script file
			nvgt_binary: Optional path to NVGT binary
			**kwargs: Additional compilation options
	Returns:
			CompilationResult with compilation details
	"""
	compiler = NVGTCompiler(nvgt_binary)
	return await compiler.compile_debug(script_path, **kwargs)


async def run_nvgt_script(
	script_path: str, nvgt_binary: Optional[str] = None, **kwargs
) -> CompilationResult:
	"""
	Convenience function to run an NVGT script directly.
	Args:
			script_path: Path to the NVGT script file
			nvgt_binary: Optional path to NVGT binary
			**kwargs: Additional execution options
	Returns:
			CompilationResult with execution details
	"""
	compiler = NVGTCompiler(nvgt_binary)
	return await compiler.run_script(script_path, **kwargs)
