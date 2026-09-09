import itertools

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import EngFormatter, PercentFormatter


def vis_volume_momentum(
    volume_df: pd.DataFrame,
    momentum_df: pd.DataFrame,
    periods: tuple[int, ...] = (5, 10, 20, 60),
):
    """Visualize the features returned by ``compute_volume_momentum``.

    ``volume_df`` must contain ``adj_vol`` and use trade dates as its index.
    """
    plot_df = momentum_df.copy()
    plot_df["volume"] = volume_df["adj_vol"]
    # `compute_price_momentum` retains the original index as trade date.
    plot_df["trade_date"] = pd.to_datetime(
        plot_df.index.astype(str),
        format="%Y%m%d",
    )

    x = range(len(plot_df))

    fig, (ax_volume, ax_bias, ax_change, ax_ratio) = plt.subplots(
        4,
        1,
        figsize=(15, 12),
        sharex=True,
        height_ratios=[3, 1, 1, 1],
    )

    # Colouring bars by their relation to the 20-day average makes volume
    # expansion and contraction readable without needing a second series.
    reference_period = 20 if 20 in periods else periods[min(1, len(periods) - 1)]
    reference_ma = plot_df[f"vol_ma_{reference_period}"]
    volume_colors = reference_ma.lt(plot_df["volume"]).map(
        {True: "tab:blue", False: "lightsteelblue"}
    )
    ax_volume.bar(
        x,
        plot_df["volume"],
        width=1.0,
        color=volume_colors,
        alpha=0.65,
        label=f"Volume (blue: above MA {reference_period})",
    )
    for period in periods:
        ax_volume.plot(
            x,
            plot_df[f"vol_ma_{period}"],
            linewidth=1.2,
            label=f"Volume MA {period}",
        )
    ax_volume.set_title("Volume Momentum")
    ax_volume.set_ylabel("Volume")
    ax_volume.yaxis.set_major_formatter(EngFormatter())
    ax_volume.legend(ncol=3, fontsize=9)
    ax_volume.grid(alpha=0.25)

    # Bias expresses unusual volume on a comparable percentage scale.
    display_periods = [p for p in (5, 20, 60) if p in periods]
    for period in display_periods:
        ax_bias.plot(
            x,
            plot_df[f"vol_ma_{period}_bias"],
            linewidth=1.2,
            label=f"Bias vs MA {period}",
        )
    ax_bias.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax_bias.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_bias.set_ylabel("MA bias")
    ax_bias.legend(ncol=3, fontsize=9)
    ax_bias.grid(alpha=0.25)

    # Bars emphasize sudden volume shocks; use 5d and 20d horizons when present.
    change_periods = [p for p in (5, 20) if p in periods]
    for period in change_periods:
        values = plot_df[f"vol_change_{period}d"]
        colors = values.ge(0).map({True: "tab:green", False: "tab:red"})
        ax_change.bar(
            x,
            values,
            width=1.0,
            alpha=0.28 if period == 20 else 0.6,
            color=colors,
            label=f"{period}-day volume change",
        )
    ax_change.axhline(0, color="black", linewidth=0.8, alpha=0.7)
    ax_change.yaxis.set_major_formatter(PercentFormatter(xmax=1))
    ax_change.set_ylabel("Change")
    ax_change.legend(fontsize=9)
    ax_change.grid(alpha=0.25)

    # A ratio above one means short-term participation exceeds long-term trend.
    for short, long in itertools.pairwise(periods):
        ax_ratio.plot(
            x,
            plot_df[f"vol_ma_{short}_{long}_ratio"],
            linewidth=1.2,
            label=f"MA {short} / MA {long}",
        )
    ax_ratio.axhline(1, color="black", linewidth=0.8, linestyle="--", alpha=0.7)
    ax_ratio.set_ylabel("MA ratio")
    ax_ratio.set_xlabel("Trade date")
    ax_ratio.legend(ncol=3, fontsize=9)
    ax_ratio.grid(alpha=0.25)

    step = max(1, len(plot_df) // 16)
    ticks = list(range(0, len(plot_df), step))
    ax_ratio.set_xticks(ticks)
    ax_ratio.set_xticklabels(
        plot_df["trade_date"].dt.strftime("%Y-%m-%d").iloc[ticks],
        rotation=45,
    )

    fig.tight_layout()
    plt.show()
