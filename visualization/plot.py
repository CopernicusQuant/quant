import matplotlib.pyplot as plt
import pandas as pd


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


def vis_rsi(df: pd.DataFrame, periods: tuple[int, ...] = (6, 14)):
    plot_df = df.copy()
    plot_df["trade_date"] = pd.to_datetime(
        plot_df["trade_date"].astype(str),
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
        plot_df["close"],
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


def vis_obv_flow(df: pd.DataFrame):
    plot_df = df.copy()
    plot_df.index = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )

    fig, (ax_price, ax_strength, ax_accel) = plt.subplots(
        3,
        1,
        figsize=(14, 10),
        sharex=True,
        height_ratios=[3, 1, 1],
    )

    # Price panel
    ax_price.plot(
        plot_df.index,
        plot_df["close"],
        label="Close",
        color="black",
        linewidth=1.2,
    )
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    # OBV flow strength:
    # +100% = all rolling volume occurred on up days
    # -100% = all rolling volume occurred on down days
    ax_strength.plot(
        plot_df.index,
        plot_df["obv_flow_strength_5"] * 100,
        label="OBV Strength (5)",
        color="tab:blue",
        linewidth=1.2,
    )
    ax_strength.plot(
        plot_df.index,
        plot_df["obv_flow_strength_20"] * 100,
        label="OBV Strength (20)",
        color="tab:orange",
        linewidth=1.2,
    )
    ax_strength.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax_strength.axhspan(0, 100, color="tab:green", alpha=0.05)
    ax_strength.axhspan(-100, 0, color="tab:red", alpha=0.05)
    ax_strength.set_ylim(-100, 100)
    ax_strength.set_ylabel("Strength (%)")
    ax_strength.legend()
    ax_strength.grid(alpha=0.3)

    # Short-term versus long-term OBV strength acceleration
    ax_accel.bar(
        plot_df.index,
        plot_df["obv_strength_accel_5_20"] * 100,
        label="Strength Accel (5 - 20)",
        color=plot_df["obv_strength_accel_5_20"]
        .ge(0)
        .map({True: "tab:green", False: "tab:red"}),
        alpha=0.55,
        width=1.0,
    )
    ax_accel.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax_accel.set_ylabel("Accel (pp)")
    ax_accel.set_xlabel("Trade Date")
    ax_accel.legend()
    ax_accel.grid(alpha=0.3)

    ax_accel.set_xticks(plot_df.index[::50])
    ax_accel.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()
