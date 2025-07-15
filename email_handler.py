
# -*- coding: utf-8 -*-
"""
Email Handler for the Gmail Screener application.

This module contains the core logic for handling email operations with the
Gmail API. It includes functions for:
- Authenticating with the Gmail API using OAuth 2.0.
- Searching for emails based on a given query.
- Fetching the content of specific emails.
- Generating a PDF file from the content of the fetched emails.
- Creating and sending an email with the PDF as an attachment.
- Marking emails as read.

This modular approach keeps the main script clean and focused on the
application's workflow.
"""

import base64
import os
import re
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httplib2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

# Import configuration from the config.py file
from config import (
    SCOPES,
    CREDENTIALS_FILE,
    FORWARD_TO_EMAIL,
    MARK_AS_READ,
    PDF_FILENAME,
)


def get_gmail_service():
    """
    Authenticates with the Gmail API and returns a service object.

    Handles the OAuth 2.0 flow and saves credentials for future use.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_console()
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def search_emails(service, query):
    """
    Searches for emails matching the given query.
    """
    try:
        response = service.users().messages().list(userId="me", q=query).execute()
        messages = response.get("messages", [])
        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId="me", q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response.get("messages", []))
        print(f"Found {len(messages)} emails matching the query.")
        return messages
    except HttpError as error:
        print(f"An error occurred while searching for emails: {error}")
        return []


import html

def strip_html_tags(text):
    """
    Removes HTML tags and their attributes from a string, unescapes HTML entities,
    and cleans up whitespace.
    """
    # Unescape HTML entities first
    text = html.unescape(text)

    # Remove all content within angle brackets, including attributes
    # This is a more aggressive approach to ensure no HTML syntax remains
    text = re.sub(r'<[^>]*>', '', text)

    # Replace multiple spaces/newlines with a single space
    text = re.sub(r'\s+', ' ', text).strip()

    # Escape any remaining literal < or > characters that might be part of text
    # but could be misinterpreted by ReportLab if not already removed by regex
    text = text.replace('<', '&lt;').replace('>', '&gt;')

    return text

def get_email_content(service, message_id):
    """
    Fetches the full content of a specific email.
    """
    try:
        email_data = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        payload = email_data['payload']
        parts = payload.get('parts', [])

        full_body = ""
        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    full_body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    # Prioritize HTML content if available and strip tags
                    full_body += strip_html_tags(base64.urlsafe_b64decode(part['body']['data']).decode('utf-8'))
        elif 'body' in payload and 'data' in payload['body']:
            full_body = strip_html_tags(base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8'))

        email_data['full_body'] = full_body
        return email_data
    except HttpError as error:
        print(f"An error occurred while fetching email content: {error}")
        return None


def create_pdf_from_emails(emails, date_range):
    """
    Generates a PDF file from the content of a list of emails.

    Args:
        emails: A list of email message objects.
        date_range: A dictionary containing 'after' and 'before' dates.

    Returns:
        The filename of the generated PDF.
    """
    pdf_base_name = os.path.splitext(PDF_FILENAME)[0]
    if date_range and "after" in date_range and "before" in date_range:
        pdf_file_name = f"{pdf_base_name}_{date_range['after'].replace('/','')}_{date_range['before'].replace('/','')}.pdf"
    else:
        pdf_file_name = PDF_FILENAME

    doc = SimpleDocTemplate(pdf_file_name, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Add a new style for bold text
    styles.add(ParagraphStyle(name='Bold', fontName='Helvetica-Bold'))
    
    # Add a style for page numbers
    styles.add(ParagraphStyle(name='PageNumber', alignment=TA_RIGHT))

    story = []
    
    # Function to add page numbers
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = "Page %s" % page_num
        canvas.drawRightString(200, 20, text)

    print(f"Generating PDF file: {pdf_file_name}...")
    for email in emails:
        headers = email["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "N/A")
        from_email = next((h["value"] for h in headers if h["name"] == "From"), "N/A")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "N/A")
        full_body = email.get('full_body', '')

        story.append(Paragraph(f"<b>Subject: {subject}</b>", styles["h2"]))
        story.append(Paragraph(f"<b>Date: {date}</b>", styles["h3"]))
        story.append(Paragraph(f"From: {from_email}", styles["h3"]))
        story.append(Spacer(1, 12))
        
        # Extract dollar amounts from the email body
        dollar_amounts = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', full_body)
        if dollar_amounts:
            story.append(Paragraph("<b>Dollar Amounts Found:</b>", styles['Bold']))
            for amount in dollar_amounts:
                story.append(Paragraph(amount, styles["BodyText"]))
            story.append(Spacer(1, 12))

        # Extract expense/purchase related information
        expense_keywords = ["total", "amount due", "paid", "charged", "invoice", "receipt", "order", "purchase"]
        expense_info = []
        for line in full_body.splitlines():
            if any(keyword in line.lower() for keyword in expense_keywords):
                expense_info.append(line.strip())
        
        if expense_info:
            story.append(Paragraph("<b>Expense/Purchase Details:</b>", styles['Bold']))
            for info in expense_info:
                story.append(Paragraph(info, styles["BodyText"]))
            story.append(Spacer(1, 12))

        story.append(Paragraph(strip_html_tags(email["snippet"]), styles["BodyText"]))
        story.append(Spacer(1, 24))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("PDF generation complete.")
    return pdf_file_name

def send_email_with_attachment(service, pdf_filename):
    """
    Sends an email with the generated PDF as an attachment.

    Args:
        service: The authenticated Gmail API service object.
        pdf_filename: The filename of the PDF to attach.
    """
    try:
        message = MIMEMultipart()
        message["to"] = FORWARD_TO_EMAIL
        message["subject"] = "Forwarded Emails in PDF"

        # Email body
        body = MIMEText("Please find the attached PDF containing the forwarded emails.")
        message.attach(body)

        # PDF attachment
        with open(pdf_filename, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_filename))
        part[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(pdf_filename)}"'
        message.attach(part)

        # Encode and send the email
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": raw_message}
        sent_message = service.users().messages().send(userId="me", body=body).execute()
        print(f"Successfully sent email with PDF to {FORWARD_TO_EMAIL}")
        return sent_message

    except HttpError as error:
        print(f"An error occurred while sending the email: {error}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def mark_emails_as_read(service, message_ids):
    """
    Marks a list of emails as read.
    """
    if not MARK_AS_READ:
        return

    try:
        service.users().messages().batchModify(
            userId="me", body={"ids": message_ids, "removeLabelIds": ["UNREAD"]}
        ).execute()
        print(f"Marked {len(message_ids)} emails as read.")
    except HttpError as error:
        print(f"An error occurred while marking emails as read: {error}")
