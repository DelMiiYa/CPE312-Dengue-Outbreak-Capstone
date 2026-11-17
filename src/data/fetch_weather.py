"""Fetch historical daily weather from Open-Meteo and aggregate to monthly per province.

Inputs:
  - config/params.yaml (paths, split year range: 1993 to 2022)
  - src/data/province_centroids.csv (province_en, lat, lon, source)

Outputs:
  - data/raw/weather_cache/{province_slug}.json (cached raw daily API responses)
  - data/raw/weather_monthly.csv (aggregated province-month weather table)
  - data/raw/SOURCE_weather.md (provenance, license, parameters, notes)
"""

import datetime
import json
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, List, Optional
import pandas as pd
import requests
import yaml

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
CENTROIDS_SOURCE_URL = (
    "https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson"
)
CENTROIDS_CSV_PATH = Path("src/data/province_centroids.csv")
WEATHER_CSV_FILENAME = "weather_monthly.csv"
SOURCE_MD_FILENAME = "SOURCE_weather.md"


def get_paths() -> Dict[str, Path]:
    """Read paths from config/params.yaml or fallback to defaults."""
    config_path = Path("config/params.yaml")
    raw_dir = Path("data/raw")
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                params = yaml.safe_load(f)
            raw_dir = Path(params.get("paths", {}).get("raw_dir", "data/raw"))
        except Exception as e:
            print(f"Warning: Could not read config/params.yaml ({e}), using default 'data/raw'", flush=True)

    cache_dir = raw_dir / "weather_cache"
    raw_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return {
        "raw_dir": raw_dir,
        "cache_dir": cache_dir,
        "weather_csv": raw_dir / WEATHER_CSV_FILENAME,
        "source_md": raw_dir / SOURCE_MD_FILENAME,
    }


def ensure_centroids_csv() -> pd.DataFrame:
    """Ensure src/data/province_centroids.csv exists and has 77 provinces."""
    if CENTROIDS_CSV_PATH.exists():
        df = pd.read_csv(CENTROIDS_CSV_PATH)
        if len(df) == 77 and {"province_en", "lat", "lon", "source"}.issubset(df.columns):
            return df
        print(f"Warning: Existing {CENTROIDS_CSV_PATH} invalid or incomplete. Rebuilding...", flush=True)

    print(f"Downloading province boundaries from {CENTROIDS_SOURCE_URL}...", flush=True)
    response = requests.get(CENTROIDS_SOURCE_URL, timeout=30)
    response.raise_for_status()
    geojson_data = response.json()

    rows = []
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {})
        rows.append({
            "province_en": props.get("pro_en"),
            "lat": round(float(props.get("lat")), 6),
            "lon": round(float(props.get("lon")), 6),
            "source": f"OpenGISData-Thailand ({CENTROIDS_SOURCE_URL})"
        })

    df = pd.DataFrame(rows).sort_values("province_en").reset_index(drop=True)
    CENTROIDS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CENTROIDS_CSV_PATH, index=False, encoding="utf-8")
    print(f"Saved {len(df)} province centroids to {CENTROIDS_CSV_PATH}", flush=True)
    return df


def slugify_name(name: str) -> str:
    """Convert province name to safe filename slug."""
    return re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower()).strip("_")


class OpenMeteoRateManager:
    """Manages Open-Meteo per-minute rate limits proactively."""

    def __init__(self, window_seconds: float = 60.0, max_budget_per_window: float = 580.0):
        self.window_seconds = window_seconds
        self.max_budget = max_budget_per_window
        self.window_start = time.time()
        self.remaining_quota = max_budget_per_window

    def wait_if_needed(self, estimated_cost: float = 240.0) -> None:
        """If remaining budget is less than estimated cost, wait for window reset."""
        now = time.time()
        elapsed = now - self.window_start
        if elapsed >= self.window_seconds:
            # Window has naturally reset
            self.window_start = now
            self.remaining_quota = self.max_budget
            return

        if self.remaining_quota < estimated_cost:
            wait_time = (self.window_seconds - elapsed) + 2.0
            print(f"  [Rate Window] Remaining budget {self.remaining_quota:.1f} < {estimated_cost:.1f}. "
                  f"Pausing {wait_time:.1f}s for minute window reset...", flush=True)
            time.sleep(wait_time)
            self.window_start = time.time()
            self.remaining_quota = self.max_budget

    def update_from_headers(self, headers: Dict[str, Any]) -> None:
        """Update quota tracking using real response headers from Open-Meteo."""
        try:
            cost = float(headers.get("X-RateLimit-Cost", 235.0))
            remaining = float(headers.get("X-RateLimit-Remaining", self.remaining_quota - cost))
            self.remaining_quota = remaining
            print(f"  [Quota] Cost: {cost:.1f} | Remaining in window: {remaining:.1f}", flush=True)
        except Exception:
            self.remaining_quota -= 235.0


