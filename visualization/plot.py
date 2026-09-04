import matplotlib.pyplot as plt
import pandas as pd


def vis_dema(df: pd.DataFrame):
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
    ax_price.plot(plot_df["trade_date"], plot_df["dema_fast"], label="Fast DEMA")
    ax_price.plot(plot_df["trade_date"], plot_df["dema_slow"], label="Slow DEMA")
    ax_price.set_ylabel("Price")
    ax_price.legend()
    ax_price.grid(alpha=0.3)
    # Spread panel: multiply by 100 to show percent
    ax_spread.plot(
        plot_df["trade_date"],
        plot_df["dema_spread"] * 100,
        label="DEMA spread",
        color="purple",
    )
    ax_spread.axhline(0, color="black", linewidth=1, alpha=0.7)
    ax_spread.set_ylabel("Spread (%)")
    ax_spread.set_xlabel("Trade Date")
    ax_spread.legend()
    ax_spread.grid(alpha=0.3)
    # Signal lines on both panels
    for i, trade_date in enumerate(plot_df.loc[plot_df["dema_gold"], "trade_date"]):
        for ax in (ax_price, ax_spread):
            ax.axvline(
                trade_date,
                color="green",
                linestyle="--",
                alpha=0.7,
                label="Golden cross" if ax is ax_price and i == 0 else None,
            )
    for i, trade_date in enumerate(plot_df.loc[plot_df["dema_dead"], "trade_date"]):
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
