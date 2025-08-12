# Installation Guide

## Overview

This guide provides step-by-step instructions for installing and setting up the flight alerts system from the GitHub repository.

---

## Prerequisites

Before installing, ensure you have the following:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **pip** for installing Python packages
- **curl** for downloading data files
- **make** utility (optional, for simplified setup)
- Access to required API keys (details in configuration section)

---

## Installation Steps

### Recommended: Using Makefile

The project includes a Makefile that automates the entire setup process.

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/flightAlertsSystem.git
cd flightAlertsSystem
```

#### 2. Complete Setup with Make

```bash
# Complete local setup (virtual environment, dependencies, data download)
make local-setup
```

#### 3. Run the Application

```bash
# Run with complete setup (recommended for first run)
make run

# Run without setup (if already configured)
make run-a
```

---

## Configuration Setup

After completing either installation method, you'll need to configure the application:

### 1. Environment Variables

Create a `.env` file in the root directory with your configuration:

```bash
# Copy example file if available, or create from scratch
cp .env.example .env  # if example exists
# OR
touch .env
```

Add the following environment variables to your `.env` file:

```env
# Currency and Pricing
CURRENCY=BRL                        # string - 3-letter currency code
CURRENCY_SYMBOL=R$                  # string - currency symbol for display
COMMISSION=500                      # integer - commission in cents
CREDIT_CARD_FEE=500                # integer - credit card fee in cents

# API Keys and Service Configuration
OPENAI_API_KEY=your_openai_key                    # string - OpenAI API key
SEATS_AERO_API_KEY=your_seats_aero_key           # string - Seats.aero API key
EXCHANGE_RATE_API_KEY=your_exchange_rate_api_key # string - Exchange rate API key
UNSPLASH_ACCESS_KEY=your_unsplash_key            # string - Unsplash API key

# Google Services Configuration
GOOGLE_SERVICE_ACCOUNT={"type":"service_account","project_id":"your_project",...} # string - JSON service account credentials
GOOGLE_EMAIL=your_email@gmail.com                # string - Gmail address for sending emails
GOOGLE_PASS=your_app_password                     # string - Gmail app password
MILEAGE_SPREADSHEET_ID=your_spreadsheet_id       # string - Google Sheets ID for mileage data
MILEAGE_WORKSHEET_NAME=mileage                    # string - Sheet name within the mileage spreadsheet
RESULT_SHEET_ID=your_result_sheet_id             # string - Google Sheets ID for storing results
```

**Important Notes:**
- **GOOGLE_SERVICE_ACCOUNT**: This should be the complete JSON service account credentials as a single line string
- **GOOGLE_PASS**: Use an App Password for Gmail, not your regular account password
- **API Keys**: All API keys are required for full functionality
- Travel parameters (origin, destination, dates, etc.) are now configured via API calls rather than environment variables

### 2. Google Services Setup

#### Google Sheets API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the following APIs:
   - Google Sheets API
   - Gmail API (for email notifications)
4. Create service account credentials:
   - Go to "Credentials" → "Create Credentials" → "Service Account"
   - Download the JSON key file
   - Copy the entire JSON content and paste it as the value for `GOOGLE_SERVICE_ACCOUNT` in your `.env` file
5. Share your Google Sheets with the service account email address (found in the JSON credentials)

#### Gmail App Password Setup

1. Enable 2-factor authentication on your Google account
2. Go to Google Account Settings → Security → 2-Step Verification → App passwords
3. Generate an app password for "Mail"
4. Use this app password as the value for `GOOGLE_PASS` in your `.env` file

#### Spreadsheet Configuration

- `MILEAGE_SPREADSHEET_ID`: Create a Google Sheet for mileage data and copy the ID from the URL
- `RESULT_SHEET_ID`: Create another Google Sheet for storing flight search results and copy its ID
- `MILEAGE_WORKSHEET_NAME`: The name of the worksheet within the mileage spreadsheet (default: "mileage")

---

## Verification

To verify the installation was successful:

```bash
# This will download data and run the application
make run
```

The application should start and begin processing flight alerts based on your configuration.

---

## Deployment

### Production Deployment

```bash
# Prepare for deployment (install dependencies, download data)
make deploy-setup

# Deploy the application
make deploy
```

### Docker Deployment

```bash
# Build Docker image
make docker-image

# Run Docker container
make run-docker

# Stop Docker container
make stop-docker
```

---

## Testing

```bash
# Run basic tests
make test

# Run all tests with summary
make test-all

# Run tests with verbose output
make test-verbose

# Run tests with coverage analysis
make test-coverage
```

---

## Cleaning Up

```bash
# Remove all generated files, cache, and logs
make clean
```

# Remove log files
rm -rf logs/

# Remove downloaded data (will need to re-download)
rm -f data/airports.csv
```

---

## Next Steps

After installation, refer to the [Usage Guide](./usage.md) for detailed instructions on configuring and running the flight alerts system.

---

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure your virtual environment is activated: `source venv/bin/activate`
- Verify the installation was successful: `make run`
- Or use: `make install` to set up everything automatically

**API Key Issues**
- Check that all required API keys are properly configured in `.env`
- Verify the `sheets_api_key.json` file is in the correct location
- Ensure API keys have proper permissions and quotas

**Data File Issues**
- If `data/airports.csv` is missing, run: `make download-data`
- Or manually download: `curl -o data/airports.csv https://davidmegginson.github.io/ourairports-data/airports.csv`
- Check internet connection if download fails

**Permission Errors**
- Ensure you have proper read/write permissions in the project directory
- Check that the virtual environment has the necessary permissions
- On Linux/Mac, you may need to make scripts executable

**Make Command Not Found**
- Install make: `sudo apt-get install make` (Ubuntu/Debian) or `brew install make` (macOS)
- Or use the manual installation method instead

**Environment Variables Not Loading**  
- Ensure `.env` file is in the project root directory
- Check `.env` file format (no spaces around `=`)
- Verify all required variables are set (see configuration section)

---

## Support

For additional support or issues not covered in this guide, please refer to the project's GitHub issues page or contact the development team.
