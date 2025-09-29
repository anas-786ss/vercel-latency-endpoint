from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

def load_telemetry():
    data_path = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
    with open(data_path, "r") as f:
        telemetry_data = json.load(f)
    df = pd.DataFrame(telemetry_data)
    return df

@app.post("/metrics")
async def post_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    df = load_telemetry()
    results = {}

    for region in regions:
        region_df = df[df["region"] == region]
        avg_latency = float(region_df["latency_ms"].mean()) if not region_df.empty else None
        p95_latency = float(np.percentile(region_df["latency_ms"], 95)) if not region_df.empty else None
        avg_uptime = float(region_df["uptime_pct"].mean()) if not region_df.empty else None
        breaches = int((region_df["latency_ms"] > threshold).sum()) if not region_df.empty else None

        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return results
