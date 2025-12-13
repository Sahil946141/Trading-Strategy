import unittest
from fastapi.testclient import TestClient
from app.main import app
import pandas as pd
from datetime import datetime, timedelta
import random

client = TestClient(app)
# test for input validation
class TestInputValidation(unittest.TestCase):

    def test_missing_fields(self):
        payload = {"datetime": "2025-12-09T10:00:00", "open": 100}
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_wrong_data_types(self):
        payload = {
            "datetime": "2025-12-09T10:00:00",
            "open": "100", "high": "101", "low": "99",
            "close": "100", "volume": "1000"
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_negative_volume(self):
        payload = {
            "datetime": "2025-12-09T10:00:00",
            "open": 100, "high": 101, "low": 99,
            "close": 100, "volume": -10
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_correct_input(self):
        unique_dt = (datetime.now() + timedelta(seconds=random.randint(1,1000))).isoformat()
        payload = {
            "datetime": unique_dt,
            "open": 100, "high": 101, "low": 99,
            "close": 100, "volume": 1000
        }
        response = client.post("/data", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

# test for Api endpoints
class TestAPIEndpoints(unittest.TestCase):

    def test_get_data(self):
        response = client.get("/data")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json()["data"], list)

    def test_strategy_performance_endpoint(self):
        response = client.get("/strategy/performance")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        for key in [
            "strategy", "best_short_sma", "best_long_sma",
            "cumulative_return_percent", "total_buy_signals",
            "total_sell_signals", "buy_dates", "sell_dates"
        ]:
            self.assertIn(key, data)

# test for SMA strategy
class TestSMAConsistency(unittest.TestCase):

    def test_sma_calculation(self):
        prices = [10, 12, 11, 13, 14, 16, 15, 18, 17, 19]
        df = pd.DataFrame({"close": prices})
        df["short"] = df["close"].rolling(3).mean()
        df["long"] = df["close"].rolling(5).mean()

        self.assertEqual(len(df), len(prices))
        self.assertTrue(df["short"].iloc[:2].isna().all())
        self.assertTrue(df["long"].iloc[:4].isna().all())

    def test_signal_generation(self):
        prices = [10, 12, 11, 13, 12, 14, 15, 13, 16, 14]
        df = pd.DataFrame({"close": prices})

        df["short"] = df["close"].rolling(2).mean()
        df["long"] = df["close"].rolling(4).mean()

        df["signal"] = 0
        df.loc[(df["short"] > df["long"]) &
               (df["short"].shift(1) <= df["long"].shift(1)), "signal"] = 1
        df.loc[(df["short"] < df["long"]) &
               (df["short"].shift(1) >= df["long"].shift(1)), "signal"] = -1

        assert 1 in df["signal"].values
        assert -1 in df["signal"].values

    def test_returns(self):
        prices = [10, 12, 11, 13, 14]
        df = pd.DataFrame({"close": prices})
        df["position"] = [0, 1, 1, 0, 1]
        df["returns"] = df["close"].pct_change() * df["position"].shift(1)
        expected = (11-12)/12
        self.assertAlmostEqual(df["returns"].iloc[2], expected)


if __name__ == "__main__":
    unittest.main()
