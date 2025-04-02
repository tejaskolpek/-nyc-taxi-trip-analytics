# 🚖 NYC Taxi Trip Analytics – AWS + Power BI

> **Built By:** Tejas  
> **Tech Stack:** AWS, Python, Power BI, Docker

---

## 📌 Project Summary

This project demonstrates an **end-to-end data pipeline** for analyzing NYC Taxi Trip data using **AWS Lambda**, **Glue**, **Athena**, and **Power BI**, all developed and tested in a reproducible **Dockerized local environment**.

The dashboard reveals insights into taxi operations across New York City—including busiest pickup zones, revenue trends, and rider behavior—all powered by cloud-native services.

---

## ⚙️ Architecture Overview

```
                ┌──────────────────────────┐
                │  NYC Taxi Parquet Files  │
                │   (Cloudfront Source)    │
                └────────────┬─────────────┘
                             ↓
             ┌──────────────────────────┐
             │ Lambda (Raw Fetcher)     │
             │ ➜ S3 /taxi/raw/          │
             └────────────┬─────────────┘
                          ↓
          ┌───────────────────────────────┐
          │ Lambda OR Glue (Data Cleaner) │
          │ ➜ S3 /taxi/filtered/          │
          └────────────┬──────────────────┘
                       ↓
         ┌────────────────────────────┐
         │ AWS Glue Crawler           │
         │ ➜ Data Catalog             │
         └────────────┬───────────────┘
                      ↓
             ┌────────────────┐
             │ Amazon Athena  │
             │ ➜ SQL Views    │
             └──────┬─────────┘
                    ↓
         ┌────────────────────────────┐
         │ Power BI (via ODBC Driver) │
         │ ➜ Visual Dashboard         │
         └────────────────────────────┘
```

---

## 💻 Technologies Used

- **AWS Lambda** – Serverless data fetch and filter functions
- **AWS Glue** – Scalable PySpark-based filtering
- **Amazon S3** – Central data lake storage
- **AWS Glue Crawler** – Auto-cataloging of schema
- **Amazon Athena** – SQL querying layer
- **Power BI** – Visual dashboard layer
- **Docker + Anaconda** – Local reproducible dev environment

---

## 🔬 Athena View Examples

```sql
-- View: Top 10 Busiest Pickup Locations
CREATE OR REPLACE VIEW top_10_busiest_pickup_locations AS
SELECT pickup_location_id AS location_id, COUNT(*) AS trip_count
FROM filtered
GROUP BY pickup_location_id
ORDER BY trip_count DESC
LIMIT 10;
```

```sql
-- View: Avg. Trip Distance by Hour
CREATE OR REPLACE VIEW avg_trip_distance_by_hour AS
SELECT HOUR(from_unixtime(cast(pickup_datetime / 1000000000 AS BIGINT))) AS hour_of_day,
       AVG(trip_distance) AS avg_trip_distance
FROM filtered
GROUP BY HOUR(from_unixtime(cast(pickup_datetime / 1000000000 AS BIGINT)))
ORDER BY hour_of_day;
```

---

## 📈 Power BI Dashboard

**Connected to Athena via ODBC driver**. Dashboard includes:
- 📊 Line charts (Revenue trends)
- 🔹 Bar charts (Pickup locations, tip %)
- 📈 Pie/clustered visuals (Passenger counts, trip ranges)
- ⏰ KPI Cards (Zero tip %)
- 📅 Interactive time slicers
- 🌍 Map visualizations with location matching

---

## 🌈 Creativity Elements

- Violin plots with seaborn
- Dynamic slicers and visual cross-filtering
- Distance bucket segmentation in SQL
- Use of KPI cards & animated revenue timeline
- Seamless Docker-powered dev/test

---

## 🔁 Folder Structure

```bash
nyc-taxi-analytics/
├── anaconda-ubuntu/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── shared_folder/
│       ├── lambda_fetch_raw.py
│       ├── lambda_filter_data.py
│       └── notebooks/
├── powerbi/
│   ├── dashboard.pbix
│   └── snapshots/
└── README.md
```

---

## 🚀 Future Enhancements

- Streamed ingestion with AWS Kinesis
- CI/CD Lambda deployment (Terraform/CDK)
- Sentiment analysis from mock feedback
- Geo-location heatmap overlays in Power BI

---

## 📬 Contact

**Tejas**  
✉️ tejkolpek@gmail.com  
🔍 LinkedIn: [linkedin.com/in/yourname](#)  
🐙 GitHub: [github.com/yourhandle](#)

---

**Built with ❤️ using AWS, Python, and Power BI.**

