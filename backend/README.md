# Dinodial AI Backend API

A FastAPI-based backend system for managing phone calls using Dinodial Proxy API. This system handles call initiation, call management, customer interactions, and automated scheduling.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Poetry (for dependency management)

### Installation

1. **Install dependencies:**
   ```bash
   make install
   ```
   Or manually:
   ```bash
   poetry install
   ```

2. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   DINODIAL_PROXY_BEARER_TOKEN=your_proxy_token_here
   ```

3. **Run the application:**
   ```bash
   make run
   ```
   Or for development with auto-reload:
   ```bash
   make dev
   ```

The API will be available at `http://localhost:8000`

## 📋 How It Works

### Architecture Overview

The system is organized into several modules:

1. **`app.py`** - Main FastAPI application with all API endpoints
2. **`phone_handler.py`** - Handles all call-related operations (initiate, list, details, recordings)
3. **`client_handler.py`** - Manages customer/restaurant flows, webhooks, and CSV operations
4. **`scheduler.py`** - Background scheduler for automated calls
5. **`config.py`** - Configuration variables
6. **`model_config.py`** - AI model configuration and prompts

### Main Endpoint: Initiate Call

**POST** `/api/phone-calls/make-call`

This is the main endpoint to initiate/connect a call. It uses the Dinodial Proxy API.

**Request Body:**
```json
{
  "prompt": "Optional custom AI prompt",
  "evaluation_tool": {
    "name": "call_outcomes",
    "behavior": "BLOCKING",
    "parameters": { ... }
  },
  "vad_engine": "CAWL"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 21,
    "message": "Call Initiated Successfully"
  },
  "status_code": 200
}
```

### Other Call Endpoints

- **GET** `/api/phone-calls/list` - Get list of all calls (with pagination)
- **GET** `/api/phone-calls/{call_id}/detail` - Get detailed information about a specific call
- **GET** `/api/phone-calls/{call_id}/recording-url` - Get recording URL for a call

### Customer Management Endpoints

- **POST** `/customer` - Create a new customer
- **GET** `/customers` - Get all customers
- **GET** `/customer/{customer_id}` - Get a specific customer
- **POST** `/trigger-call/{customer_id}` - Manually trigger a call for a customer
- **POST** `/webhook/call-result` - Webhook endpoint for call results

### Background Scheduler

The scheduler runs every 5 minutes and automatically:
- Triggers order booking calls for new customers
- Checks for customers past their expected arrival time
- Triggers recovery calls for no-show customers

## 📁 File Structure

```
backend/
├── app.py              # Main FastAPI application
├── phone_handler.py     # Call-related functions (Proxy API)
├── client_handler.py   # Customer/restaurant flows and webhooks
├── scheduler.py        # Background scheduler
├── config.py           # Configuration variables
├── model_config.py     # AI model configuration
├── csv_utils.py        # CSV file operations
├── Makefile           # Build and run commands
└── README.md          # This file
```

## 🔧 Makefile Commands

- `make install` - Install dependencies
- `make run` - Run the application
- `make dev` - Run in development mode (auto-reload)
- `make clean` - Clean Python cache files
- `make help` - Show all available commands

## 🔑 Configuration

All configuration is managed through:
- **Environment variables** (`.env` file)
- **`config.py`** - API endpoints and base URLs
- **`model_config.py`** - Default prompts and AI model settings

## 📝 API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔄 Workflow

1. **Call Initiation**: Use `/api/phone-calls/make-call` to start a call
2. **Call Management**: Use list/detail endpoints to track calls
3. **Webhooks**: Dinodial sends call results to `/webhook/call-result`
4. **Scheduler**: Automatically manages customer follow-ups

## 🛠️ Development

For development with auto-reload:
```bash
make dev
```

This runs the server with `--reload` flag, so changes to code will automatically restart the server.

## 📦 Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- httpx - HTTP client for API calls
- APScheduler - Background task scheduling
- python-dotenv - Environment variable management

## 🐛 Troubleshooting

- **Port already in use**: Change the port in `app.py` or use `--port` flag
- **Missing environment variables**: Ensure `.env` file exists with required tokens
- **Import errors**: Run `make install` to ensure all dependencies are installed

## 📄 License

[Add your license information here]
