# Market Activity 特征设计

## 结论

`compute_activity_features` 使用**日内价格区间**与**换手率**描述市场活动状态。它不判断价格上涨或下跌，而是回答两个独立问题：

1. 当天的价格波动范围相对近期历史处于什么位置？
2. 当天的换手率相对近期历史处于什么位置？

默认输出以 **5 / 20 日**衡量短期与中短期的平滑状态，并以 **60 日滚动窗口**计算历史分位数。三个组合 score 用于区分“高波动且活跃”、“高波动但交易清淡”与“交易活跃但价格变动有限”等状态；它们是连续研究特征，不是方向性交易信号。

| 特征组 | 当前字段 | 主要角色 | 首版模型建议 |
| --- | --- | --- | --- |
| 日内波动范围 | `amplitude`、`amplitude_ma_{period}` | 当日及近期的价格活动程度 | 是 |
| 换手率偏离 | `turnover_ma_{period}_bias` | 当日交易活跃度相对局部常态的变化 | 是 |
| 历史分位数 | `amplitude_quantile_60`、`turnover_quantile_60` | 将活动度标准化到自身近期历史 | 是 |
| 联合状态 | 三个 `*_score_60` | 识别波动与换手的组合状态 | 是，需做消融验证 |

所有字段仅使用当前日和之前的数据。预测未来收益时，特征和目标必须严格按交易时间对齐。

---

## 当前实现与参数

实现需要输入 `adj_high`、`adj_low`、`adj_close` 与 `turnover`，并假设 DataFrame 已按交易日期从早到晚排序：

```python
periods = [5, 20]
quantile_period = 60

prev_close = close.shift(1)
amplitude = (high - low) / prev_close.where(prev_close > 0)

for period in periods:
    result[f"amplitude_ma_{period}"] = amplitude.rolling(
        window=period, min_periods=1
    ).mean()

    turnover_ma = turnover.rolling(window=period, min_periods=1).mean()
    result[f"turnover_ma_{period}_bias"] = (
        turnover / turnover_ma.clip(lower=1e-6) - 1
    )
```

分位数使用当前日包含在内的滚动窗口：

```python
amplitude_quantile = amplitude.rolling(
    window=quantile_period,
    min_periods=40,
).rank(pct=True)

turnover_quantile = turnover.rolling(
    window=quantile_period,
    min_periods=40,
).rank(pct=True)
```

因此，当前实现的分位数表示“今天在最近最多 60 个交易日中的相对排名”，而不是与全市场或全样本的静态排名。

---

## `amplitude`：标准化日内价格区间

定义为：

$$
amplitude_t = \frac{High_t - Low_t}{Close_{t-1}}
$$

其中价格使用复权后的 `adj_high`、`adj_low` 与 `adj_close`。以前一日收盘价作为分母，使不同绝对价格水平的股票具有更可比的尺度。

| `amplitude` 状态 | 含义 |
| --- | --- |
| 较低 | 当日最高价与最低价之间的区间较窄 |
| 较高 | 当日盘中价格分散程度较大 |
| 缺失 | 首日没有前收盘价，或前收盘价无效 |

它衡量的是**范围**，不是方向：收盘大涨、收盘大跌，甚至盘中剧烈波动后收盘基本持平，都可能产生较高的 `amplitude`。

### `amplitude_ma_5` 与 `amplitude_ma_20`

对长度为 $n$ 的窗口：

$$
AmplitudeMA_{n,t} = \frac{1}{n}\sum_{i=t-n+1}^{t} amplitude_i
$$

当前使用 `min_periods=1`，窗口未完整时会使用已有的非缺失历史计算均值。`amplitude_ma_5` 对近期状态更敏感；`amplitude_ma_20` 则更平滑，近似反映一个月的常态波动范围。

---

## `turnover_ma_{period}_bias`：换手率相对常态的偏离

首先计算换手率均值：

$$
TurnoverMA_{n,t} = \frac{1}{n}\sum_{i=t-n+1}^{t} Turnover_i
$$

再计算：

$$
turnover\_ma\_{n}\_bias_t =
\frac{Turnover_t}{\max(TurnoverMA_{n,t}, 10^{-6})} - 1
$$

对应字段：

```text
turnover_ma_5_bias
turnover_ma_20_bias
```

| Bias 状态 | 含义 |
| --- | --- |
| `> 0` | 当日换手率高于近期均值 |
| `< 0` | 当日换手率低于近期均值 |
| `≈ 0` | 当日换手率接近近期常态 |

