"""One header logo shared by the landing page, storefront and owner workspace."""
import base64
from pathlib import Path

def logo_html():
    encoded=base64.b64encode((Path(__file__).parent/'images/hotvile-logo.svg').read_bytes()).decode('ascii')
    return f'<img class="hotvile-logo" src="data:image/svg+xml;base64,{encoded}" alt="HotVile Hot Sauce Co.">'
