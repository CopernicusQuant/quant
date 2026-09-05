# DEMA 特征设计

## 结论

对于 LightGBM 日频量化特征，DEMA 应主要作为**趋势状态的连续描述**，而不是仅作为金叉、死叉交易规则。

第一版建议使用：

```python
spread = dema_fast / dema_slow - 1

result["dema_20_60_spread"] = spread
result["dema_20_60_spread_change_5d"] = spread.diff(5)
```

其中：

| 特征                          | 角色                 | 是否建议首版输入模型   |
| ----------------------------- | -------------------- | ---------------------- |
| `dema_20_60_spread`           | 当前趋势状态与强度   | 是                     |
| `dema_20_60_spread_change_5d` | 趋势增强或减弱的速度 | 可选                   |
| `dema_gold` / `dema_dead`     | 离散的交叉事件       | 否，可用于可视化或研究 |

---

## 指标定义

### DEMA

双重指数移动平均线（DEMA）通过 EMA 及其二次 EMA 降低传统 EMA 的滞后性：

$$
DEMA(t, n) = 2 \times EMA(P, n) - EMA(EMA(P, n), n)
$$

其中，`P` 为价格，`n` 为计算周期。

在趋势跟踪场景中，使用快速 DEMA 与慢速 DEMA 的相对关系描述不同时间尺度下的趋势状态。

### DEMA Spread

推荐使用快、慢 DEMA 的相对差离率：

$$
spread_t = \frac{DEMA_{fast,t}}{DEMA_{slow,t}} - 1
$$

对应实现：

```python
spread = dema_fast / dema_slow - 1
result["dema_spread"] = spread
```

`spread` 的含义如下：

| 状态             | 含义                         |
| ---------------- | ---------------------------- |
| `spread > 0`     | 快速 DEMA 位于慢速 DEMA 上方 |
| `spread < 0`     | 快速 DEMA 位于慢速 DEMA 下方 |
| `spread ≈ 0`     | 两条 DEMA 接近交叉           |
| 较大的正值       | 多头趋势较强                 |
| 绝对值较大的负值 | 空头趋势较强                 |

`spread` 同时保留了趋势方向和趋势强度信息。

---

## 连续特征优先于金叉与死叉

### 金叉与死叉的局限

金叉、死叉可定义为：

```python
dema_gold = (
    (dema_fast.shift(1) < dema_slow.shift(1))
    & (dema_fast > dema_slow)
).astype(int)

dema_dead = (
    (dema_fast.shift(1) > dema_slow.shift(1))
    & (dema_fast < dema_slow)
).astype(int)
```

它们是事件型二元特征。例如：

```text
Day 1: fast < slow
Day 2: fast > slow   → gold = 1
Day 3: fast > slow   → gold = 0
Day 4: fast > slow   → gold = 0
```

模型只能识别 Day 2 发生过金叉，无法从该信号中判断交叉后的趋势强度、持续时间或趋势变化速度。

对于 LightGBM，连续状态变量通常提供更多可学习的信息。因此，应优先使用 `dema_spread`，而不是将其压缩为 `dema_gold` 与 `dema_dead` 等二元变量。

### 与 Spread 的关系

在正常股票价格下，慢速 DEMA 通常大于零，因此：

$$
spread > 0
\iff
DEMA_{fast} > DEMA_{slow}
$$

基于 `spread` 的金叉定义：

```python
(spread.shift(1) <= 0) & (spread > 0)
```

与直接比较快、慢 DEMA 的定义：

```python
(dema_fast.shift(1) <= dema_slow.shift(1)) & (dema_fast > dema_slow)
```

在含义上几乎等价。差异仅在于是否将前一期刚好相等视为交叉；对浮点价格数据而言，这一差异通常很小。

因此，没有必要为了检测金叉而特意将逻辑改写为 `spread`。`spread` 的主要价值在于作为连续特征输入模型。

---

## Spread Change：趋势变化速度

除当前趋势状态外，可使用 `spread` 的变化量表示趋势正在增强还是减弱：

```python
result["dema_spread_change_5d"] = spread.diff(5)
```

其计算形式为：

$$
spread\_change_{5d,t} = spread_t - spread_{t-5}
$$

该特征不表示当前趋势方向，而是表示最近 5 个交易日的趋势变化速度。

| `spread` | `spread_change_5d` | 解读                             |
| -------- | -----------------: | -------------------------------- |
| `+3%`    |              `+2%` | 当前为多头趋势，且趋势正在增强   |
| `+3%`    |              `-2%` | 当前仍为多头趋势，但趋势正在减弱 |
| `-3%`    |              `-2%` | 当前为空头趋势，且趋势正在增强   |
| `-3%`    |              `+2%` | 当前仍为空头趋势，但趋势正在减弱 |

