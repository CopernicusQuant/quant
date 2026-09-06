import matplotlib.pyplot as plt
import pandas as pd


def vis_dema(df: pd.DataFrame, fast_period: int = 20, slow_period: int = 60):
    plot_df = df.copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df["trade_date"].astype(str),
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
    ax_price.plot(plot_df["trade_date"], plot_df["close"], label="Close", color="black")
    ax_price.plot(
        plot_df["trade_date"],
        plot_df[f"dema_{fast_period}_{slow_period}_fast"],
        label="Fast DEMA",
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df[f"dema_{fast_period}_{slow_period}_slow"],
        label="Slow DEMA",
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)
    # Spread panel: multiply by 100 to show percent
    ax_spread.plot(
        plot_df["trade_date"],
        plot_df[f"dema_{fast_period}_{slow_period}_spread"] * 100,
        label="DEMA spread",
        color="purple",
    )
    ax_spread.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax_spread.set_ylabel("Spread (%)")
    ax_spread.set_xlabel("Trade Date")
    ax_spread.legend()
    ax_spread.grid(alpha=0.3)
    # Signal lines on both panels
    for i, trade_date in enumerate(
        plot_df.loc[
            plot_df[f"dema_{fast_period}_{slow_period}_gold"] == 1, "trade_date"
        ]
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
        plot_df.loc[
            plot_df[f"dema_{fast_period}_{slow_period}_dead"] == 1, "trade_date"
        ]
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


def vis_macd(df: pd.DataFrame):
    plot_df = df.copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df["trade_date"].astype(str),
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
    ax_price.plot(plot_df["trade_date"], plot_df["close"], label="Close", color="black")
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


def vis_bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2.0,
):
    plot_df = df.copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df["trade_date"].astype(str),
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
        plot_df["close"],
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

    ax_width.set_xticks(plot_df["trade_date"].iloc[::50])
    ax_width.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()


def vis_kdj(df: pd.DataFrame, n: int = 9):
    plot_df = df.copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df["trade_date"].astype(str),
        format="%Y%m%d",
    )

    fig, (ax_price, ax_k) = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=True,
        height_ratios=[3, 1],
    )

    # Price / Bollinger Bands panel
    ax_price.plot(
        plot_df["trade_date"],
        plot_df["close"],
        label="Close",
        color="black",
        linewidth=1.2,
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df[f"kdj_low_{n}"],
        label=f"Low_{n}",
        linewidth=1.2,
    )
    ax_price.plot(
        plot_df["trade_date"],
        plot_df[f"kdj_high_{n}"],
        label=f"High_{n}",
        linewidth=1.2,
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    # Price position between low and high:
    # 0 = 0%, 1 = 100%
    ax_k.plot(
        plot_df["trade_date"],
        plot_df["kdj_k"],
        label="KDJ_K",
        color="tab:purple",
    )
    ax_k.axhline(0, color="tab:green", linewidth=1, alpha=0.7)
    ax_k.axhline(50, color="tab:blue", linewidth=1, linestyle="--", alpha=0.7)
    ax_k.axhline(100, color="tab:red", linewidth=1, alpha=0.7)
    ax_k.set_ylabel("Percentage")
    ax_k.legend()
    ax_k.grid(alpha=0.3)

    ax_k.set_xticks(plot_df["trade_date"].iloc[::50])
    ax_k.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()