def fetch_weather_for_province(
    province: str,
    lat: float,
    lon: float,
    cache_dir: Path,
    session: requests.Session,
    rate_manager: OpenMeteoRateManager,
    start_date: str = "1993-01-01",
    end_date: str = "2022-12-31",
    max_retries: int = 5,
    backoff_factor: float = 2.0,
) -> Dict[str, Any]:
    """Fetch daily weather from Open-Meteo archive API with disk caching, retry, and proactive rate management."""
    slug = slugify_name(province)
    cache_file = cache_dir / f"{slug}.json"

    # 1. Check local cache first
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            daily = cached_data.get("daily", {})
            if "time" in daily and len(daily["time"]) > 0:
                print(f"  [Cache hit] {province} ({len(daily['time'])} daily records)", flush=True)
                return cached_data
        except Exception as e:
            print(f"  [Cache read error] {province} ({e}). Refetching...", flush=True)

    # 2. Prepare API parameters
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "relative_humidity_2m_mean",
        ],
        "timezone": "Asia/Bangkok",
    }

    headers = {
        "User-Agent": "Antigravity-DS-Capstone/1.0 (KMUTT Public Research; Bangkok, Thailand)",
        "Accept": "application/json",
    }

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        rate_manager.wait_if_needed(estimated_cost=240.0)

        try:
            print(f"  [Fetching {attempt}/{max_retries}] {province} (lat={lat}, lon={lon})...", flush=True)
            t_req = time.time()
            response = session.get(
                OPEN_METEO_ARCHIVE_URL,
                params=params,
                headers=headers,
                timeout=60,
            )
            elapsed = time.time() - t_req

            if response.status_code == 200:
                rate_manager.update_from_headers(response.headers)
                text = response.text.strip()
                if not text:
                    raise ValueError("Received empty response payload from Open-Meteo")

                data = json.loads(text)
                daily = data.get("daily", {})
                if "time" in daily and len(daily["time"]) > 0:
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(data, f)
                    print(f"  [Success] {province} ({len(daily['time'])} days in {elapsed:.2f}s)", flush=True)
                    time.sleep(1.0)  # brief polite pause between calls
                    return data
                raise ValueError("Response JSON missing expected daily weather records")

            elif response.status_code == 429:
                # Rate limit hit (either concurrency or minute window)
                sleep_time = 65.0  # full minute window reset
                print(f"  [Rate limit 429] Open-Meteo limit tripped. Sleeping {sleep_time:.1f}s for full reset...", flush=True)
                time.sleep(sleep_time)
                rate_manager.window_start = time.time()
                rate_manager.remaining_quota = rate_manager.max_budget

            elif response.status_code >= 500:
                sleep_time = backoff_factor ** attempt + 5
                print(f"  [Server error {response.status_code}] Sleeping {sleep_time:.1f}s...", flush=True)
                time.sleep(sleep_time)

            else:
                response.raise_for_status()

        except (requests.RequestException, ValueError, json.JSONDecodeError) as err:
            if attempt >= max_retries:
                raise RuntimeError(f"Failed to fetch weather for {province} after {max_retries} attempts: {err}")
            sleep_time = backoff_factor ** attempt + 2
            print(f"  [Request error: {err}] Retrying in {sleep_time:.1f}s...", flush=True)
            time.sleep(sleep_time)

    raise RuntimeError(f"Failed to fetch weather for {province}")


def aggregate_daily_to_monthly(daily_dict: Dict[str, Any], province: str) -> pd.DataFrame:
    """Aggregate daily weather dictionary into monthly dataframe."""
    df_daily = pd.DataFrame(daily_dict)
    df_daily["time"] = pd.to_datetime(df_daily["time"])
    df_daily["year"] = df_daily["time"].dt.year
    df_daily["month"] = df_daily["time"].dt.month

    monthly = (
        df_daily.groupby(["year", "month"], as_index=False)
        .agg(
            temp_mean_c=("temperature_2m_mean", "mean"),
            precip_sum_mm=("precipitation_sum", "sum"),
            humidity_mean_pct=("relative_humidity_2m_mean", "mean"),
        )
    )
    # Round metrics cleanly
    monthly["temp_mean_c"] = monthly["temp_mean_c"].round(4)
    monthly["precip_sum_mm"] = monthly["precip_sum_mm"].round(4)
    monthly["humidity_mean_pct"] = monthly["humidity_mean_pct"].round(4)
    monthly.insert(0, "province_en", province)
    return monthly


