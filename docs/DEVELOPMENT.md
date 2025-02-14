# Development Guide

## Getting Started

### Prerequisites

1. **Development Environment**
   - macOS 10.15 or later
   - Node.js 18+
   - Python 3.8+
   - Visual Studio Code (recommended)

2. **Required Accounts**
   - GitHub account
   - OpenAI API account

### Initial Setup

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/magic-hand-organizer.git
cd magic-hand-organizer
```

2. **Install Dependencies**
```bash
# Node.js dependencies
npm install

# Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env file with your settings
```

## Development Workflow

### 1. Code Organization

```plaintext
src/
├── main/                 # Electron main process
├── renderer/             # React UI components
└── shared/              # Shared utilities
    ├── constants.js
    └── utils.js

python/
├── organizer/           # Python backend
└── prompts/            # AI system prompts

tests/
├── unit/
└── integration/
```

### 2. Branch Strategy

- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `release/*`: Release preparation

### 3. Commit Convention

```plaintext
type(scope): description

- type: feat, fix, docs, style, refactor, test, chore
- scope: main, renderer, ai, etc.
- description: present tense, lowercase
```

Example:
```bash
git commit -m "feat(ai): add new categorization algorithm"
```

## Implementation Guidelines

### 1. File Watcher Implementation

```javascript
// Correct way to implement file watching
const watcher = chokidar.watch(DESKTOP_PATH, {
  ignored: /(^|[\/\\])\../,
  persistent: true,
  ignoreInitial: true,
  awaitWriteFinish: {
    stabilityThreshold: 2000,
    pollInterval: 100
  }
});
```

### 2. AI Integration

```python
# Best practices for AI integration
class AIClassifier:
    def __init__(self):
        self._init_api()
        self._load_prompts()
        self._setup_cache()

    async def classify_file(self, filename):
        try:
            return await self._get_classification(filename)
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return "Uncategorized"
```

### 3. Menu Bar Development

```javascript
// Menu bar implementation guidelines
class MenuBarManager {
  constructor() {
    this.createTray();
    this.setupEventHandlers();
    this.initializeState();
  }

  createTray() {
    // Implementation
  }

  setupEventHandlers() {
    // Implementation
  }
}
```

## Testing

### 1. Unit Testing

```javascript
// Example unit test
describe('FileClassifier', () => {
  beforeEach(() => {
    // Setup
  });

  test('classifies PDF files correctly', async () => {
    const classifier = new FileClassifier();
    const result = await classifier.classify('document.pdf');
    expect(result).toBe('Documents');
  });
});
```

### 2. Integration Testing

```python
# Example integration test
def test_end_to_end_organization():
    # Setup
    organizer = FileOrganizer()
    test_file = create_test_file()

    # Execute
    result = organizer.process_file(test_file)

    # Verify
    assert result.success
    assert file_in_correct_location(test_file)
```

### 3. E2E Testing

```javascript
// Example E2E test
describe('Application Startup', () => {
  test('starts and shows in menu bar', async () => {
    const app = await startApplication();
    expect(await app.isInMenuBar()).toBe(true);
  });
});
```

## Debugging

### 1. Main Process

```javascript
// Launch with debugging
npm run debug:main

// In another terminal
node --inspect-brk ...
```

### 2. Renderer Process

```javascript
// Enable DevTools
win.webContents.openDevTools();
```

### 3. Python Backend

```python
# Add debugging statements
import pdb; pdb.set_trace()
```

## Building

### 1. Development Build

```bash
# Start development server
npm run dev

# Watch for changes
npm run watch
```

### 2. Production Build

```bash
# Build for production
npm run build

# Package application
npm run package
```

## Common Issues

### 1. File Permission Issues

```javascript
// Handle permission errors
try {
  await fs.move(source, target);
} catch (error) {
  if (error.code === 'EACCES') {
    await requestPermissions();
    await fs.move(source, target);
  }
}
```

### 2. AI API Rate Limiting

```python
# Implement rate limiting
class RateLimiter:
    def __init__(self, max_requests=60, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    async def wait_if_needed(self):
        now = time.time()
        self.requests = [req for req in self.requests if now - req < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            wait_time = self.requests[0] + self.time_window - now
            await asyncio.sleep(wait_time)
```

## Performance Optimization

### 1. File Operations

```javascript
// Batch file operations
class BatchProcessor {
  constructor() {
    this.queue = [];
    this.processing = false;
  }

  async add(file) {
    this.queue.push(file);
    if (!this.processing) {
      await this.process();
    }
  }

  async process() {
    this.processing = true;
    while (this.queue.length > 0) {
      const batch = this.queue.splice(0, 10);
      await Promise.all(batch.map(file => this.processFile(file)));
    }
    this.processing = false;
  }
}
```

### 2. Memory Management

```javascript
// Implement cache cleanup
class Cache {
  constructor(maxSize = 1000) {
    this.maxSize = maxSize;
    this.cache = new Map();
  }

  set(key, value) {
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      this.cache.delete(oldestKey);
    }
    this.cache.set(key, value);
  }
}
```

## Deployment

### 1. Release Process

```bash
# 1. Update version
npm version patch/minor/major

# 2. Build application
npm run build

# 3. Create release
npm run release
```

### 2. Auto-Update Configuration

```javascript
// Configure auto-updater
const { autoUpdater } = require('electron-updater');

autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'yourusername',
  repo: 'sparkle-ai-organizer'
});
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests
4. Update documentation
5. Submit pull request

## Resources

- [Electron Documentation](https://www.electronjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Python Documentation](https://docs.python.org)
