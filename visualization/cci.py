import matplotlib.pyplot as plt
import pandas as pd


def vis_cci(
    stock_df: pd.DataFrame,
    cci_df: pd.DataFrame,
    window: int = 14,
    periods: tuple[int, ...] = (5,),
) -> None:
    plot_df = stock_df[["adj_high", "adj_low", "adj_close"]].join(cci_df).copy()
    plot_df = plot_df[plot_df.index > "20260101"]
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )
    x = range(len(plot_df))

    fig, (ax_price, ax_cci) = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=True,
        height_ratios=[3, 1.5],
    )

    # Price inputs used by CCI: high, low, close, and typical-price mean.
    ax_price.fill_between(
        x,
        plot_df["adj_low"],
        plot_df["adj_high"],
        color="tab:blue",
        alpha=0.12,
        label="Daily high–low range",
    )
    ax_price.plot(
        x,
        plot_df["adj_close"],
        color="black",
        linewidth=1.2,
        label="Adjusted close",
    )
    ax_price.plot(
        x,
        plot_df["tp"],
        color="tab:gray",
        linewidth=0.9,
        alpha=0.8,
        label="Typical price (HLC / 3)",
    )
    ax_price.plot(
        x,
        plot_df["tp_sma"],
        color="tab:orange",
        linewidth=1.2,
        label=f"Typical price MA ({window})",
    )

    ax_price.set_title(f"Commodity Channel Index ({window})")
    ax_price.set_ylabel("Price")
    ax_price.legend(ncol=2, fontsize=9)
    ax_price.grid(alpha=0.3)

    # CCI and its smoothed versions.
    ax_cci.plot(
        x,
        plot_df["cci"],
        color="tab:purple",
        linewidth=1.2,
        label="CCI",
    )
    for period in periods:
        column = f"cci_ma_{period}"
        if column in plot_df:
            ax_cci.plot(
                x,
                plot_df[column],
                linewidth=1.1,
                label=f"CCI MA ({period})",
            )

    # Reference levels are context, not direct trading signals.
    ax_cci.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax_cci.axhline(
        100,
        color="tab:red",
        linestyle="--",
        linewidth=0.9,
        label="+100",
    )
    ax_cci.axhline(
        -100,
        color="tab:green",
        linestyle="--",
        linewidth=0.9,
        label="-100",
    )
    ax_cci.axhspan(100, 200, color="tab:red", alpha=0.06)
    ax_cci.axhspan(-200, -100, color="tab:green", alpha=0.06)

    ax_cci.set_ylabel("CCI")
    ax_cci.set_xlabel("Trade date")
    ax_cci.legend(ncol=4, fontsize=9)
    ax_cci.grid(alpha=0.3)

    step = max(1, len(plot_df) // 10)
    ticks = list(range(0, len(plot_df), step))
    ax_cci.set_xticks(ticks)
    ax_cci.set_xticklabels(
        plot_df["trade_date"].dt.strftime("%Y-%m-%d").iloc[ticks],
        rotation=45,
    )

    fig.tight_layout()
    plt.show()