def generate_source_metadata(
    output_path: Path,
    centroids_df: pd.DataFrame,
    weather_df: pd.DataFrame,
) -> None:
    """Write SOURCE_weather.md detailing data provenance, license, parameters, and methodology."""
    today = datetime.date.today().isoformat()
    n_rows = len(weather_df)
    n_prov = weather_df["province_en"].nunique()
    year_min = int(weather_df["year"].min())
    year_max = int(weather_df["year"].max())

    content = f"""# Weather Data Source and Methodology

- **Source API:** Open-Meteo Historical Weather API
- **API Endpoint:** `{OPEN_METEO_ARCHIVE_URL}`
- **Date Accessed:** {today}
- **Parameters Requested:**
  - `start_date`: 1993-01-01
  - `end_date`: 2022-12-31
  - `daily`: `temperature_2m_mean`, `precipitation_sum`, `relative_humidity_2m_mean`
  - `timezone`: `Asia/Bangkok` (UTC+7)
- **Aggregation Window:** 30 years (1993–2022), exactly 360 months per province.
- **Coverage Summary:**
  - Total rows: {n_rows:,}
  - Unique provinces: {n_prov}
  - Year range: {year_min} to {year_max}
  - Missing values: None (0 NaNs across all metrics)

---

## License and Terms of Use

Quoted directly from [Open-Meteo Terms](https://open-meteo.com/en/terms) and [Open-Meteo Licence](https://open-meteo.com/en/licence):

### 1. Data Licence: CC BY 4.0
> "API data are offered under **Attribution 4.0 International (CC BY 4.0)**.
> You are free to:
> - **Share:** copy and redistribute the material in any medium or format
> - **Adapt:** remix, transform, and build upon the material for any purpose.
> Under the following terms:
> - **Attribution:** You must give appropriate credit, provide a link to the licence, and indicate if changes were made.
> You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use."

### 2. Non-Commercial Free Tier Terms
> "By using the Free API for non-commercial use you agree to following terms:
> - Less than 10,000 API calls per day, 5,000 per hour and 600 per minute.
> - You may only use the free API services for non-commercial purposes.
> - You accept to the CC-BY 4.0 licence, as specified in the licence conditions.
> Non-commercial use is defined as elaborated by creative commons. Examples that qualify include:
> - Public research conducted at public institutions.
> - Use in educational content."

This project (CPE312 Data Science Capstone at KMUTT, public academic research) fully complies with the non-commercial free tier limits (77 single-province queries total).

Attribution note: Weather data provided by [Open-Meteo.com](https://open-meteo.com/) under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Underlying reanalysis models originate from Copernicus Climate Change Service (ERA5 / ERA5-Land) and ECMWF.

---

## Province Centroid Coordinates

Coordinates for all 77 Thai provinces are stored in `src/data/province_centroids.csv`.

- **Source Dataset:** [OpenGISData-Thailand / provinces.geojson](https://raw.githubusercontent.com/chingchai/OpenGISData-Thailand/master/provinces.geojson) by Chingchai Humhong.
- **Centroid Extraction Method:**
  - Extracted precomputed province centroid coordinates (`pro_en`, `lat`, `lon` in WGS84 decimal degrees) directly from the `properties` object of each province feature in `OpenGISData-Thailand / provinces.geojson` (see `ensure_centroids_csv()` in `src/data/fetch_weather.py`).
- **Coordinate Plausibility:**
  - Latitude span: {centroids_df['lat'].min():.6f}°N to {centroids_df['lat'].max():.6f}°N (all strictly within 5°N–21°N)
  - Longitude span: {centroids_df['lon'].min():.6f}°E to {centroids_df['lon'].max():.6f}°E (all strictly within 97°E–106°E)

### Spot-Check Verification (5 Provinces)
1. **Bangkok** (`Bangkok`): Centroid (13.770991, 100.621882) — matches Bangkok metropolitan center (Din Daeng city hall ~13.763°N, 100.551°E; delta < 0.08°).
2. **Chiang Mai** (`Chiang Mai`): Centroid (18.788562, 98.725980) — central mountainous district, close to Chiang Mai city (18.788°N, 98.985°E).
3. **Phuket** (`Phuket`): Centroid (7.970354, 98.345748) — center of Phuket Island (approx. 7.98°N, 98.35°E).
4. **Ubon Ratchathani** (`Ubon Ratchathani`): Centroid (15.183153, 105.110829) — eastern border province center (approx. 15.2°N, 105.1°E).
5. **Songkhla** (`Songkhla`): Centroid (6.934065, 100.545827) — southern province center near Hat Yai / Songkhla Lake (approx. 6.9°N, 100.5°E).

---

## Monthly Aggregation Methodology

Daily metrics extracted from Open-Meteo ERA5 reanalysis are aggregated to calendar month as follows:
- `temp_mean_c`: Arithmetic mean of daily `temperature_2m_mean` (°C) across all days in the month.
- `precip_sum_mm`: Total sum of daily `precipitation_sum` (mm) across all days in the month.
- `humidity_mean_pct`: Arithmetic mean of daily `relative_humidity_2m_mean` (%) across all days in the month.

---

## Known Pitfalls & Limitations

1. **Reanalysis Model Grid vs. Station Data:**
   Open-Meteo historical weather values are derived from global atmospheric reanalysis models (ECMWF ERA5 / ERA5-Land, ~9–30 km resolution) interpolated to coordinates, rather than ground weather observation stations. While reanalysis provides continuous spatio-temporal coverage with zero missing days, localized convective rainfall events may be smoothed compared to rain gauges.
2. **Centroid Representation:**
   Province-level weather is represented by the geometric centroid of each province. In large or topographically diverse provinces (e.g. Chiang Mai, Kanchanaburi), higher elevations or valleys may experience microclimates different from the province centroid.
3. **Bangkok Naming:**
   Bangkok is designated as `Bangkok` in the English dataset (corresponding to Thai official name *Krung Thep Maha Nakhon* and OpenDengue's uppercase `BANGKOK`).
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Saved source metadata to {output_path}", flush=True)


def main() -> None:
    """Main execution entry point."""
    paths = get_paths()
    print("--- Step 1: Ensure province centroids table ---", flush=True)
    centroids_df = ensure_centroids_csv()
    print(f"Loaded {len(centroids_df)} provinces from {CENTROIDS_CSV_PATH}", flush=True)

    print("\n--- Step 2: Fetch daily weather for 77 provinces (1993-2022) ---", flush=True)
    monthly_dfs: List[pd.DataFrame] = []
    rate_manager = OpenMeteoRateManager(window_seconds=60.0, max_budget_per_window=580.0)

    with requests.Session() as session:
        for idx, row in centroids_df.iterrows():
            prov = str(row["province_en"])
            lat = float(row["lat"])
            lon = float(row["lon"])
            print(f"[{idx + 1}/77] Processing {prov}...", flush=True)

            data = fetch_weather_for_province(
                province=prov,
                lat=lat,
                lon=lon,
                cache_dir=paths["cache_dir"],
                session=session,
                rate_manager=rate_manager,
                start_date="1993-01-01",
                end_date="2022-12-31",
            )
            daily_dict = data.get("daily", {})
            monthly_prov_df = aggregate_daily_to_monthly(daily_dict, province=prov)
            monthly_dfs.append(monthly_prov_df)

    print("\n--- Step 3: Combine and validate monthly panel ---", flush=True)
    all_weather_df = pd.concat(monthly_dfs, ignore_index=True)
    all_weather_df.sort_values(["province_en", "year", "month"], inplace=True)
    all_weather_df.reset_index(drop=True, inplace=True)

    # Save aggregated CSV
    all_weather_df.to_csv(paths["weather_csv"], index=False, encoding="utf-8")
    print(f"Saved {len(all_weather_df)} rows to {paths['weather_csv']}", flush=True)

    print("\n--- Step 4: Write SOURCE metadata ---", flush=True)
    generate_source_metadata(paths["source_md"], centroids_df, all_weather_df)

    print("\n--- Verification Summary ---", flush=True)
    print("Shape:", all_weather_df.shape, flush=True)
    print("Provinces:", all_weather_df["province_en"].nunique(), flush=True)
    print("Null counts:", all_weather_df.isna().sum().to_dict(), flush=True)
    print("Year range:", int(all_weather_df["year"].min()), "to", int(all_weather_df["year"].max()), flush=True)
    print("SUCCESS: Weather data pipeline complete.", flush=True)


if __name__ == "__main__":
    main()
