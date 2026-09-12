import matplotlib.pyplot as plt
import pandas as pd


def vis_macd(stock_df: pd.DataFrame, macd_df: pd.DataFrame):
    plot_df = stock_df.join(macd_df).copy()
    plot_df = plot_df[plot_df.index >= "20250101"]
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )
    fig, (ax_price, ax_spread) = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=True,
        height_ratios=[3, 1],
    )
    # Price / DEMA panel
    ax_price.plot(
        plot_df["trade_date"], plot_df["adj_close"], label="Close", color="black"
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["macd_ema_fast"],
        label="Fast EMA",
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["macd_ema_slow"],
        label="Slow EMA",
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)
    # Spread panel: multiply by 100 to show percent
    ax_spread.plot(
        plot_df["trade_date"],
        plot_df["macd_diff"],
        label="DIFF",
        color="purple",
    )
    hist_colors = plot_df["macd_hist"].ge(0).map({True: "tab:green", False: "tab:red"})
    ax_spread.bar(
        plot_df["trade_date"],
        plot_df["macd_hist"],
        label="MACD Histogram",
        color=hist_colors,
        alpha=0.45,
        width=1.0,  # one day; adjust if your data frequency differs
    )
    ax_spread.plot(
        plot_df["trade_date"],
        plot_df["macd_dea"],
        label="DEA",
        color="teal",
    )
    ax_spread.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax_spread.set_ylabel("Speed")
    ax_spread.set_xlabel("Trade Date")
    ax_spread.legend()
    ax_spread.grid(alpha=0.3)
    # Signal lines on both panels
    for i, trade_date in enumerate(
        plot_df.loc[plot_df["macd_gold"] == 1, "trade_date"]
    ):
        for ax in (ax_price, ax_spread):
            ax.axvline(
                trade_date,
                color="green",
                linestyle="--",
                alpha=0.7,
                label="Golden cross" if ax is ax_price and i == 0 else None,
            )
    for i, trade_date in enumerate(
        plot_df.loc[plot_df["macd_dead"] == 1, "trade_date"]
    ):
        for ax in (ax_price, ax_spread):
            ax.axvline(
                trade_date,
                color="red",
                linestyle="--",
                alpha=0.7,
                label="Dead cross" if ax is ax_price and i == 0 else None,
            )
    ax_spread.set_xticks(plot_df["trade_date"].iloc[::50])
    ax_spread.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    plt.show()
