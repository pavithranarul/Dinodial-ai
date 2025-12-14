# Dinodial - Restaurant Voice Agent System

An intelligent restaurant management system that automates customer interactions through AI-powered voice calls. The system handles table reservations, order bookings, arrival confirmations, and automatically sends email confirmations to customers.

## 🎯 Features

- **AI Voice Agent**: Automated phone calls using Dinodial.ai proxy API with natural language processing
- **Customer Management**: CSV-based customer database with CRUD operations
- **Automated Reservations**: Dynamic prompt generation for personalized customer interactions
- **Email Notifications**: Automatic reservation confirmation emails using SMTP
- **Background Scheduler**: Automated call triggering and email processing
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Modern Frontend**: React-based landing page with booking modal
- **Call Monitoring**: Real-time call status tracking and recording URL retrieval
- **Multi-language Support**: Auto-detection and response in customer's language

## 🏗️ Architecture

```
Dinodial/
├── backend/          # FastAPI backend service
│   ├── app.py       # Main FastAPI application
│   ├── phone_handler.py    # Dinodial API integration
│   ├── csv_utils.py        # Customer data management
│   ├── client_handler.py   # Call flow management
│   ├── model_config.py    # AI prompt configuration
│   ├── scheduler.py        # Background job scheduler
│   └── config.py           # Environment configuration
└── frontend/        # React frontend application
    └── src/
        └── components/     # React components
```

## 🛠️ Tech Stack

### Backend

- **Python 3.11+**: Core language
- **FastAPI**: Web framework
- **Poetry**: Dependency management
- **APScheduler**: Background task scheduling
- **httpx**: Async HTTP client
- **Google Gemini API**: LLM for reservation extraction
- **SMTP**: Email delivery

### Frontend

- **React 18**: UI framework
- **Vite**: Build tool
- **CSS**: Styling

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 16+ and npm
- Poetry (for Python dependency management)
- Dinodial.ai API access with bearer token
- Google API key for Gemini
- SMTP credentials for email sending

## 🚀 Setup Instructions

### Backend Setup

1. **Navigate to backend directory**:

   ```bash
   cd backend
   ```

2. **Install dependencies using Poetry**:

   ```bash
   poetry install
   ```

   Or using pip:

   ```bash
   pip install -r requirement.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file in the `backend/` directory:

   ```env
   DINODIAL_PROXY_BEARER_TOKEN=your_dinodial_bearer_token
   GOOGLE_API_KEY=your_google_api_key
   ```

4. **Run the backend server**:

   ```bash
   poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

   Or using the provided scripts:

   ```bash
   ./run.sh          # Production mode
   ./run-dev.sh      # Development mode
   ```

### Frontend Setup

1. **Navigate to frontend directory**:

   ```bash
   cd frontend
   ```

2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **Start development server**:

   ```bash
   npm run dev
   ```

4. **Build for production**:
   ```bash
   npm run build
   ```

## 📡 API Endpoints

### Customer Management

- `POST /customer` - Create a new customer and trigger automatic call

  ```json
  {
    "name": "John Doe",
    "mobile": "+1234567890",
    "email": "john@example.com",
    "customer_id": "RES12345",
    "timestamp": "2024-01-01T12:00:00",
    "admin_token": "optional_token"
  }
  ```

- `GET /customers` - Get all customers
- `GET /customer/{customer_id}` - Get customer by ID

### Phone Call Management

- `POST /api/phone-calls/make-call` - Initiate a voice call

  ```json
  {
    "prompt": "Optional custom prompt",
    "evaluation_tool": {},
    "vad_engine": "CAWL",
    "customer_id": "RES12345"
  }
  ```

- `GET /api/phone-calls/list` - List all calls (supports pagination)

  - Query params: `page`, `limit`

- `GET /api/phone-calls/{call_id}/detail` - Get call details
- `GET /api/phone-calls/{call_id}/recording-url` - Get call recording URL

### Health Check

- `GET /health` - Health check endpoint

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)

- `DINODIAL_PROXY_BASE`: Dinodial proxy API base URL
- `DINODIAL_PROXY_BEARER_TOKEN`: Authentication token (from `.env`)
- `RESTAURANT_NAME`: Restaurant name for prompts and emails
- `GOOGLE_API_KEY`: Google Gemini API key (from `.env`)

