import matplotlib.pyplot as plt
import pandas as pd


def vis_kdj(stock_df: pd.DataFrame, kdj_df: pd.DataFrame, n: int = 9):
    plot_df = stock_df.join(kdj_df).copy()
    plot_df = plot_df[-60:]
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
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
        plot_df["adj_close"],
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
    ax_k.plot(
        plot_df["trade_date"],
        plot_df["kdj_d"],
        label="KDJ_D",
        color="teal",
    )
    ax_k.plot(
        plot_df["trade_date"],
        plot_df["kdj_j"],
        label="KDJ_J",
        color="pink",
    )
    ax_k.axhline(0, color="tab:green", linewidth=1, alpha=0.7)
    ax_k.axhline(50, color="tab:blue", linewidth=1, linestyle="--", alpha=0.7)
    ax_k.axhline(100, color="tab:red", linewidth=1, alpha=0.7)
    ax_k.set_ylabel("Percentage")
    ax_k.legend()
    ax_k.grid(alpha=0.3)

    ax_k.set_xticks(plot_df["trade_date"].iloc[::2])
    ax_k.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    plt.show()
