# [`gmail.py`](../../src/services/gmail.py)

This module provides Gmail service functionality for sending flight alert emails with PDF attachments. It handles secure email delivery through Gmail's SMTP service, specifically designed for administrative notifications and report distribution in the flight alert system.

---

## 📄 Overview

The module implements a simple, function-based approach for email delivery using Gmail's SMTP SSL service. It's designed specifically for self-sending emails (same sender and recipient) with optional PDF attachments, primarily used for delivering flight alert reports to administrators.

The service provides:
- Secure SMTP SSL connection to Gmail (port 465)
- PDF attachment support for flight reports  
- Comprehensive error handling and logging
- Integration with global state management
- Simple configuration-based authentication

---

## 📦 Functions

### `email_self(subject: str, body: str, attachments: list[PDF_OBJ] = None) -> None`

Sends an email to the configured Gmail address with optional PDF attachments.

#### Parameters:
- **`subject`** (`str`): Email subject line
- **`body`** (`str`): Plain text email body content  
- **`attachments`** (`list[PDF_OBJ]`, optional): List of PDF objects to attach. Each PDF_OBJ should contain:
  - `bin`: Binary PDF data
  - `title`: Filename for the attachment
  - Defaults to None if no attachments needed

#### Behavior:
- **SMTP Connection**: Uses `smtplib.SMTP_SSL` with Gmail's server (`smtp.gmail.com:465`)
- **Authentication**: Uses configured Google email and app password
- **Message Composition**: Creates EmailMessage with plain text content
- **Attachment Processing**: Adds PDF attachments with proper MIME type (`application/pdf`)
- **Self-Sending**: Sends from configured email address to the same address
- **Logging**: Records successful sends and errors via global state logger

#### Returns:
- `None`: Function completes silently on success

#### Raises:
- **`Exception`**: Re-raises any SMTP, authentication, or connection errors that occur during the email sending process

---

## 🧠 Error Handling

- **SMTP Errors**: Wraps email sending in try-except block with comprehensive error logging
- **Authentication Failures**: Logs and re-raises authentication errors for debugging
- **Connection Issues**: Handles SSL connection problems with detailed error messages
- **Attachment Processing**: Gracefully handles PDF attachment errors

---

## 💡 Usage Examples

### Basic Email Sending

```python
from services.gmail import email_self

# Send simple notification email
email_self(
    subject="Flight Alerts System - Daily Report",
    body="System running normally. No issues detected."
)
```

### Email with PDF Attachments

```python
from services.gmail import email_self
from data_types.pdf_types import PDF_OBJ

# Create PDF attachments
pdf_reports = [
    PDF_OBJ(title="sao_paulo_paris_deals.pdf", bin=pdf_binary_data_1),
    PDF_OBJ(title="rio_london_deals.pdf", bin=pdf_binary_data_2)
]

# Send email with attachments
email_self(
    subject="Daily Flight Alerts - July 28, 2025",
    body="Please find today's top flight deals attached. Review and approve for distribution.",
    attachments=pdf_reports
)
```

### Integration with Flight Pipeline

```python
# Typical usage in alerts_runner.py
def send_daily_reports(trip_options):
    """Send daily flight reports to administrator"""
    try:
        # Generate PDFs for each trip option
        pdf_attachments = [generate_pdf(option) for option in trip_options]
        
        # Send consolidated email
        email_self(
            subject=f"Flight Alerts - {len(trip_options)} deals for {date.today()}",
            body=f"Generated {len(trip_options)} flight deal reports. Please review attached PDFs.",
            attachments=pdf_attachments
        )
        
        state.logger.info("Daily reports sent successfully")
        
    except Exception as e:
        state.logger.error(f"Failed to send daily reports: {e}")
        raise
```

---

## 🔐 Authentication

**Gmail App Password Setup:**
1. Enable 2-factor authentication on Google account
2. Generate app password: Google Account > Security > App Passwords
3. Use app password (not regular password) in configuration

**Required Configuration:**
- **`config.GOOGLE_EMAIL`**: Gmail address for both sender and recipient
- **`config.GOOGLE_PASS`**: Gmail app password (16-character generated password)

**Security Notes:**
- Uses SSL encryption for all communications
- App passwords are more secure than regular passwords for SMTP
- Self-sending pattern reduces external email security concerns

---

## 🔗 Dependencies

- **`smtplib`**: Built-in Python SMTP client for Gmail communication
- **`email.message.EmailMessage`**: Built-in email message composition
- [`config`](../config.md): Configuration management for email credentials
- [`global_state`](../global_state.md): Centralized logging and state management
- [`PDF_OBJ`](../data_types/pdf_types.md): Data structure for PDF attachments

---

## ⚠️ Notes

- **Self-Sending Only**: Function sends from and to the same email address
- **Plain Text Only**: Email body is plain text (no HTML formatting)
- **PDF Attachments Only**: Designed specifically for PDF file attachments
- **No Authentication Validation**: Errors occur during SMTP connection if credentials are invalid
- **Gmail Specific**: Hardcoded for Gmail SMTP service (smtp.gmail.com:465)
- **Synchronous Operation**: Blocks until email sending completes or fails
