
# Gmail Screener

This Python application connects to a Gmail account, selects emails based on user-defined criteria, combines them into a single PDF file with enhanced formatting, and forwards that PDF to a specified email address. It is designed to be easy to configure and understand, even for beginner programmers.

## Features

*   **Connects to Gmail**: Securely authenticates with your Gmail account using the Gmail API.
*   **Advanced, Customizable Filtering**: Use a dedicated `criteria.json` file to define complex search queries, including date ranges and multiple search terms with logical AND/OR operators.
*   **Enhanced PDF Compilation**: Automatically generates a single PDF file containing the content of the selected emails, with the following features:
    *   **Page Numbers**: Each page is numbered for easy reference.
    *   **Formatted Headers**: The email subject and date are displayed in bold for better readability.
    *   **Dollar Amount Extraction**: Automatically finds and lists any dollar amounts mentioned in the email body.
*   **Automated Forwarding**: Forwards the generated PDF to any email address you choose.
*   **Well-Commented Code**: The source code is extensively commented to explain how each part of the application works.
*   **Easy Configuration**: All settings are stored in `config.py` and `criteria.json` for easy modification.

## How It Works

The application follows these steps:

1.  **Authentication**: It connects to the Gmail API using your credentials. The first time you run the application, you will be prompted to authorize it in your web browser. This creates a `token.json` file that stores your authentication details for future runs.
2.  **Criteria Loading**: It reads the `criteria.json` file to get your desired search parameters.
3.  **Email Search**: It constructs a search query from your criteria and uses it to find matching emails in your Gmail account.
4.  **PDF Generation**: It fetches the content of the selected emails and compiles them into a single PDF file with the enhanced features mentioned above.
5.  **Forwarding**: It sends an email with the generated PDF as an attachment to the recipient you specified.
6.  **Mark as Read**: After the emails are processed, they are marked as read to prevent them from being processed again.
7.  **Cleanup**: The generated PDF file is automatically deleted after it has been sent.

## Getting Started

Follow these instructions to set up and run the application on your local machine.

### Prerequisites

*   Python 3.6 or higher
*   A Google account with Gmail enabled

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone <repository-url>
cd gmail-screener
```

### 2. Set Up the Virtual Environment

It is recommended to use a virtual environment to manage the project's dependencies. Create and activate a virtual environment by running:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

Install the required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Configure the Application

Before you can run the application, you need to configure it by editing the `config.py` and `criteria.json` files.

#### a. Enable the Gmail API and Get Credentials

1.  **Go to the Google Cloud Console**: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2.  **Create a new project** (or select an existing one).
3.  **Enable the Gmail API**: In the navigation menu, go to **APIs & Services > Library**, search for "Gmail API", and enable it.
4.  **Create OAuth 2.0 Credentials**:
    *   Go to **APIs & Services > Credentials**.
    *   Click **Create Credentials > OAuth client ID**.
    *   Select **Desktop application** as the application type.
    *   Click **Create**.
    *   A window will appear with your client ID and client secret. Click **Download JSON** to download your credentials file.
5.  **Rename and Move the Credentials File**:
    *   Rename the downloaded file to `credentials.json`.
    *   Move this file into the root directory of the project (the same directory as `main.py`).

    **Important**: Keep this `credentials.json` file secure and do not share it with anyone.

#### b. Edit `config.py`

Open the `config.py` file and customize the following settings:

*   `FORWARD_TO_EMAIL`: The email address where you want to forward the PDF.
*   `PDF_FILENAME`: The name of the PDF file that will be generated.
*   `MARK_AS_READ`: Set to `True` to mark emails as read after processing.

#### c. Edit `criteria.json`

Open the `criteria.json` file to define your email search criteria. Here is an example:

```json
{
  "date_range": {
    "after": "2024/01/01",
    "before": "2025/12/31"
  },
  "include": {
    "logical_operator": "AND",
    "terms": [
      "subject:invoice",
      "has:attachment"
    ]
  },
  "exclude": {
    "logical_operator": "OR",
    "terms": [
      "subject:spam",
      "from:junk@example.com"
    ]
  }
}
```

*   `date_range`: (Optional) Specify a time period for the email search.
    *   `after`: (Optional) The start date (YYYY/MM/DD).
    *   `before`: (Optional) The end date (YYYY/MM/DD).
*   `include`: (Optional) Defines the criteria for emails to include.
    *   `logical_operator`: (Optional) The logical operator to use when combining multiple `include` terms. Can be `AND` or `OR`. Defaults to `AND`.
    *   `terms`: A list of search terms to include. These follow the standard Gmail search query format.
*   `exclude`: (Optional) Defines the criteria for emails to exclude.
    *   `logical_operator`: (Optional) The logical operator to use when combining multiple `exclude` terms. Can be `AND` or `OR`. Defaults to `OR`.
    *   `terms`: A list of search terms to exclude. These follow the standard Gmail search query format.

### 5. Run the Application

Once you have completed the configuration, you can run the application from your terminal:

```bash
python main.py
```

The first time you run it, a browser window will open, asking you to log in to your Google account and grant the application permission to access your Gmail. After you approve, the application will start running.

## Pushing to GitHub

This project is set up to be easily pushed to a new GitHub repository. It includes a `.gitignore` file that excludes sensitive and unnecessary files from being tracked by Git.

### Files Included in `.gitignore`

*   `venv/`
*   `__pycache__/`
*   `token.json`
*   `credentials.json`
*   `*.pdf` (to ignore the generated PDF files)

By ignoring these files, you can safely share your code without exposing your sensitive information.

## How to Contribute

This project is designed for educational purposes, and contributions are welcome! If you have ideas for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
