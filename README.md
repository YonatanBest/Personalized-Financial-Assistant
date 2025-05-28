# Personalized Financial Assistant

A smart financial assistant built using AutoGen that helps users manage their finances through API integration and file management capabilities.

## Features

- **Currency Exchange Rate Integration**: Real-time currency conversion using external API
- **Expense Tracking**: Record and categorize expenses
- **Report Generation**: Generate financial reports and summaries
- **File Management**: Export/Import financial data in various formats

## Requirements

- Python 3.9+
- AutoGen
- FastAPI
- SQLite
- Other dependencies (see requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Personalized-Financial-Assistant.git
cd Personalized-Financial-Assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

## Usage

1. Start the application:
```bash
python main.py
```

2. The assistant will guide you through available commands:
- Check currency exchange rates
- Record expenses
- Generate financial reports
- Import/Export financial data

## Project Structure

```
.
├── agents/             # AutoGen agents
├── api/                # API integration
├── data/              # Data storage
├── reports/           # Generated reports
├── utils/             # Utility functions
├── main.py            # Entry point
├── requirements.txt   # Dependencies
└── README.md         # Documentation
```

## License

MIT License