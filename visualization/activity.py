import matplotlib.pyplot as plt
import pandas as pd


def vis_activity_features(
    stock_df: pd.DataFrame,
    feature_df: pd.DataFrame,
    periods: list[int] | None = None,
    quantile_period: int = 60,
) -> None:
    if periods is None:
        periods = [5, 20]

    plot_df = stock_df.join(feature_df)
    plot_df["trade_date"] = stock_df.index
    plot_df = plot_df[plot_df["trade_date"] > "20250101"]
    x = range(len(plot_df))

    fig, (ax_price, ax_amplitude, ax_turnover, ax_score) = plt.subplots(
        4, 1, figsize=(14, 12), sharex=True, height_ratios=[2.5, 1.5, 1.5, 2]
    )

    # 1. price context
    ax_price.plot(
        x, plot_df["adj_close"], label="Adjusted Close", color="black", linewidth=1.2
    )
    ax_price.set_ylabel("Price")
    ax_price.set_title("Market Activity Features")
    ax_price.legend()
    ax_price.grid(alpha=0.3)

    # 2. Intraday range / amplitude and its moving averages
    ax_amplitude.plot(
        x,
        plot_df["amplitude"] * 100,
        label="Intraday Range",
        color="tab:orange",
        alpha=0.65,
    )
    for period in periods:
        ax_amplitude.plot(
            x,
            plot_df[f"amplitude_ma_{period}"] * 100,
            label=f"Range MA ({period})",
            linewidth=1.2,
        )
    ax_amplitude.set_ylabel("Range (%)")
    ax_amplitude.legend(ncol=len(periods) + 1)
    ax_amplitude.grid(alpha=0.3)

    # 3. Turnover and deviation from its moving average
    ax_turnover.bar(
        x,
        plot_df["turnover"],
        label="Turnover",
        color="tab:blue",
        alpha=0.34,
        width=1.0,
    )
    ax_turnover.set_ylabel("Turnover")
    ax_turnover.grid(alpha=0.3)
    ax_turnover_bias = ax_turnover.twinx()
    for period in periods:
        ax_turnover_bias.plot(
            x,
            plot_df[f"turnover_ma_{period}_bias"] * 100,
            label=f"Turnover vs MA ({period})",
            linewidth=1.1,
        )
    ax_turnover_bias.axhline(0, color="black", linewidth=0.8, alpha=0.6)
    ax_turnover_bias.set_ylabel("Turnover Bias(%)")

    handles_left, labels_left = ax_turnover.get_legend_handles_labels()
    handles_right, labels_right = ax_turnover_bias.get_legend_handles_labels()
    ax_turnover.legend(
        handles_left + handles_right,
        labels_left + labels_right,
        loc="upper left",
        ncol=len(periods) + 1,
    )

    # 4. Historical percentiles and combined activity scores
    # ax_score.plot(
    #     x,
    #     plot_df[f"amplitude_quantile_{quantile_period}"],
    #     label="Range Percentile",
    #     color="tab:orange",
    #     alpha=0.7,
    # )
    # ax_score.plot(
    #     x,
    #     plot_df[f"turnover_quantile_{quantile_period}"],
    #     label="Turnover Percentile",
    #     color="tab:blue",
    #     alpha=0.7,
    # )
    ax_score.plot(
        x,
        plot_df[f"activity_score_{quantile_period}"],
        label="High Range + High Turnover",
        color="tab:red",
        linewidth=1.5,
    )
    ax_score.plot(
        x,
        plot_df[f"thin_trade_amplitude_score_{quantile_period}"],
        label="High Range + Low Turnover",
        color="tab:purple",
        linewidth=1.2,
    )
    ax_score.plot(
        x,
        plot_df[f"turnover_without_move_score_{quantile_period}"],
        label="Low Range + High Turnover",
        color="tab:green",
        linewidth=1.2,
    )

    ax_score.set_ylim(0, 1.05)
    ax_score.set_ylabel("Percentile / Score")
    ax_score.set_xlabel("Trade Date")
    ax_score.legend(ncol=2)
    ax_score.grid(alpha=0.3)

    step = max(1, len(plot_df) // 10)
    ticks = list(range(0, len(plot_df), step))
    ax_score.set_xticks(ticks)
    ax_score.set_xticklabels(
        plot_df["trade_date"].iloc[ticks],
        rotation=45,
    )
    fig.tight_layout()
    plt.show()
