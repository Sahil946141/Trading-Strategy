from fastapi import APIRouter, HTTPException
from app.db import get_connection
import pandas as pd

router = APIRouter()

@router.get("/strategy/performance")
def sma_strategy_performance():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT datetime, close
            FROM price_data
            ORDER BY datetime ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        if not rows:
            raise HTTPException(404, "No price data available.")
        
        df = pd.DataFrame(rows, columns=["datetime", "close"])

        df["datetime"] = pd.to_datetime(df["datetime"])

        df["close"] = df["close"].astype(float)

        # Startegy
        short_range = range(5,40)
        long_range = range(50,150)

        best_short = None
        best_long = None
        best_return = float("-inf")

        final = df.copy() 

        # first used standard SMA values like 20 and 50, and then added an optimization loop that tests different SMA combinations. The code automatically picks the pair that gives the best performance on the data.

        for s in short_range:
            for l in long_range:
                if s >= l:
                    continue
                temp = df.copy()
                temp["short_sma"] = temp["close"].rolling(s).mean()
                temp["long_sma"] = temp["close"].rolling(l).mean()

                # generate signals

                temp["signal"] = 0
                temp.loc[(temp["short_sma"] > temp["long_sma"]) &
                         (temp["short_sma"].shift(1) <= temp["long_sma"].shift(1)), "signal"] = 1

                temp.loc[(temp["short_sma"] < temp["long_sma"]) &

                         (temp["short_sma"].shift(1) >= temp["long_sma"].shift(1)), "signal"] = -1

                # position & Returns
                temp["position"] = temp["signal"].replace(-1, 0).ffill().fillna(0)
                temp["returns"] = temp["close"].pct_change() * temp["position"].shift(1)

                equity = (1 + temp["returns"].fillna(0)).cumprod()

                cumulative_return = (equity.iloc[-1] - 1) * 100
                # track best SMA
                if cumulative_return > best_return:
                    best_return = round(cumulative_return, 2)
                    best_short = s
                    best_long = l
                    final = temp 
        
        # Now use the best parameters found

        cumulative_return = best_return

        # Buy / Sell DATES for the BEST strategy

        buy_dates = final.loc[final["signal"] == 1, "datetime"].dt.strftime("%Y-%m-%d").tolist()
        sell_dates = final.loc[final["signal"] == -1, "datetime"].dt.strftime("%Y-%m-%d").tolist()
        
        # Final json response
        return {
            "strategy": "Simple SMA Crossover With Optimization",
            "best_short_sma": best_short,
            "best_long_sma": best_long,
            "cumulative_return_percent": cumulative_return,
            "total_buy_signals": len(buy_dates),
            "total_sell_signals": len(sell_dates),
            "buy_dates": buy_dates,
            "sell_dates": sell_dates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
