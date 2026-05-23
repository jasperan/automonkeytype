# automonkeytype

Human-like typing automation for monkeytype.com using Playwright and a physics-inspired keystroke engine.

## Stack

- Python 3.10+ with Playwright (browser automation)
- Click (CLI)
- pytest (tests)
- setuptools build backend

## Commands

```bash
# Install in editable mode
pip install -e .
playwright install chromium

# Run
automonkeytype --wpm 100 --errors 0.02
automonkeytype --wpm 120 --mode time --count 60
automonkeytype --mode quote --headless
python -m automonkeytype --wpm 80

# Tests (unit only, no browser)
pytest tests/ -m "not integration and not live and not slow"

# Integration tests (require browser)
pytest tests/ -m integration

# All tests
pytest tests/
```

## Layout

```
automonkeytype/
  cli.py          # Click entry point (--wpm, --errors, --mode, --count, --headless)
  engine.py       # Main typing loop orchestration
  browser.py      # Playwright browser with stealth/anti-detection config
  scraper.py      # MonkeyType DOM word extraction and results parsing
  humanizer.py    # Keystroke delay generation (bigrams, trigrams, fatigue, noise)
  controller.py   # PID WPM controller with rolling window measurement
  keyboard.py     # QWERTY geometry, finger assignments, inter-key distances
  __main__.py     # python -m automonkeytype support
tests/
  conftest.py
  fixtures/
  test_controller.py
  test_humanizer.py
  test_keyboard.py
  test_integration.py
  test_live_smoke.py
  test_ci_workflow.py
```

## Conventions

- Each module owns one concern; cross-module coupling goes through `engine.py`
- pytest markers: `integration` (browser fixture), `live` (live monkeytype.com), `slow`
- Anti-detection: randomized viewport, spoofed navigator, rotated user agents in `browser.py`
- Typing delays computed in `humanizer.py`; PID feedback loop in `controller.py`
- Error injection uses neighboring QWERTY keys, not random characters
