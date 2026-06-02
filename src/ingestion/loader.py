# src/ingestion/loader.py

from pathlib import Path
import zipfile

import requests
from tqdm import tqdm

CUAD_URL = (
    "https://zenodo.org/records/4595826/files/CUAD_v1.zip?download=1"
)


def download_file(url: str, destination: Path) -> None:
    """Download file with progress bar."""

    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get("content-length", 0))

    with open(destination, "wb") as file, tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        desc=destination.name,
    ) as progress:

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                progress.update(len(chunk))


def download_cuad(data_dir: str = "data") -> Path:
    """
    Download and extract CUAD dataset.

    Returns:
        Path to extracted CUAD directory.
    """

    data_path = Path(data_dir)
    cuad_path = data_path / "cuad"

    pdf_dir = cuad_path / "full_contract_pdf"

    # Already downloaded
    if pdf_dir.exists() and any(pdf_dir.glob("*.pdf")):
        print(f"✓ CUAD already exists at {cuad_path}")
        return cuad_path

    cuad_path.mkdir(parents=True, exist_ok=True)

    zip_path = cuad_path / "CUAD_v1.zip"

    # Download
    if not zip_path.exists():
        print("Downloading CUAD dataset...")
        download_file(CUAD_URL, zip_path)

    # Extract everything
    print("Extracting dataset...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(cuad_path)

    print(f"✓ CUAD extracted to {cuad_path}")

    return cuad_path


if __name__ == "__main__":
    download_cuad()