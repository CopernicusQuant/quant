import matplotlib.pyplot as plt
import pandas as pd


def vis_bollinger_bands(
    stock_df: pd.DataFrame,
    bb_df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
):
    plot_df = stock_df.join(bb_df).copy()
    plot_df = plot_df[-60:]
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )

    fig, (ax_price, ax_position, ax_width) = plt.subplots(
        3,
        1,
        figsize=(14, 10),
        sharex=True,
        height_ratios=[3, 1, 1],
    )

    # Price / Bollinger Bands panel
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["adj_close"],
        label="Close",
        color="black",
        linewidth=1.2,
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["bb_mid"],
        label=f"Middle ({period})",
        color="tab:blue",
        linewidth=1,
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["bb_upper"],
        label=f"Upper (+{std_dev}σ)",
        color="tab:red",
        linewidth=1,
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["bb_lower"],
        label=f"Lower (-{std_dev}σ)",
        color="tab:green",
        linewidth=1,
    )
    ax_price.fill_between(
        plot_df["trade_date"],
        plot_df["bb_lower"],
        plot_df["bb_upper"],
        color="tab:blue",
        alpha=0.12,
        label="Band range",
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    # Price position in the band:
    # 0 = lower band, 0.5 = middle band, 1 = upper band
    ax_position.plot(
        plot_df["trade_date"],
        plot_df["bb_position"],
        label="BB Position",
        color="tab:purple",
    )
    ax_position.axhline(0, color="tab:green", linewidth=1, alpha=0.7)
    ax_position.axhline(0.5, color="tab:blue", linewidth=1, linestyle="--", alpha=0.7)
    ax_position.axhline(1, color="tab:red", linewidth=1, alpha=0.7)
    ax_position.set_ylabel("Position")
    ax_position.legend()
    ax_position.grid(alpha=0.3)

    # Normalized band width
    ax_width.plot(
        plot_df["trade_date"],
        plot_df["bb_width"] * 100,
        label="BB Width",
        color="tab:orange",
    )
    ax_width.set_ylabel("Width (%)")
    ax_width.set_xlabel("Trade Date")
    ax_width.legend()
    ax_width.grid(alpha=0.3)

    ax_width.set_xticks(plot_df["trade_date"].iloc[::2])
    ax_width.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()