分母下限 `1e-6` 用于避免零除。若窗口内换手率长期为零，得到的偏离值应结合停牌或数据缺失等数据质量情况解释，而不应自动视作有效的市场信号。

---

## 历史分位数：`amplitude_quantile_60` 与 `turnover_quantile_60`

两项分位数的取值通常在 $(0, 1]$ 内：

| 分位数 | 含义 |
| ---: | --- |
| 接近 `1` | 当前值处于最近 60 日的较高水平 |
| 接近 `0.5` | 当前值约处于近期中位水平 |
| 接近 `0` | 当前值处于最近 60 日的较低水平 |

由于使用 `rank(pct=True)`，若存在相同值，Pandas 会按默认的平均名次处理。因此分位数不是严格的“历史百分位阈值”，而是滚动窗口内的百分比排名。

`min_periods=40` 表示历史样本少于 40 个有效值时输出 `NaN`。对 `amplitude` 而言，首日通常因没有前收盘价而缺失；因此，在没有其他缺失值的情况下，它会比换手率分位数晚一个交易日才可能有效。

---

## 联合活动状态 score

令：

$$
A_t = amplitude\_quantile\_60
$$

$$
T_t = turnover\_quantile\_60
$$

当前生成三个无量纲 score：

| 字段 | 定义 | 高值代表的状态 |
| --- | --- | --- |
| `activity_score_60` | $A_t \times T_t$ | 日内区间高，且换手率高 |
| `thin_trade_amplitude_score_60` | $A_t \times (1-T_t)$ | 日内区间高，但换手率低 |
| `turnover_without_move_score_60` | $(1-A_t) \times T_t$ | 日内区间低，但换手率高 |

这些 score 的理论范围为 $[0, 1]$。乘法意味着只有两个条件同时明显时 score 才会较高；例如高换手但普通振幅不会形成高 `activity_score_60`。

它们不包含收盘方向，故不应将“高区间 + 高换手”直接解释为看涨或看跌。更合理的用途是与趋势、收益、行业、流动性或事件特征交叉分析，随后以样本外测试判断其增量价值。

---

## 特征处理配置

`feature/feature_meta.py` 对当前默认参数生成的字段做了如下配置：

| 字段类别 | 处理 |
| --- | --- |
| `turnover`、`amplitude`、`amplitude_ma_5`、`amplitude_ma_20`、两个换手率 bias | winsorize + 行业中性化 |
| 两个分位数与三个 score | 行业中性化 |

原始幅度和换手率偏离可能含有极端值，因此配置 winsorize；分位数和 score 已有自然边界，当前仅做中性化。若改动 `periods` 或 `quantile_period`，应同步补充新字段的元数据配置。

---

## 可视化

`visualization/activity.py` 的 `vis_activity_features(stock_df, feature_df)` 将原始行情与特征通过 `trade_date` index 对齐后，绘制四个共享横轴的面板：

1. 复权收盘价：提供价格背景；
2. 日内区间及其移动平均：观察短期与中短期波动范围；
3. 换手率柱状图及换手率均线偏离：区分绝对活动量和相对异常程度；
4. 三个联合状态 score：比较当前主要的活动类型。

当前图表仅展示指定日期之后的数据，并以等距序号作为横坐标位置，再显示交易日期标签。调用示例：

```python
stock.set_index("trade_date", inplace=True)
activity_features = compute_activity_features(stock)
vis_activity_features(stock, activity_features)
```

---

## 边界情况与验证建议

- `rolling()` 和 `shift()` 按当前行顺序计算；输入必须按交易日期升序排列。
- `quantile_period` 当前应不小于 `40`，否则固定的 `min_periods=40` 会超过滚动窗口长度而报错。
- 前收盘价非正、缺失的高低价或缺失换手率会传播为 `NaN`；不要将 warm-up 的 `NaN` 直接填为 `0`，因为两者的经济含义不同。
- 不同股票、市场或数据源的换手率口径必须一致，否则横截面比较和行业中性化会失真。
- 使用 walk-forward 或 expanding-window 样本外测试，分别检验原始幅度、换手偏离、分位数与联合 score 的预测增量，并做消融实验以识别与价格动量、成交量动量、波动率特征的冗余。

这些特征描述的是市场活动状态；其是否具有可交易价值，仍需在严格时间对齐、考虑成本与可交易性约束的回测中验证。
