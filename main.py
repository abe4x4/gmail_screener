
# -*- coding: utf-8 -*-
"""
Main script for the Gmail Screener application.

This script serves as the entry point for the application. It orchestrates the
entire process of:
1. Authenticating with the Gmail API.
2. Searching for emails based on the criteria defined in `config.py`.
3. Fetching the content of each email.
4. Compiling the emails into a single PDF file.
5. Sending the PDF as an attachment to the specified recipient.
6. Marking the processed emails as read (if configured to do so).

To run the application, simply execute this script from your terminal:
    python main.py

Make sure you have all the required packages installed and your `config.py`
file is properly configured.
"""

import os
import json

# Import functions from the email_handler module
from email_handler import (
    get_gmail_service,
    search_emails,
    get_email_content,
    create_pdf_from_emails,
    send_email_with_attachment,
    mark_emails_as_read,
)

# Import configuration from the config.py file
from config import CRITERIA_FILE, PDF_FILENAME

def build_search_query(criteria):
    """
    Builds a Gmail search query from the given criteria.
    """
    query_parts = []
    if "date_range" in criteria:
        if "after" in criteria["date_range"]:
            query_parts.append(f"after:{criteria['date_range']['after']}")
        if "before" in criteria["date_range"]:
            query_parts.append(f"before:{criteria['date_range']['before']}")
    
    if "include" in criteria and "terms" in criteria["include"] and criteria["include"]["terms"]:
        operator = f" {criteria['include'].get('logical_operator', 'AND')} "
        query_parts.append(f"({operator.join(criteria['include']['terms'])})")
        
    if "exclude" in criteria and "terms" in criteria["exclude"] and criteria["exclude"]["terms"]:
        operator = f" {criteria['exclude'].get('logical_operator', 'OR')} "
        query_parts.append(f"-({operator.join(criteria['exclude']['terms'])})")
        
    return " ".join(query_parts)

def main():
    """
    The main function of the application.

    This function orchestrates the entire email processing and forwarding workflow.
    """
    print("Starting the Gmail Screener application...")

    # 1. Authenticate with the Gmail API
    print("Authenticating with Gmail...")
    service = get_gmail_service()
    if not service:
        print("Failed to authenticate with Gmail. Exiting.")
        return
    print("Authentication successful.")

    # 2. Load search criteria and build the query
    try:
        with open(CRITERIA_FILE, 'r') as f:
            criteria = json.load(f)
    except FileNotFoundError:
        print(f"Error: Criteria file not found at '{CRITERIA_FILE}'. Exiting.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{CRITERIA_FILE}'. Exiting.")
        return
        
    search_query = build_search_query(criteria)
    print(f"Searching for emails with query: '{search_query}'...")
    messages = search_emails(service, search_query)

    if not messages:
        print("No emails found matching the criteria. Exiting.")
        return

    # 3. Fetch the content of each email
    emails = []
    message_ids = []
    for message_summary in messages:
        message_id = message_summary["id"]
        print(f"Fetching content for email ID: {message_id}")
        email_content = get_email_content(service, message_id)
        if email_content:
            emails.append(email_content)
            message_ids.append(message_id)

    if not emails:
        print("Could not fetch content for any of the selected emails. Exiting.")
        return

    # 4. Create a PDF from the emails
    date_range = criteria.get("date_range", {})
    pdf_filename = create_pdf_from_emails(emails, date_range)

    # 5. Send the PDF as an attachment
    sent_message = send_email_with_attachment(service, pdf_filename)

    # 6. Mark the emails as read if the email was sent successfully
    if sent_message:
        mark_emails_as_read(service, message_ids)

    # 7. Clean up the generated PDF file
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)
        print(f"Cleaned up and removed the PDF file: {pdf_filename}")

    print("\nApplication has finished processing.")


if __name__ == "__main__":
    main()
