# Queue Manager - AIR-AI Oracle

## Overview

The queue manager handles rate-limited API operations (like Ollama calls) with automatic fallback to local-first generation. This ensures the Oracle keeps working even when API limits are hit.

## Features

- **Persistent Queue**: Jobs survive server restarts
- **Priority Levels**: High, normal, low priority processing
- **Rate Limit Tracking**: Per-service limits (configurable)
- **Automatic Fallback**: Returns local results when rate-limited
- **Background Processing**: Processes jobs every 10 seconds automatically

## API Endpoints

### Get Queue Status
```
GET /queue/status
```

Returns:
```json
{
  "pending": 3,
  "completed": 12,
  "failed": 1,
  "fallback": 2,
  "total": 18,
  "processing": false
}
```

### Add Job to Queue
```
POST /queue/add
Content-Type: application/json

{
  "type": "llm_generate",
  "service": "ollama",
  "params": {"prompt": "Generate a mystical reading"},
  "priority": "normal",
  "fallback_local": true
}
```

Returns:
```json
{
  "job_id": "abc123def456",
  "status": "queued",
  "priority": "normal",
  "fallback_enabled": true
}
```

### Get Job Status
```
GET /queue/job/<job_id>
```

### Process Queue (Manual Trigger)
```
POST /queue/process
Content-Type: application/json

{"executor": "mock"}  // Optional, for testing
```

### Clear Queue
```
POST /queue/clear
Content-Type: application/json

{"status": "completed"}  // Optional filter
```

### Retry Failed Jobs
```
POST /queue/retry
```

## Configuration

Rate limits are configured in `queue_manager.py`:

```python
self.rate_limits = {
    "ollama": {"per_minute": 10, "per_hour": 60},
    "openai": {"per_minute": 3, "per_hour": 60},
    "default": {"per_minute": 10, "per_hour": 100}
}
```

## Usage Example (JavaScript)

```javascript
// Add an LLM generation job
const response = await fetch('/queue/add', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    type: 'llm_generate',
    service: 'ollama',
    params: {
      model: 'phi3:mini',
      prompt: 'Generate a mystical oracle reading for a TTRPG session'
    },
    priority: 'normal',
    fallback_local: true
  })
});

const {job_id} = await response.json();

// Check job status
const status = await fetch(`/queue/job/${job_id}`);
const job = await status.json();

if (job.status === 'completed') {
  console.log('Result:', job.result);
} else if (job.status === 'fallback') {
  console.log('Rate limited, using local fallback');
}
```

## Local-First Strategy

When `fallback_local: true`:
1. Queue checks rate limits before API call
2. If rate-limited, job immediately returns fallback status
3. Your app can use local generators (donjon, dice, FFT) instead
4. Job remains in queue for later retry if needed

This means the Oracle **always works** - API enrichment is optional.

## Testing

Run the test suite:
```bash
python app/test_queue.py
```

## Files

- `queue_manager.py` - Core queue logic
- `test_queue.py` - Test suite
- `queue/` - Persistent queue storage (auto-created)
  - `job_queue.json` - Pending/completed jobs
  - `queue_state.json` - Rate limit state
