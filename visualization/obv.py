import matplotlib.pyplot as plt
import pandas as pd


def vis_obv_flow(stock_df: pd.DataFrame, obv_df: pd.DataFrame):
    plot_df = stock_df.join(obv_df).copy()
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
        plot_df["adj_close"],
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
        plot_df["obv_strength_5"] * 100,
        label="OBV Strength (5)",
        color="tab:blue",
        linewidth=1.2,
    )
    ax_strength.plot(
        plot_df.index,
        plot_df["obv_strength_20"] * 100,
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
