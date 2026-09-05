# Bollinger Bands 特征设计

## 结论

Bollinger Bands 在本项目中应主要作为**价格相对位置**与**波动率状态**的连续特征，而不是简单的“上轨卖、下轨买”交易规则。

第一版建议使用经典的 **20 / 2** 参数组合，并仅保留：

```python
result["bb_width"] = bb_width
result["bb_position"] = bb_position
```

| 特征                      | 角色                            | 是否建议首版输入模型   |
| ------------------------- | ------------------------------- | ---------------------- |
| `bb_position`             | 价格在局部波动区间中的位置      | 是                     |
| `bb_width`                | 归一化波动率、volatility regime | 是                     |
| `upper` / `mid` / `lower` | 价格轨道                        | 否，仅用于可视化或研究 |

---

## 指标定义

经典 Bollinger Bands 由中轨、上轨和下轨组成：

$$
Mid_t = SMA_{period}(Close)_t
$$

$$
Upper_t = Mid_t + k\sigma_t
$$

$$
Lower_t = Mid_t - k\sigma_t
$$

其中，$\sigma_t$ 是 `period` 窗口内收盘价的滚动标准差，$k$ 是标准差倍数。

当前默认参数：

```python
period = 20
std_dev = 2.0
```

对应实现：

```python
mid = close.rolling(window=period).mean()
rolling_std = close.rolling(window=period).std(ddof=0)

upper = mid + rolling_std * std_dev
lower = mid - rolling_std * std_dev
```

`period=20` 约对应一个交易月，`std_dev=2` 是最常用的传统参数组合。

---

## 标准差口径：`ddof=0`

项目中的 Bollinger Bands 使用总体标准差：

```python
rolling_std = close.rolling(window=period).std(ddof=0)
```

而不是 Pandas `rolling().std()` 默认的 `ddof=1`。

对于窗口中 $n$ 个观测值：

$$
Variance = \frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-ddof}
$$

| 设置     | 分母  | 含义       | 标准差大小 |
| -------- | ----- | ---------- | ---------- |
| `ddof=0` | $n$   | 总体标准差 | 较小       |
| `ddof=1` | $n-1$ | 样本标准差 | 较大       |

技术指标通常将当前滚动窗口视为当前可观察到的完整价格区间，因此采用 `ddof=0` 是合理的。更重要的是，项目中 rolling volatility、z-score 与 Bollinger Bands 等相关特征应统一统计口径，以保证数值可比较、回测和生产计算一致。

---

## `bb_width`：归一化波动率特征

定义：

$$
bb\_width_t = \frac{Upper_t-Lower_t}{Mid_t}
$$

对应实现：

```python
bb_width = diff_ul / mid.replace(0, np.nan)
```

其中：

$$
diff\_ul = Upper-Lower = 2k\sigma
$$

因此：

$$
bb\_width = \frac{2k\sigma}{Mid}
$$

当 `std_dev = 2` 时：

$$
bb\_width = 4\frac{\sigma}{Mid}
$$

`bb_width` 本质上是相对价格水平归一化后的波动率。

若只使用绝对带宽：

$$
Upper-Lower
$$

则高价股票会天然获得更大的数值，同一股票跨越不同价格阶段时也难以比较。除以 `mid` 后，特征表示的是：

> Bollinger Band 相对于当前价格水平有多宽。

这使其更适合用于跨股票的横截面模型训练。

### 市场含义

| `bb_width` 状态 | 常见含义                 |
| --------------- | ------------------------ |
| 较低            | 波动收缩、盘整或 squeeze |
| 开始上升        | 波动开始扩张             |
| 较高            | 高波动市场环境           |
| 从高位下降      | 波动重新收缩             |

低 `bb_width` 不是直接的上涨信号，更接近于：

$$
Low\ BBWidth \Rightarrow P(|FutureReturn|\text{ 较大}) \uparrow
$$