### AI Prompt Configuration

The system uses `make-call-request.json` for AI agent configuration:

- **Prompt**: XML-formatted instructions for the voice agent
- **Evaluation Tool**: Structured data extraction schema
- **VAD Engine**: Voice Activity Detection engine (default: CAWL)

Dynamic prompt generation supports customer name substitution using `{{customer_name}}` placeholder.

## 📊 Data Flow

1. **Customer Registration**: Frontend submits customer data → Backend creates CSV entry → Automatic call triggered
2. **Call Execution**: Dinodial.ai processes call → Call status tracked via polling
3. **Reservation Extraction**: Call completion → Regex/JSON/LLM extraction → Validation
4. **Email Notification**: Confirmed reservation → SMTP email sent to customer
5. **Background Processing**: Scheduler monitors calls every 2-5 minutes for automated workflows

## 🔄 Background Scheduler

The system includes automated background tasks:

- **Customer Call Scanning** (every 5 minutes):

  - Triggers order booking calls for new customers
  - Sends arrival confirmation calls for expected arrivals
  - Handles missed customer recovery calls

- **Reservation Email Processing** (every 2 minutes):
  - Scans completed calls
  - Extracts reservation details
  - Sends confirmation emails automatically

## 📧 Email System

The system automatically sends reservation confirmation emails when:

- Call status is "completed"
- Reservation details are confirmed
- Customer email is available

Email includes:

- Customer name
- Reservation date and time
- Number of guests
- Restaurant information

## 🔍 Reservation Extraction

The system uses a multi-tier extraction strategy:

1. **Primary**: Regex extraction from call data JSON
2. **Fallback**: Structured JSON path traversal
3. **Last Resort**: Google Gemini LLM extraction

This ensures high reliability in extracting reservation details from various call response formats.

## 📁 Project Structure

```
Dinodial/
├── backend/
│   ├── app.py                 # FastAPI main application
│   ├── phone_handler.py       # Dinodial API wrapper
│   ├── csv_utils.py           # Customer CSV operations
│   ├── client_handler.py      # Call flow handlers
│   ├── model_config.py        # AI prompt management
│   ├── scheduler.py           # Background jobs
│   ├── config.py              # Configuration
│   ├── make-call-request.json # AI agent config
│   ├── customers.csv          # Customer database
│   ├── pyproject.toml         # Poetry dependencies
│   └── .env                   # Environment variables
└── frontend/
    ├── src/
    │   ├── App.jsx            # Main React component
    │   └── components/        # UI components
    │       ├── Hero.jsx
    │       ├── About.jsx
    │       ├── Menu.jsx
    │       ├── Contact.jsx
    │       └── BookingModal.jsx
    └── package.json           # NPM dependencies
```

## 🧪 Usage Examples

### Create Customer and Trigger Call

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/customer",
        json={
            "name": "Jane Smith",
            "mobile": "+1234567890",
            "email": "jane@example.com"
        }
    )
    print(response.json())
```

### Make Custom Call

```python
response = await client.post(
    "http://localhost:8000/api/phone-calls/make-call",
    json={
        "customer_id": "RES12345",
        "prompt": "Custom greeting message"
    }
)
```

### Get Call Details

```python
response = await client.get(
    "http://localhost:8000/api/phone-calls/12345/detail"
)
```

## 🔐 Security Notes

- Store sensitive tokens in `.env` file (not committed to git)
- Use environment variables for API keys
- Implement proper authentication for production deployments
- Validate and sanitize all user inputs

## 🐛 Troubleshooting

### Common Issues

1. **CSV initialization errors**: Ensure write permissions in backend directory
2. **Call failures**: Verify `DINODIAL_PROXY_BEARER_TOKEN` is set correctly
3. **Email sending fails**: Check SMTP credentials and network connectivity
4. **Scheduler not running**: Ensure scheduler is started in `app.py` lifespan

## 📝 License

This project is proprietary software.

## 👥 Authors

- pavithranarul7@gmail.com
- a.hariharan0007@gmail.com
- hiteshkumarmz16@gmail.com

## 🔗 Related Resources

- [Dinodial.ai Documentation](https://dinodial.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
