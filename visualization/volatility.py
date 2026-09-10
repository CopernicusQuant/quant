import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter


def vis_volatility(
    stock_df: pd.DataFrame,
    volatility_df: pd.DataFrame,
) -> None:
    plot_df = stock_df.join(volatility_df).copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )
    x = range(len(plot_df))

    # Raw daily rolling standard deviation of returns.
    raw_volatility = plot_df["adj_close"].pct_change().rolling(20).std()

    fig, (ax_price, ax_volatility, ax_rank) = plt.subplots(
        3,
        1,
        figsize=(15, 10),
        sharex=True,
        height_ratios=[2.5, 1.5, 1.5],
    )

    ax_price.plot(x, plot_df["adj_close"], color="black", label="Adjusted close")
    ax_price.set_ylabel("Price")
    ax_price.set_title("Raw Rolling Volatility")
    ax_price.grid(alpha=0.3)
    ax_price.legend()

    ax_volatility.plot(
        x,
        raw_volatility,
        color="tab:orange",
        label="20-day daily volatility",
    )
    ax_volatility.set_ylabel("Daily volatility")
    ax_volatility.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_volatility.grid(alpha=0.3)
    ax_volatility.legend()

    ax_rank.plot(
        x,
        plot_df["volatility_rank"],
        color="tab:purple",
        label="Volatility percentile",
    )
    ax_rank.set_ylim(0, 1.05)
    ax_rank.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_rank.set_ylabel("Percentile")
    ax_rank.set_xlabel("Trade date")
    ax_rank.grid(alpha=0.3)
    ax_rank.legend()

    step = max(1, len(plot_df) // 10)
    ticks = list(range(0, len(plot_df), step))
    ax_rank.set_xticks(ticks)
    ax_rank.set_xticklabels(
        plot_df["trade_date"].dt.strftime("%Y-%m-%d").iloc[ticks],
        rotation=45,
    )

    fig.tight_layout()
    plt.show()