即未来发生较大幅度波动的可能性可能提高，但方向仍需结合趋势和动量特征判断。因此，`bb_width` 的主要角色是描述 volatility regime，而不是单独产生方向预测。

---

## `bb_position`：价格位置特征

定义：

$$
bb\_position_t =
\frac{Close_t-Lower_t}{Upper_t-Lower_t}
$$

对应实现：

```python
bb_position = (close - lower) / diff_ul.replace(0, np.nan)
```

典型解释：

| `bb_position` | 含义         |
| ------------: | ------------ |
|           `0` | 价格位于下轨 |
|         `0.5` | 价格位于中轨 |
|           `1` | 价格位于上轨 |
|         `> 1` | 价格突破上轨 |
|         `< 0` | 价格跌破下轨 |

不应将该特征裁剪到 `[0, 1]`。价格突破上、下轨本身具有信息价值；截断会丢失突破幅度的信息。

进一步展开：

$$
bb\_position = 0.5 + \frac{Close-Mid}{2k\sigma}
$$

因此，`bb_position` 本质上是价格相对近期均值的标准化偏离程度，与 z-score 是线性等价的表达。它告诉模型：

> 当前价格在最近一段时间局部价格分布中处于什么位置。

---

## 参数选择：优先研究 `period`

`std_dev = k` 决定上下轨距中轨多少个标准差：

```text
k = 1：带较窄
k = 2：经典 Bollinger Bands
k = 3：带较宽
```

但若 $k$ 对所有样本固定，它对机器学习特征主要是尺度变换。

对于带宽：

$$
bb\_width = 2k\frac{\sigma}{Mid}
$$

改变 $k$ 仅将特征乘以常数。

对于价格位置：

$$
bb\_position = 0.5 + \frac{Close-Mid}{2k\sigma}
$$

改变 $k$ 同样主要是线性缩放偏离项。因此，对 LightGBM 而言，`period` 通常比 `std_dev` 更值得研究。

不建议第一阶段同时生成：

```text
BB(20, 1)
BB(20, 2)
BB(20, 3)
```

这些特征高度冗余。如后续需要多尺度实验，应选择明显不同的窗口：

```text
period = 10 / 20 / 60
```

分别表示短期、月度和季度附近的局部波动区间。

---

## 与 DEMA、MACD 的互补关系

Bollinger Bands 不应被简单解释为“上轨卖、下轨买”。例如，`bb_position > 1` 的含义依赖市场环境：

| 市场环境        | `bb_position > 1` 的可能含义                |
| --------------- | ------------------------------------------- |
| 横盘 / 均值回归 | 价格偏高，可能向均值回归                    |
| 强趋势          | 价格贴近或持续突破上轨，可能代表强 momentum |

这类条件关系适合由 LightGBM 等非线性模型结合其他特征学习。

当前特征家族的职责可以概括为：

| 特征          | 主要信息                   |
| ------------- | -------------------------- |
| DEMA spread   | 趋势方向、趋势强度         |
| MACD / PPO    | 动量及动量变化             |
| `bb_position` | 价格在局部波动区间中的位置 |
| `bb_width`    | 当前波动率 regime          |

Bollinger Bands 补充了 MA、DEMA 与 MACD 相对较少提供的波动率维度。其价值更可能来自特征交互，例如：

```text
DEMA spread > 0
+ bb_position 较高
+ bb_width 开始扩张
→ 可能代表趋势突破

DEMA spread ≈ 0
+ bb_position 较高
+ bb_width 较低
→ 可能更接近横盘环境中的均值回归
```

因此，即使 `bb_width` 单独与未来收益的线性相关性较弱，也不能直接认为其没有预测价值。

---

## 缺失值与除零处理

完整实现：

```python
mid = close.rolling(window=period).mean()
rolling_std = close.rolling(window=period).std(ddof=0)

upper = mid + rolling_std * std_dev
lower = mid - rolling_std * std_dev
diff_ul = upper - lower

result["bb_width"] = diff_ul / mid.replace(0, np.nan)
result["bb_position"] = (close - lower) / diff_ul.replace(0, np.nan)
```

