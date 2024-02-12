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


from contextlib import asynccontextmanager

import daiquiri
from fastapi import FastAPI

from demo.router import router
from demo.settings import SETTINGS

LOGGER = daiquiri.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Defines the startup and shutdown events."""
    # Startup event
    await startup_db_client(application)

    yield

    # Shutdown event
    await shutdown_db_client(application)


app = FastAPI(
    title="CRUD API",
    docs_url="/api/item/docs",
    openapi_url="/api/item/openapi.json",
    version=SETTINGS.version,
    lifespan=lifespan,  # type: ignore
)


app.include_router(router, prefix="/api")


async def startup_db_client(application: FastAPI):
    """Connect to MongoDB and create indexes."""

    ...


async def shutdown_db_client(application: FastAPI):
    """Disconnect from MongoDB."""
    # application.mongodb_client.close()  # type: ignore
    ...


@app.get("/", include_in_schema=False)
def read_root():
    return {
        "app": SETTINGS.app,
        "version": SETTINGS.version,
        "docs": SETTINGS.docs_url,
        "environment": SETTINGS.environment,
    }