特征分工如下：

```text
spread
→ 当前趋势状态与强度

spread_change
→ 趋势变化速度
```

`dema_spread_change_5d` 是可选增强特征，而非第一版的必要输入。是否保留应通过样本外 ablation test 验证。

---

## 缺失值与 Warm-up Period

调用：

```python
spread.diff(5)
```

会使前 5 行产生 `NaN`。这是因为这些时间点没有可用于计算 $t-5$ 的历史数据。

不建议使用：

```python
fillna(0)
```

原因是两者含义不同：

| 值    | 含义                        |
| ----- | --------------------------- |
| `0`   | 过去 5 天 `spread` 没有变化 |
| `NaN` | 历史数据不足，无法计算      |

LightGBM 可以原生处理缺失值。实践中，指标系统通常在所有特征计算完成后统一移除 warm-up period，例如：

```python
WARMUP_DAYS = 250
```

因此，`diff(5)` 产生的初始缺失值通常不会影响最终训练样本。

---

## DEMA 窗口选择

对于预测未来约 20 个交易日收益的日频系统，`DEMA(20, 60)` 是合理的基准组合：

```text
20 日 ≈ 1 个交易月
60 日 ≈ 1 个季度
```

这两个窗口具有明确且不同的市场时间尺度。

不建议在初始阶段密集搜索高度相近的参数，例如：

```text
20 / 50
20 / 55
20 / 60
20 / 65
20 / 70
```

这些组合之间通常高度相关，容易造成参数过拟合，而不一定带来独立信息。

---

## 单组与多组 DEMA

### 第一版：单组 DEMA

建议先使用单组 20 / 60：

```python
dema_20_60_spread
dema_20_60_spread_change_5d
```

首先验证 DEMA 特征家族本身是否具有增量样本外预测能力。

### 后续扩展：不同时间尺度

如需引入多组 DEMA，应选择明显不同的时间尺度：

```text
10 / 20
→ 短期趋势

20 / 60
→ 中期趋势

60 / 200
→ 长期趋势
```

应避免仅增加多个相近参数组合。

### 多组特征的训练方式

若保留多组 DEMA，应将它们作为不同输入特征同时送入同一个 LightGBM 模型：

```python
features = [
    "dema_10_20_spread",
    "dema_20_60_spread",
    "dema_60_200_spread",
]
```

模型可自行学习：

- 各时间尺度的重要性；
- 短期与长期趋势分别在哪些市场状态下有效；
- 不同时间尺度趋势之间的交互关系。

不需要为每组 DEMA 单独训练模型。单独训练仅适用于研究或 ablation 阶段，用于比较不同特征集合的增量价值。

---

## 推荐开发顺序

### 第一阶段

```python
dema_20_60_spread
```

### 第二阶段

```python
dema_20_60_spread
dema_20_60_spread_change_5d
```

### 第三阶段

在 walk-forward ablation 验证存在增量价值后，再考虑增加明显不同的趋势尺度：

```python
dema_20_60_spread
dema_20_60_spread_change_5d
dema_60_200_spread
```

---

## 验证与可视化建议

### 价格与 DEMA 曲线

用于基础计算校验：

```text
Price
DEMA fast
DEMA slow
Gold / Dead marker
```

重点确认快慢线关系及 crossover 的计算是否正确。

### DEMA Spread 时间序列

绘制：

```text
dema_spread
y = 0
```

可直观验证：

```text
spread > 0  → fast DEMA 位于 slow DEMA 上方
spread < 0  → fast DEMA 位于 slow DEMA 下方
cross 0     → crossover
```

### Spread 分组与未来收益

每天在股票横截面上按 `spread` 分组，例如分为十组：

```text
Q1 ... Q10
```

随后比较各组未来 20 日平均超额收益。若收益与 `spread` 存在较稳定的单调关系，则该特征可能具有预测能力。

### Yearly Rank IC

应按年份观察 `spread` 与未来收益的 Rank IC，而不只观察全样本平均值。

重点判断该特征在多个市场环境下是否保持稳定，而非仅在某一特定时期有效。

---

## 推荐特征集合

当前最适合作为第一版的 DEMA 设计为：

```python
spread = dema_fast / dema_slow - 1

result["dema_20_60_spread"] = spread
result["dema_20_60_spread_change_5d"] = spread.diff(5)
```

推荐的角色划分：

```text
DEMA
- dema_20_60_spread: 当前趋势状态与强度
- dema_20_60_spread_change_5d: 可选的趋势加速度特征

Gold / Dead
- 用于可视化或研究
- 不一定需要输入 LightGBM
```

整体原则是：优先使用连续的趋势状态特征，让 LightGBM 学习何时以及如何利用这些信息；避免将可连续表达的信息过早压缩为金叉、死叉等二元交易信号。
