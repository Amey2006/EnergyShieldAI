"""
One-time helper to generate a small synthetic historical Brent price series
so ARIMA/GARCH have something to run against out of the box.
REPLACE data/historical_brent.csv with real EIA historical data when you can -
EIA publishes free daily Brent/WTI spot price series
(https://www.eia.gov/opendata/browser/petroleum/pri/spt).
"""
import os
import numpy as np
import pandas as pd

np.random.seed(42)
n = 500
dates = pd.date_range(end=pd.Timestamp.today(), periods=n, freq="D")
returns = np.random.normal(loc=0.0002, scale=0.015, size=n)
# add a couple of synthetic shock clusters so GARCH has volatility clustering to find
returns[150:160] += np.random.normal(0, 0.04, 10)
returns[400:410] += np.random.normal(0, 0.05, 10)
prices = 80 * np.exp(np.cumsum(returns))

df = pd.DataFrame({"date": dates, "brent_close": prices.round(2)})
out_path = os.path.join(os.path.dirname(__file__), "data", "historical_brent.csv")
df.to_csv(out_path, index=False)
print(f"Wrote {len(df)} rows -> {out_path}")
