# Project Setup Guide

## Prerequisites

- Python 3.12.x
- pip (Python package installer)
- Virtual environment tool (venv)

## Initial Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd appointmentsystem
```

2. Set up BWS executable:
   - Download the BWS executable from: https://github.com/bitwarden/sdk-sm/releases/download/bws-v1.0.0/bws-x86_64-pc-windows-msvc-1.0.0.zip
   - Extract the downloaded zip file
   - Create a `tools` directory in the project root if it doesn't exist
   - Copy the `bws.exe` from the extracted files into the `tools` directory

   > **Important**: Do not use the standard BWS installation. This project specifically requires the executable from the above link.

3. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
```

## Environment Configuration

Create a `.env` file in the project root with the following variables:

```dotenv
BWS_ACCESS_TOKEN=[your-bws-access-token]
PROJECT_ID=[your-project-id]
```

These environment variables are required for:
- `BWS_ACCESS_TOKEN`: Authentication token for BWS service
- `PROJECT_ID`: Your project identifier

## Testing

The project uses pytest with several plugins:

### Installed Test Dependencies
```
pytest==8.0.0
pytest-asyncio==0.23.5
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-env==1.1.3
pytest-timeout==2.2.0
pytest-xdist==3.5.0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest src/test/test_bws.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src
```

## Project Structure

```
appointmentsystem/
├── docs/               # Documentation
├── src/               # Source code
│   ├── main/         # Main application code
│   ├── test/         # Test files
│   └── utils/        # Utility functions
├── tools/            # Contains bws.exe
├── .env              # Environment configuration
├── requirements.txt  # Project dependencies
└── test-requirements.txt  # Test dependencies
```

## Troubleshooting

1. **BWS Connection Issues**
   - Verify BWS_ACCESS_TOKEN in .env
   - Ensure bws.exe is correctly placed in the tools directory
   - Confirm you're using the correct BWS executable (from the specified GitHub release)
   - Check network connectivity

2. **Test Failures**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed
   - Check .env configuration
   - Review test logs for specific errors
