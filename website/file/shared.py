from pathlib import Path
from django.core.files.storage import FileSystemStorage


HERE = Path(__file__).parent
ROOT = HERE.parent.parent
UPLOADS = ROOT / "uploads"

fs = FileSystemStorage(location=UPLOADS)


