# Atlas-AI

## Website Text Change Monitor

A Python tool to monitor websites for text changes.

### Features

- Monitor entire webpage or specific text
- Detect changes using content hashing
- Store baseline and track changes over time
- Continuous monitoring mode
- Contextual change detection

### Installation

```bash
pip install -r requirements.txt
```

### Usage

#### Basic Usage

```python
from website_monitor import WebsiteMonitor

# Monitor specific text on a website
monitor = WebsiteMonitor(
    url="https://example.com",
    target_text="Important Text",
    storage_file="monitor_data.json"
)

result = monitor.check_changes()
print(result)
```

#### Command Line

```bash
python website_monitor.py
```

### API

#### `WebsiteMonitor(url, target_text=None, storage_file="website_data.json")`

- `url`: Website URL to monitor
- `target_text`: Specific text to monitor (optional, monitors entire page if None)
- `storage_file`: JSON file to store state

#### `check_changes()`

Returns a dictionary with:
- `changed`: Boolean indicating if content changed
- `message`: Description of the result
- `current_state`: Current content state
- `previous_state`: Previous content state (if changed)

### Examples

1. **Monitor entire website:**
```python
monitor = WebsiteMonitor(url="https://example.com")
result = monitor.check_changes()
```

2. **Monitor specific text:**
```python
monitor = WebsiteMonitor(
    url="https://example.com",
    target_text="Price: $"
)
result = monitor.check_changes()
```

3. **Continuous monitoring:**
```python
import time

monitor = WebsiteMonitor(url="https://example.com")

while True:
    result = monitor.check_changes()
    if result.get('changed'):
        print("Content changed!")
    time.sleep(300)  # Check every 5 minutes
```
