"""Fetch OpenDengue V1.3.1 dataset and filter Thailand Admin1 monthly data.

Outputs:
  - data/raw/Temporal_extract_V1_3_1.zip (downloaded)
  - data/raw/Temporal_extract_V1_3_1.csv (extracted raw extract)
  - data/raw/opendengue_tha_admin1_month.csv (filtered Thailand province-month rows)
  - data/raw/SOURCE_opendengue.md (data provenance, checksum, license, citation)
"""

import datetime
import hashlib
from pathlib import Path
import sys
import zipfile
import pandas as pd
import requests
import yaml

# OpenDengue V1.3.1 download URL
OPENDENGUE_URL = (
    "https://raw.githubusercontent.com/OpenDengue/master-repo/main/"
    "data/releases/V1.3.1/Temporal_extract_V1_3_1.zip"
)
ZIP_FILENAME = "Temporal_extract_V1_3_1.zip"
FILTERED_CSV_FILENAME = "opendengue_tha_admin1_month.csv"
SOURCE_MD_FILENAME = "SOURCE_opendengue.md"


def get_raw_dir() -> Path:
    """Read raw_dir from config/params.yaml or fallback to default."""
    config_path = Path("config/params.yaml")
    raw_dir = Path("data/raw")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                params = yaml.safe_load(f)
            raw_dir = Path(params.get("paths", {}).get("raw_dir", "data/raw"))
        except Exception as e:
            print(f"Warning: Could not read config/params.yaml ({e}), using default 'data/raw'")
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir


def compute_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def download_file(url: str, dest_path: Path, chunk_size: int = 1024 * 1024) -> None:
    """Download a file with progress reporting."""
    print(f"Downloading from {url} to {dest_path}...")
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(
                        f"\rProgress: {downloaded / (1024 * 1024):.1f} MB / "
                        f"{total_size / (1024 * 1024):.1f} MB ({percent:.1f}%)",
                        end="",
                        flush=True,
                    )
    print("\nDownload complete.")