### Warm-up period

前 `period - 1` 行因历史数据不足而无法计算滚动均线和标准差，结果应保留为 `NaN`。

### 零带宽

当滚动窗口中价格完全不变时：

```text
rolling_std = 0
upper = lower
diff_ul = 0
```

此时 `bb_position` 的分母为零，价格在带内的相对位置没有定义。使用：

```python
diff_ul.replace(0, np.nan)
```

会使该结果为 `NaN`，而不会得到 `inf` 或产生除零警告。

同样，不建议把无法计算的 `bb_width` 或 `bb_position` 人为填成 `0`：

| 值    | 含义                             |
| ----- | -------------------------------- |
| `0`   | 真实的零带宽，或价格恰好位于下轨 |
| `NaN` | 历史不足或指标无法定义           |

两者的业务含义不同。LightGBM 可原生处理缺失值；也可在全部特征计算完成后统一移除 warm-up period。

---

## 推荐开发顺序

### 第一阶段

仅保留核心特征：

```text
bb_width
bb_position
```

首先在 walk-forward 样本外验证其增量价值。

### 第二阶段

若特征重要度、SHAP 或 ablation test 显示 Bollinger 特征有稳定贡献，再加入变化特征：

```python
result["bb_width_change_5d"] = bb_width.diff(5)
result["bb_position_change_5d"] = bb_position.diff(5)
```

其中 `bb_width_change_5d` 可以区分相同波动率水平下，市场正处于扩张还是收缩阶段。

### 第三阶段

再考虑多窗口和长期相对位置，例如：

```text
bb_width_10
bb_width_20
bb_width_60
bb_width_percentile_252d
```

`bb_width_percentile_252d` 用于描述当前波动率在该股票过去一年中的相对位置，可能比固定阈值更适合识别 Bollinger squeeze。

每增加一组特征，都应通过样本外 ablation test 验证增量价值，避免无差别扩充高度相关的技术指标。

---

## 验证与可视化建议

### 价格与布林带

绘制：

```text
Close
Middle band
Upper band
Lower band
Band fill area
```

重点确认：

- 中轨是否为 `period` 日均线；
- 上下轨是否与中轨保持对称；
- 带宽是否会随波动率上升而扩张；
- 收盘价突破轨道时，`bb_position` 是否相应大于 `1` 或小于 `0`。

### `bb_position` 时间序列

绘制：

```text
bb_position
y = 0
y = 0.5
y = 1
```

用于直观确认价格相对上、中、下轨的位置关系。

### `bb_width` 时间序列

绘制：

```text
bb_width
```

用于观察波动率收缩、扩张以及可能的 squeeze 阶段。

### 分组与未来收益

每天按 `bb_position` 或 `bb_width` 在股票横截面分组，例如十组：

```text
Q1 ... Q10
```

比较各组未来 20 日平均超额收益，并进一步按趋势或市场状态分层。例如，对 `bb_position` 可分别在 `dema_spread > 0` 与 `dema_spread <= 0` 的样本中验证，以判断其均值回归与趋势延续效应是否依赖市场环境。

也应按年份观察 Rank IC，避免仅依赖全样本平均表现。

---

## 推荐特征集合

第一版：

```python
mid = close.rolling(window=20).mean()
rolling_std = close.rolling(window=20).std(ddof=0)

upper = mid + 2.0 * rolling_std
lower = mid - 2.0 * rolling_std
diff_ul = upper - lower

result["bb_width"] = diff_ul / mid.replace(0, np.nan)
result["bb_position"] = (close - lower) / diff_ul.replace(0, np.nan)
```

整体角色划分：

```text
Bollinger Bands
- bb_position: normalized price-location feature
- bb_width: volatility-regime feature
```

第一阶段不将 `upper`、`mid`、`lower` 作为模型输入，也不将 Bollinger Bands 固化为传统买卖信号。后续是否增加变化率或多周期特征，应以样本外模型结果为依据。
