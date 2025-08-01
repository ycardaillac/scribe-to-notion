# Scribe to Notion

Import Amazon Scribe notes to Notion pages with a clean, testable architecture.

## Features

- ✅ **Parse Amazon Scribe clippings** from `My Clippings.txt` files
- ✅ **Import highlights to Notion** with proper formatting
- ✅ **Clean Architecture** with dependency injection and interfaces
- ✅ **Command-line interface** for easy usage

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd scribe-to-notion

# Install dependencies
poetry install
```

## Usage

### Command Line Interface

The easiest way to use this tool is via the CLI:

```bash
# Import clippings to Notion
poetry run scribe-to-notion /path/to/My\ Clippings.txt --parent-page-id YOUR_PAGE_ID
```

### Environment Setup

You'll need a Notion API token. You can set it as an environment variable:

```bash
export NOTION_API_TOKEN="your_notion_api_token_here"
```

Or pass it directly to the command:

```bash
poetry run scribe-to-notion clippings.txt --parent-page-id YOUR_PAGE_ID --api-token your_token
```

### Getting Your Notion API Token

1. Go to [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "Scribe to Notion")
4. Select the workspace where you want to create pages
5. Copy the "Internal Integration Token"

### Connecting Your Integration to Pages

After creating the integration, you need to connect it to the pages where you want to create book pages:

1. Open the Notion page where you want to create book pages
2. Click the **•••** menu in the top right corner
3. Go to **Connections** → **Add connections**
4. Browse and select your "Scribe to Notion" integration
5. Click **Confirm** to add the connection

**Important**: The integration must be connected to the parent page before you can create subpages there!

### Getting Your Parent Page ID

1. Open the Notion page where you want to create book pages
2. Copy the page ID from the URL: `https://notion.so/your-page-id-here`
3. Use this ID as the `--parent-page-id` parameter

## Development

### Running Tests

```bash
# Run unit tests
poetry run pytest

# Run integration tests (requires API token)
poetry run pytest tests/integration/
```

### Setting Up Integration Tests

Integration tests require a Notion API token and parent page ID. To set them up:

1. Copy the template file:
   ```bash
   cp tests/integration/config.py.template tests/integration/config.py
   ```

2. Edit `tests/integration/config.py` and add your actual values:
   ```python
   NOTION_API_TOKEN = "your_actual_api_token_here"
   PARENT_PAGE_ID = "your_actual_parent_page_id_here"
   ```

**Note**: The `config.py` file is ignored by Git to keep your API token secure.


### Project Structure

```
scribe-to-notion/
├── scribe_to_notion/
│   ├── core/           # Business logic and interfaces
│   ├── adapters/       # External service implementations
│   ├── services/       # Use cases and orchestration
│   └── cli/           # Command-line interface
├── tests/
│   ├── unit/          # Unit tests with mocks
│   └── integration/   # Integration tests with real API
└── pyproject.toml
```

### Architecture

This project follows **Clean Architecture** principles:

- **Core**: Domain models and interfaces (no external dependencies)
- **Adapters**: Implementations for external services (Notion API, file parsing)
- **Services**: Business logic orchestration
- **CLI**: User interface layer (Frameworks & Drivers)

## Example Output

```
📖 Parsing clippings from: My Clippings.txt
✅ Found 15 total clippings
✅ Found 13 highlights
📚 Found 2 books with highlights:
   • Sauve-moi (French Edition) (Musso, Guillaume): 1 highlights
   • The Hard Thing About Hard Things: 12 highlights

🚀 Importing to Notion parent page: 23f7f0222e4480bda4dcd63eb26bc655

✅ Import completed successfully!
📄 Created 2 book pages:
   • Sauve-moi (French Edition) (Musso, Guillaume)
     📄 Page ID: 2417f022-2e44-8107-9674-c39ecf795dd9
     🔗 URL: https://notion.so/2417f0222e4481079674c39ecf795dd9
   • The Hard Thing About Hard Things
     📄 Page ID: 2417f022-2e44-8163-b375-ed92b6bd09e0
     🔗 URL: https://notion.so/2417f0222e448163b375ed92b6bd09e0

🎉 All done! Your highlights are now in Notion.
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.

See LICENSE.MIT
