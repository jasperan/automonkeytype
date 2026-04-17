# automonkeytype

Human-like typing automation for [monkeytype.com](https://monkeytype.com).

Types with realistic dynamics, not just fast, but *convincingly human*:
bigram-aware timing, finger travel distance modeling, fatigue simulation,
error injection with natural corrections, and PID-controlled WPM targeting.

## Features

- **Human-like keystroke timing**: Gaussian-distributed delays calibrated per finger transition, bigram/trigram frequency bonuses, same-finger penalties, hand-alternation speed boosts
- **Keyboard geometry modeling**: full QWERTY layout with row stagger, inter-key distance calculations, finger assignments
- **PID WPM controller**: servo-locks typing speed to your target WPM in real-time with rolling-window measurement
- **Fatigue simulation**: WPM gradually degrades over longer tests, modeling realistic human endurance
- **Realistic error injection**: configurable typo rate using neighboring keys, with human-like reaction time before correction
- **Anti-detection stealth**: randomized viewport, spoofed navigator properties, rotated user agents, disabled automation flags
- **Multiple test modes**: supports words, time, quote, zen, and custom MonkeyType modes

## Installation

<!-- one-command-install -->
> **One-command install**: clone, configure, and run in a single step:
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/jasperan/automonkeytype/main/install.sh | bash
> ```
>
> <details><summary>Advanced options</summary>
>
> Override install location:
> ```bash
> PROJECT_DIR=/opt/myapp curl -fsSL https://raw.githubusercontent.com/jasperan/automonkeytype/main/install.sh | bash
> ```
>
> Or install manually:
> ```bash
> git clone https://github.com/jasperan/automonkeytype.git
> cd automonkeytype
> pip install -e .
> playwright install chromium
> ```
> </details>

## Usage

```bash
# Type at 100 WPM (default) on a 50-word test
automonkeytype

# Type at 150 WPM with 3% error rate
automonkeytype --wpm 150 --errors 0.03

# 60-second timed test at 120 WPM
automonkeytype --wpm 120 --mode time --count 60

# Quote mode, headless browser
automonkeytype --mode quote --headless

# Run as a Python module
python -m automonkeytype --wpm 80 --errors 0.02
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--wpm` | `100` | Target words per minute |
| `--errors` | `0.0` | Typo probability per keystroke (0.0-1.0) |
| `--mode` | `words` | Test mode: words, time, quote, zen, custom |
| `--count` | `50` | Word count (words mode) or seconds (time mode) |
| `--headless` | off | Run browser without visible window |

## How It Works

### Typing Dynamics Engine

Each keystroke delay is computed from multiple factors:

1. **Base delay**: derived from target WPM: `60 / (WPM * 5)` seconds per character
2. **Bigram speed**: 50 common English bigrams (th, he, in, er...) get 15-25% speed boosts modeling muscle memory
3. **Trigram speed**: common trigrams (the, ing, and...) get additional acceleration
4. **Key distance**: Euclidean distance on the physical keyboard layout adds ~4% delay per key-unit of travel
5. **Same-finger penalty**: consecutive keys typed by the same finger add 35% delay (must lift and reposition)
6. **Hand alternation**: switching hands gives a 15% speed boost (overlapping finger motion)
7. **Gaussian noise**: random variation (configurable consistency parameter) prevents robotic regularity
8. **Fatigue**: gradual slowdown over thousands of keystrokes

### PID Speed Controller

A PID controller continuously measures rolling WPM from a sliding window of keystroke timestamps and adjusts a delay multiplier:
- Typing too fast? Multiplier increases, slowing you down
- Typing too slow? Multiplier decreases, speeding you up
- Result: actual WPM locks onto target within a few words

### Error Injection

When enabled, errors use neighboring keys on the QWERTY layout (not random characters) and include realistic reaction time (~300ms) before the backspace correction, because humans don't instantly notice typos.

## Architecture

```
automonkeytype/
├── cli.py          # Click CLI entry point
├── engine.py       # Main typing loop orchestration
├── browser.py      # Playwright browser with stealth config
├── scraper.py      # MonkeyType DOM word extraction & results
├── humanizer.py    # Human-like delay generation (bigrams, fatigue, noise)
├── controller.py   # PID WPM controller with rolling window
└── keyboard.py     # QWERTY layout geometry & finger mapping
```

## License

GPL-3.0. See [LICENSE](LICENSE).
