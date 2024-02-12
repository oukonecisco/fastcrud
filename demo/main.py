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
import uvicorn

from demo.settings import SETTINGS

LOGGER = daiquiri.getLogger(__name__)


def api():
    """Execute the RESTful API Server."""
    daiquiri.setup(level=SETTINGS.log_level)  # type: ignore
    kwargs = {
        "host": "0.0.0.0",
        "port": SETTINGS.api_port,
        "workers": SETTINGS.workers,
        "log_level": SETTINGS.log_level.lower(),
    }
    if SETTINGS.environment == "local":
        kwargs["reload"] = True

    uvicorn.run("demo.api:app", **kwargs)