def extract_zip(zip_path: Path, extract_dir: Path) -> Path:
    """Extract zip file and return path to the main CSV file."""
    print(f"Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as z:
        csv_members = [m for m in z.namelist() if m.endswith(".csv")]
        if not csv_members:
            raise FileNotFoundError(f"No CSV file found inside {zip_path}")
        target_csv_name = csv_members[0]
        target_path = extract_dir / target_csv_name
        if not target_path.exists():
            z.extract(target_csv_name, path=extract_dir)
            print(f"Extracted: {target_path}")
        else:
            print(f"CSV already extracted: {target_path}")
        return target_path


def filter_thailand_admin1_monthly(csv_path: Path, output_csv: Path) -> dict:
    """Filter rows for Thailand Admin1 monthly cases using chunking."""
    print(f"Filtering {csv_path.name} for Thailand Admin1 monthly records...")
    total_rows = 0
    tha_rows = 0
    filtered_chunks = []

    # Read in chunks with low_memory=False and dtype=str for adm_2_name to avoid DtypeWarning
    chunk_size = 100000
    for chunk in pd.read_csv(
        csv_path,
        chunksize=chunk_size,
        low_memory=False,
        dtype={"adm_2_name": str},
    ):
        total_rows += len(chunk)
        is_tha = chunk["ISO_A0"] == "THA"
        tha_rows += is_tha.sum()
        mask = is_tha & (chunk["S_res"] == "Admin1") & (chunk["T_res"] == "Month")
        filtered_chunks.append(chunk[mask])

    filtered_df = pd.concat(filtered_chunks, ignore_index=True)
    filtered_df.to_csv(output_csv, index=False)
    print(f"Filtered CSV saved to {output_csv}")

    stats = {
        "total_rows": total_rows,
        "tha_rows": int(tha_rows),
        "filtered_rows": len(filtered_df),
        "columns": list(filtered_df.columns),
        "num_columns": len(filtered_df.columns),
        "nunique_adm_1": int(filtered_df["adm_1_name"].nunique()),
        "min_date": str(filtered_df["calendar_start_date"].min()),
        "max_date": str(filtered_df["calendar_start_date"].max()),
    }
    return stats


def write_source_md(
    source_md_path: Path,
    url: str,
    zip_path: Path,
    sha256_hash: str,
    stats: dict,
    download_date: str,
) -> None:
    """Write provenance and metadata file."""
    content = f"""# OpenDengue Data Provenance

- **Source URL:** {url}
- **Retrieved Date:** {download_date}
- **Local Zip Archive:** `{zip_path.name}` ({zip_path.stat().st_size:,} bytes)
- **SHA-256 Checksum (zip):** `{sha256_hash}`
- **Filtered File:** `{FILTERED_CSV_FILENAME}`

## Data Statistics
- **Total rows in raw dataset:** {stats['total_rows']:,}
- **Total rows for Thailand (`ISO_A0 == 'THA'`):** {stats['tha_rows']:,}
- **Filtered rows (`ISO_A0 == 'THA' & S_res == 'Admin1' & T_res == 'Month'`):** {stats['filtered_rows']:,}
- **Number of columns:** {stats['num_columns']}
- **Columns:** `{', '.join(stats['columns'])}`
- **Unique `adm_1_name` count:** {stats['nunique_adm_1']}
- **Date range (`calendar_start_date`):** {stats['min_date']} to {stats['max_date']}

## License
Content and data provided by OpenDengue are licensed under **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.
- **Source page:** `https://opendengue.org` (verified 2026-11-08)
- **Notice on opendengue.org:**
  > © Copyright 2025 the OpenDengue project
  > The Dengue Mapping and Modelling Group
  > LSHTM, London UK
  > Content licensed under CC BY 4.0 (http://creativecommons.org/licenses/by/4.0/).

## Citations
Please cite the following publications when using this dataset:

1. **Research Paper:**
   Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. (2024). A global dataset of publicly available dengue case count data. *Sci Data* 11(1):296. https://doi.org/10.1038/s41597-024-03120-7

2. **Dataset:**
   Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. (2026). OpenDengue: data from the OpenDengue database. Version [1.3.1]. figshare. https://doi.org/10.6084/m9.figshare.24259573.
"""
    with open(source_md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Source metadata saved to {source_md_path}")


def main():
    raw_dir = get_raw_dir()
    zip_path = raw_dir / ZIP_FILENAME
    filtered_csv_path = raw_dir / FILTERED_CSV_FILENAME
    source_md_path = raw_dir / SOURCE_MD_FILENAME

    download_date = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # 1. Download (Idempotent: skip if zip already exists)
    if zip_path.exists() and zip_path.stat().st_size > 0:
        print(f"Zip archive already exists at {zip_path}, skipping download.")
    else:
        download_file(OPENDENGUE_URL, zip_path)

    # 2. Checksum of zip
    print("Computing SHA-256 checksum of zip archive...")
    sha256_hash = compute_sha256(zip_path)
    print(f"SHA-256: {sha256_hash}")

    # 3. Extract CSV from zip
    extracted_csv_path = extract_zip(zip_path, raw_dir)

    # 4. Filter Thailand Admin1 monthly data
    stats = filter_thailand_admin1_monthly(extracted_csv_path, filtered_csv_path)

    # 5. Write provenance / metadata
    write_source_md(
        source_md_path,
        OPENDENGUE_URL,
        zip_path,
        sha256_hash,
        stats,
        download_date,
    )

    # 6. Verification against SSOT
    print("\n--- Verification Summary ---")
    print(f"Shape: ({stats['filtered_rows']}, {stats['num_columns']})")
    print(f"Unique adm_1_name: {stats['nunique_adm_1']}")
    print(f"Date range: {stats['min_date']} to {stats['max_date']}")

    expected_shape = (27024, 16)
    expected_provinces = 78
    expected_min_date = "1993-01-01"
    expected_max_date = "2022-12-01"

    mismatches = []
    if (stats["filtered_rows"], stats["num_columns"]) != expected_shape:
        mismatches.append(
            f"Shape mismatch: got ({stats['filtered_rows']}, {stats['num_columns']}), expected {expected_shape}"
        )
    if stats["nunique_adm_1"] != expected_provinces:
        mismatches.append(
            f"Province count mismatch: got {stats['nunique_adm_1']}, expected {expected_provinces}"
        )
    if stats["min_date"] != expected_min_date:
        mismatches.append(
            f"Min date mismatch: got {stats['min_date']}, expected {expected_min_date}"
        )
    if stats["max_date"] != expected_max_date:
        mismatches.append(
            f"Max date mismatch: got {stats['max_date']}, expected {expected_max_date}"
        )

    if mismatches:
        print("\nWARNING: Verification discrepancies found:")
        for m in mismatches:
            print(f"  - {m}")
        sys.exit(1)
    else:
        print("\nSUCCESS: All acceptance criteria match SSOT exactly!")


if __name__ == "__main__":
    main()
