# Weather Data Source and Methodology

- **Source API:** Open-Meteo Historical Weather API
- **API Endpoint:** `https://archive-api.open-meteo.com/v1/archive`
- **Date Accessed:** 2026-11-09
- **Parameters Requested:**
  - `start_date`: 1993-01-01
  - `end_date`: 2022-12-31
  - `daily`: `temperature_2m_mean`, `precipitation_sum`, `relative_humidity_2m_mean`
  - `timezone`: `Asia/Bangkok` (UTC+7)
- **Aggregation Window:** 30 years (1993–2022), exactly 360 months per province.
- **Coverage Summary:**
  - Total rows: 27,720
  - Unique provinces: 77
  - Year range: 1993 to 2022
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
  - Latitude span: 6.177906°N to 19.846900°N (all strictly within 5°N–21°N)
  - Longitude span: 98.029960°E to 105.110829°E (all strictly within 97°E–106°E)

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
