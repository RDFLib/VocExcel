from importlib import metadata

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    ...


def get_version() -> str:
    try:
        version = metadata.version("vocexcel")
    except metadata.PackageNotFoundError:
        version = "0.0.0-dev.0"

    return version


class Settings:
    VOCEXCEL_VERSION = get_version()
