# -*- coding: utf-8 -*-
__author__ = "CX Catalog Team"
__email__ = "cxcatalog-notifications@cisco.com"
__copyright__ = """
Copyright 2022, Cisco Systems, Inc. 
All Rights Reserved. 
 
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, 
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
OTHER DEALINGS IN THE SOFTWARE. 
"""  # noqa
__status__ = "Production"


import daiquiri
from pydantic_settings import BaseSettings

from fastcrud import __version__

LOGGER = daiquiri.getLogger(__name__)


class Settings(BaseSettings):
    """Settings."""

    app: str = "Item Services"
    microservice: str = "item"
    environment: str = "local"
    workers: int = 1
    version: str = __version__
    docs_url: str = "/api/item/docs"
    openapi_url: str = "/api/item/openapi.json"
    metrics_url: str = "/metrics"
    api_port: int = 9090
    log_level: str = "INFO"

    allow_origins: list[str] = []
    api_default_limit: int = 10
    api_default_offset: int = 0
    debug: bool = False
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    mongodb_url: str | None = "mongodb://root:example@0.0.0.0/"
    mongodb_name: str = "fastcrud"


SETTINGS = Settings()
