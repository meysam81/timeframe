# TimeFrame

[![linter](https://github.com/meysam81/timeframe/actions/workflows/linter.yml/badge.svg?branch=main&event=push)](./.pre-commit-config.yaml)
[![tests](https://github.com/meysam81/timeframe/actions/workflows/tests.yml/badge.svg?branch=main)](./tox.ini)
[![codecov](https://codecov.io/gh/meysam81/timeframe/branch/main/graph/badge.svg?token=NM0LMWP0X2)](https://codecov.io/gh/meysam81/timeframe)
[![License](https://img.shields.io/github/license/meysam81/timeframe)](./LICENSE)
[![Open Issues](https://img.shields.io/github/issues-raw/meysam81/timeframe)](https://github.com/meysam81/timeframe/issues)
[![Open PRs](https://img.shields.io/github/issues-pr-raw/meysam81/timeframe)](https://github.com/meysam81/timeframe/pulls)
[![Contributors](https://img.shields.io/github/contributors/meysam81/timeframe)](https://github.com/meysam81/timeframe/graphs/contributors)
[![Version](https://img.shields.io/pypi/v/timeframe)](https://pypi.org/project/timeframe/)
[![Downloads](https://img.shields.io/pypi/dm/timeframe)](https://pypi.org/project/timeframe/)
[![Python](https://img.shields.io/pypi/pyversions/timeframe)](https://pypi.org/project/timeframe/)
[![Wheel](https://img.shields.io/pypi/wheel/timeframe)](https://pypi.org/project/timeframe/)

## Introduction

This package makes the following calculations on `datetime`:

* Adding two time frames, resulting in one bigger time frame or two disjoint one.
* Multiplying two time frames, resuling in either an overlapped time frame or
an empty one, depending on the two time frames.
* Substracting two time frames, resuling in one or several time frames.

## Install

Installing the package is as simple as running the following command inside
your terminal:

```bash
pip install timeframe
```

## Examples

**NOTE**: You can always take a look at the test cases in the [tests](./test)
directory to get a sense of how to use the package, but consider the below
examples first, because it's fairly easy to use.

You need to import `datetime` as well as `TimeFrame`:

```python
from datetime import datetime
from timeframe import TimeFrame
```

### Inclusion

#### New API

```python
>>> tf1 = TimeFrame(datetime(2021, 1, 1), datetime(2021, 1, 2))
>>> tf2 = TimeFrame(datetime(2021, 1, 1, 12), datetime(2021, 1, 1, 13))
>>> tf2 in tf1
True
```

#### Deprecated

This implies whether or not one time frame includes another; it can also be
used to check if a `datetime` is inside one `TimeFrame`.

When you want to check if a `datetime` is inside a `TimeFrame`:

```python
tf1 = TimeFrame(datetime(2021, 1, 26, 19), datetime(2021, 1, 26, 20))
tf1.includes(datetime(2021, 1, 26, 19, 30))
# output: True
```

When You want to check if an instance of `TimeFrame` is inside another one:

```python
tf2 = TimeFrame(datetime(2021, 1, 26, 19, 30), datetime(2021, 1, 26, 19, 40))
tf1.includes(tf2)
# output: True
```

```python
tf3 = TimeFrame(datetime(2021, 1, 26, 19, 45), datetime(2021, 1, 26, 21, 30))
tf1.includes(tf3)
# output: False
```

### Duration

`TimeFrame` has a property named `duration` which can be used to retrieve the
total amount of seconds that `TimeFrame` has:

```python
tf1.duration
# output: 3600.0
```

```python
tf2.duration
# output: 600.0
```

```python
tf3.duration
# output: 6300.0
```

### Comparison

You can always compare two `TimeFrame` to see if one is greater than the other or not.
This comparison is based on the `end` of one `TimeFrame` and the `start` of the other.

```python
tf1 > tf2
# output: False
```

```python
tf3 > tf2
# output: True
```

You can also compare equality using either greater-equal sign, or a simple equal.

```python
tf1 == tf2
# output: False
```

```python
tf3 >= tf2
# output: True
```

### Overlap

When you want to know how much two time frames have in common, use multiply sign:

```python
tf1 * tf2
# output: 2021-01-26T19:30:00#2021-01-26T19:40:00
```

```python
tf2 * tf3
# output: Empty TimeFrame
```

You can also check their duration as well:

```python
(tf1 * tf2).duration
# output: 600.0
```

```python
(tf2 * tf3).duration
# output: 0.0
```

### Summation (union)

The summation sign is used to get the union of two time frames:

```python
tf1 + tf2
# output: 2021-01-26T19:00:00#2021-01-26T20:00:00
```

```python
(tf1 + tf2).duration
# output: 3600.0
```

```python
tf1 + tf3
# output: 2021-01-26T19:00:00#2021-01-26T21:30:00
```

```python
(tf1 + tf3).duration
# output: 9000.0
```

### Minus

You can also substract one time frame from the other, which will ultimately
result in either two disjoint time frames, or one unified time frame, depending
on the time frames.

```python
tf1 - tf2
# output:
# 2021-01-26T19:00:00#2021-01-26T19:29:59.999999
# 2021-01-26T19:40:00.000001#2021-01-26T20:00:00
```

```python
(tf1 - tf2).duration
# output: 2999.999998
```

Substracting two disjoint time frames will return the first time frame as a result.

```python
tf2 - tf3
# output: 2021-01-26T19:30:00#2021-01-26T19:40:00
```

```python
(tf2 - tf3).duration
# output: 600.0
```

```python
(tf2 - tf3) == tf2
# output: True
```

## Acknowledgment

Thank you for showing interest in this package. Feel free to contact me if you
feel like it. 🥂

## Contribution

Any contribution of any size is greatly appreciated. Feel free to open a PR or
issue in the github page at any time. 🤗
