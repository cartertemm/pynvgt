import platform
import click
from pynvgt.installer import NVGTBuild


@click.group()
@click.version_option()
def cli():
	"Command interface to python features for the non-visual gaming toolkit (NVGT)"


@cli.command(name="install")
@click.option(
	"-p",
	"--path",
	help="""The path under which the NVGT binary as well as include/lib folders and documentation will end up. Defaults to "C:\\nvgt" on Windows, "/opt/nvgt" on Linux, and "/Applications/NVGT.app" on MacOS."""
)
@click.option(
	"-d",
	"--dev",
	help="Install the latest development (possibly unstable) version.",
	is_flag=True,
	default=False
)
@click.option(
	"--platform",
	default=platform.system().lower(),
	help=f"""Download the files for the provided platform, which can be one of "android", "linux", "mac", or "windows". Defaults to {platform.system().lower()}, based on the active environment."""
)
def install(dev, path, platform):
	"Silently installs a copy of NVGT to the provided path."
	if dev:
		click.echo("Getting latest development version...")
	else:
		click.echo("Getting latest version...")
	builder = NVGTBuild.get_latest(dev=dev)
	click.echo(f"Found {builder.version}")
	click.echo(f"Installing for {platform}")
	builder.install_for_platform(platform)


@cli.command(name="uninstall")
@click.option(
	"-p",
	"--path",
	help="""The path from which to remove NVGT. Defaults to "C:\\nvgt" on Windows, "/opt/nvgt" on Linux, and "/Applications/NVGT.app" on MacOS."""
)
@click.option(
	"--platform",
	default=platform.system().lower(),
	help=f"""Platform to uninstall from, which can be one of "linux", "darwin", or "windows". Defaults to {platform.system().lower()}, based on the active environment."""
)
def uninstall(path, platform):
	"Removes an existing NVGT installation from the specified path."
	click.echo(f"Uninstalling NVGT for {platform}")
	builder = NVGTBuild(version="")  # Version not needed for uninstall
	builder.uninstall_for_platform(platform, path)
