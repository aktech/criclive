# criclive

**Live cricket scores in your terminal.**

[![PyPI version](https://img.shields.io/pypi/v/criclive.svg)](https://pypi.python.org/pypi/criclive)
[![Test](https://github.com/aktech/criclive/actions/workflows/test.yml/badge.svg)](https://github.com/aktech/criclive/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/criclive.svg)](https://pypi.python.org/pypi/criclive)

## Install

### Using pip

```
pip install criclive
```

### Using pixi

```
git clone https://github.com/aktech/criclive.git
cd criclive
pixi install
```

## Usage

```
criclive
```

```
╒════╤═══════════════════════╤════╤══════════════════════╤══════════╤══════════╕
│    │ Team 1                │    │ Team 2               │ Format   │ Status   │
╞════╪═══════════════════════╪════╪══════════════════════╪══════════╪══════════╡
│  1 │ LHQ                   │ vs │ HYDK                 │ T20      │ Preview  │
├────┼───────────────────────┼────┼──────────────────────┼──────────┼──────────┤
│  2 │ RSA  187/4 (19.6 ov)  │ vs │ NZ  154/8 (19.6 ov)  │ T20      │ RSA won  │
├────┼───────────────────────┼────┼──────────────────────┼──────────┼──────────┤
│  3 │ INDT                  │ vs │ KNSO                 │ T20      │ Preview  │
├────┼───────────────────────┼────┼──────────────────────┼──────────┼──────────┤
│  4 │ SAUS  55/3 (27.6 ov)  │ vs │ VIC                  │ TEST     │ Break    │
├────┼───────────────────────┼────┼──────────────────────┼──────────┼──────────┤
│  5 │ WAR  204/10 (49.3 ov) │ vs │ TIT  209/6 (43.1 ov) │ ODI      │ TIT won  │
├────┼───────────────────────┼────┼──────────────────────┼──────────┼──────────┤
│  6 │ IND  255/5 (19.6 ov)  │ vs │ NZ  159/10 (18.6 ov) │ T20      │ IND won  │
╘════╧═══════════════════════╧════╧══════════════════════╧══════════╧══════════╛
```

## Development

```bash
git clone https://github.com/aktech/criclive.git
cd criclive
pixi install
pixi run start    # run criclive
pixi run test     # run tests
```

## Contributing

Use GitHub's Pull request/issues feature for all contributions.

## License

MIT
