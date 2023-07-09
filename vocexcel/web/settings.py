from os import environ

from vocexcel.settings import Settings as BaseSettings


class Settings(BaseSettings):
    VOCEXCEL_WEB_STATIC_DIR = environ.get("VOCEXCEL_WEB_STATIC_DIR", "vocexcel/web/static")
