import matplotlib.pyplot as plt
import pandas as pd


def vis_rsi(
    stock_df: pd.DataFrame, rsi_df: pd.DataFrame, periods: tuple[int, ...] = (6, 14)
):
    plot_df = stock_df.join(rsi_df).copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )

    fig, (ax_price, ax_rsi) = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=True,
        height_ratios=[3, 1],
    )

    # Price panel
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["adj_close"],
        label="Close",
        color="black",
        linewidth=1.2,
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    # RSI panel
    for period in periods:
        ax_rsi.plot(
            plot_df["trade_date"],
            plot_df[f"rsi_{period}"],
            label=f"RSI ({period})",
            linewidth=1.2,
        )

    # Conventional RSI reference levels
    ax_rsi.axhline(70, color="tab:red", linestyle="--", linewidth=1, label="Overbought")
    ax_rsi.axhline(30, color="tab:green", linestyle="--", linewidth=1, label="Oversold")
    ax_rsi.axhline(50, color="gray", linestyle=":", linewidth=1, alpha=0.8)

    # Highlight the overbought / oversold ranges
    ax_rsi.axhspan(70, 100, color="tab:red", alpha=0.08)
    ax_rsi.axhspan(0, 30, color="tab:green", alpha=0.08)

    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel("RSI")
    ax_rsi.set_xlabel("Trade Date")
    ax_rsi.legend()
    ax_rsi.grid(alpha=0.3)

    ax_rsi.set_xticks(plot_df["trade_date"].iloc[::50])
    ax_rsi.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()
