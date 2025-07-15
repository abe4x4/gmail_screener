
# -*- coding: utf-8 -*-
"""
Configuration file for the Gmail Screener application.

This file contains all the settings and credentials required for the application
to run. Storing configuration in a separate file like this makes it easy to
change settings without modifying the main application logic. It also improves
security by keeping sensitive information separate from the source code.
"""

# Gmail API settings
# ------------------
# These settings are necessary for authenticating with the Gmail API.
# You will need to create a project in the Google Cloud Console, enable the
# Gmail API, and create OAuth 2.0 credentials.

# The name of the file containing your Google API credentials.
# This file is typically downloaded from the Google Cloud Console and should be
# kept secure.
CREDENTIALS_FILE = "credentials.json"

# The scopes define the level of access the application has to your Gmail
# account. For this application, we need to read, send, and modify emails.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",  # To read emails
    "https://www.googleapis.com/auth/gmail.send",      # To send emails with attachments
    "https://www.googleapis.com/auth/gmail.modify",    # To mark emails as read/unread
]

# Email forwarding settings
# -------------------------
# These settings define the criteria for which emails to select and where to
# send the generated PDF.

# The email address to which the PDF will be sent.
# Make sure this is a valid email address that you have access to.
FORWARD_TO_EMAIL = "iabouzeid@gmail.com"

# The name of the file containing your search criteria.
CRITERIA_FILE = "criteria.json"

# PDF generation settings
# -----------------------
# The name of the generated PDF file.
PDF_FILENAME = "forwarded_emails.pdf"

# Application behavior settings
# -----------------------------
# These settings control how the application behaves after processing emails.

# Whether to mark the processed emails as read.
# This can help prevent the same emails from being included in the PDF again.
MARK_AS_READ = True # Set to True to mark emails as read after processing.
