# Personalized Financial Assistant

A comprehensive web application that combines financial tools with AI assistance to help users manage their finances effectively.

## Features

- 💰 **Transaction Management**
  - Log income and expenses
  - Categorize transactions
  - View monthly summaries
  - Import/Export transactions via CSV

- 💱 **Currency Tools**
  - Real-time exchange rates
  - Currency conversion calculator
  - Support for major world currencies

- 🪙 **Cryptocurrency**
  - Live cryptocurrency prices
  - Multi-currency display (USD/EUR)
  - Quick price checks for popular coins

- 📊 **Financial Reports**
  - Monthly summary PDFs
  - Category-wise spending analysis
  - Data export in CSV format

- 🤖 **AI Assistant**
  - Natural language interaction
  - Automated function execution
  - Financial insights and advice

## Tech Stack

- Backend: Flask (Python)
- Database: SQLite
- Frontend: HTML, CSS (Bootstrap), JavaScript
- APIs: 
  - ExchangeRate-API for currency conversion
  - CoinGecko API for cryptocurrency prices
  - OpenAI API for AI assistance
- Additional Libraries:
  - Pandas for data handling
  - FPDF for PDF generation
  - SQLAlchemy for database ORM

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/YonatanBest/Personalized-Financial-Assistant.git
   cd Personalized-Financial-Assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key
   ```

5. Initialize the database:
   ```bash
   python
   >>> from functions.db_tools import Base, engine
   >>> Base.metadata.create_all(engine)
   >>> exit()
   ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
financial-assistant/
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── dashboard.html    # Financial dashboard
│   └── ...              # Other templates
├── functions/            # Backend functionality
│   ├── api_tools.py     # External API integrations
│   ├── db_tools.py      # Database operations
│   └── file_tools.py    # File handling (CSV/PDF)
├── llm/                  # AI/LLM functionality
│   └── agent.py         # OpenAI function calling
├── static/              # Static assets
│   └── style.css       # Custom styles
├── database/            # SQLite database
└── exports/            # Generated files (PDF/CSV)
```

## API Keys Required

1. **OpenAI API Key**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key
   - Add to `.env` file as `OPENAI_API_KEY`

2. **ExchangeRate-API Key**
   - Sign up at [ExchangeRate-API](https://www.exchangerate-api.com/)
   - Get your API key
   - Add to `.env` file as `EXCHANGE_RATE_API_KEY`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 