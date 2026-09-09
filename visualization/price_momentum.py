import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter


def vis_price_momentum(
    price_df: pd.DataFrame,
    momentum_df: pd.DataFrame,
    periods: tuple[int, ...] = (5, 10, 20, 60, 120),
):
    plot_df = momentum_df.copy()
    plot_df["close"] = price_df["adj_close"]

    # `compute_price_momentum` retains the original index as trade date.
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )

    fig, (ax_price, ax_bias, ax_return, ax_breadth) = plt.subplots(
        4,
        1,
        figsize=(15, 12),
        sharex=True,
        height_ratios=[3, 1, 1, 1],
    )

    # Price and moving averages
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["close"],
        color="black",
        linewidth=1.4,
        label="Adjusted close",
        zorder=3,
    )
    for period in periods:
        ax_price.plot(
            plot_df["trade_date"],
            plot_df[f"ma_{period}"],
            linewidth=1,
            alpha=0.85,
            label=f"MA {period}",
        )

    ax_price.set_title("Price Momentum")
    ax_price.set_ylabel("Price")
    ax_price.legend(ncol=3, fontsize=9)
    ax_price.grid(alpha=0.25)

    # Distance from moving averages: shows overextension / mean reversion
    display_periods = [p for p in (5, 20, 60) if p in periods]
    for period in display_periods:
        ax_bias.plot(
            plot_df["trade_date"],
            plot_df[f"ma_{period}_bias"],
            linewidth=1.2,
            label=f"Bias vs MA {period}",
        )

    ax_bias.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax_bias.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_bias.set_ylabel("MA bias")
    ax_bias.legend(ncol=3, fontsize=9)
    ax_bias.grid(alpha=0.25)

    # Trailing returns: bars make direction and magnitude easy to scan
    return_periods = [p for p in (5, 20) if p in periods]
    for period in return_periods:
        values = plot_df[f"return_{period}d"]
        colors = values.ge(0).map({True: "tab:green", False: "tab:red"})

        ax_return.bar(
            plot_df["trade_date"],
            values,
            width=1.0,
            alpha=0.28 if period == 20 else 0.6,
            color=colors,
            label=f"{period}-day return",
        )

    ax_return.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax_return.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_return.set_ylabel("Return")
    ax_return.legend(fontsize=9)
    ax_return.grid(alpha=0.25)

    # Breadth of daily upward closes
    ax_breadth.plot(
        plot_df["trade_date"],
        plot_df["up_ratio_5d"],
        color="tab:blue",
        linewidth=1.3,
        label="Up-day ratio (5d)",
    )
    ax_breadth.plot(
        plot_df["trade_date"],
        plot_df["up_ratio_20d"],
        color="tab:orange",
        linewidth=1.3,
        label="Up-day ratio (20d)",
    )
    ax_breadth.axhline(
        0.5,
        color="black",
        linewidth=0.8,
        linestyle="--",
        alpha=0.7,
        label="50%",
    )
    ax_breadth.fill_between(
        plot_df["trade_date"],
        0.5,
        plot_df["up_ratio_20d"],
        where=plot_df["up_ratio_20d"].ge(0.5),
        color="tab:green",
        alpha=0.08,
    )
    ax_breadth.fill_between(
        plot_df["trade_date"],
        0.5,
        plot_df["up_ratio_20d"],
        where=plot_df["up_ratio_20d"].lt(0.5),
        color="tab:red",
        alpha=0.08,
    )

    ax_breadth.set_ylim(0, 1)
    ax_breadth.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_breadth.set_ylabel("Up-day share")
    ax_breadth.set_xlabel("Trade date")
    ax_breadth.legend(ncol=3, fontsize=9)
    ax_breadth.grid(alpha=0.25)

    locator = mdates.AutoDateLocator(minticks=5, maxticks=10)
    ax_breadth.xaxis.set_major_locator(locator)
    ax_breadth.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    fig.tight_layout()
    plt.show()
