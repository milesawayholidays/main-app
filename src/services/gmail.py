"""
Gmail service for sending flight alert emails with PDF attachments.

This module provides functionality to send emails through Gmail's SMTP service,
specifically designed for delivering flight alert reports and notifications.
It handles authentication, PDF attachment processing, and error management
for reliable email delivery.

The module integrates with:
- Gmail SMTP service for email delivery
- Configuration management for credentials
- Global state for logging
- PDF objects for attachment handling

Key Features:
- Secure SMTP SSL connection to Gmail
- PDF attachment support for flight reports
- Self-sending capability for admin notifications
- Comprehensive error handling and logging
"""

import smtplib
from email.message import EmailMessage

from config import config
from global_state import state

from data_types.pdf_types import PDF_OBJ


def email_self(subject: str, body: str, attachments: list[PDF_OBJ] = None) -> None:
    """
    Send an email to the configured Gmail address with optional PDF attachments.
    
    This function sends an email from the configured Gmail account to itself,
    primarily used for sending flight alert reports to administrators. It
    supports multiple PDF attachments and provides comprehensive error handling.
    
    Args:
        subject (str): Email subject line
        body (str): Plain text email body content
        attachments (list[PDF_OBJ], optional): List of PDF objects to attach.
            Each PDF_OBJ should contain 'bin' (binary data) and 'title' (filename).
            Defaults to None if no attachments needed.
            
    Returns:
        None
        
    Raises:
        Exception: Re-raises any SMTP or authentication errors that occur
            during the email sending process
            
    Note:
        - Uses Gmail's SMTP SSL service on port 465
        - Requires GOOGLE_EMAIL and GOOGLE_PASS to be configured
        - All PDF attachments are set with MIME type 'application/pdf'
        - Logs successful sends and errors to the global state logger
        - Sends email from and to the same configured address
        
    Example:
        >>> pdf_obj = PDF_OBJ(title="flight_report.pdf", bin=pdf_binary_data)
        >>> email_self(
        ...     subject="Daily Flight Alerts",
        ...     body="Please find today's flight deals attached.",
        ...     attachments=[pdf_obj]
        ... )
    """
    msg = EmailMessage()
    mail = config.GOOGLE_EMAIL
    password = config.GOOGLE_PASS
    msg['From'] = mail
    msg['To'] = mail
    msg['Subject'] = subject
    msg.set_content(body)
    if attachments:
        for attachment in attachments:
            # Read the PDF file from the file path
            with open(attachment.filePath, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=attachment.title)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail, password)
            smtp.send_message(msg)
            state.logger.info(f"Email sent successfully to {mail}")
            print("Email sent successfully.")

    except Exception as e:
        state.logger.error(f"Failed to send email: {e}")
        raise e
  
  
def email(subject: str, body: str, to: str):
    '''
    This function sends an email from the configured Gmail account to a specified recipient.
    It supports plain text content and provides error handling for the email sending process.

    Args:
        subject (str): Email subject line
        body (str): Plain text email body content
        to (str): Recipient email address

    Returns:
        None

    Raises:
        Exception: Re-raises any SMTP or authentication errors that occur
        during the email sending process

    Note:
        - Uses Gmail's SMTP SSL service on port 465
        - Requires GOOGLE_EMAIL and GOOGLE_PASS to be configured
        - Logs successful sends and errors to the global state logger

    Example:
        >>> email(
        ...     subject="Test Email",
        ...     body="This is a test email.",
        ...     to="recipient@example.com"
        ... )
    '''
    msg = EmailMessage()
    mail = config.GOOGLE_EMAIL
    password = config.GOOGLE_PASS
    msg['From'] = mail
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(mail, password)
            smtp.send_message(msg)
            state.logger.info(f"Email sent successfully to {to}")
            print("Email sent successfully.")

    except Exception as e:
        state.logger.error(f"Failed to send email: {e}")
        raise e