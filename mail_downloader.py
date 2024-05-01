import os
import imaplib
import email
import subprocess
import argparse
from datetime import datetime
import logging
import pdfkit
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IMAP configuration
IMAP_SERVER = "your_imap_server"
USERNAME = "your_email@example.com"
# PASSWORD = 'your_email_password'
MAILBOX = "All Mail"

# PDF output directory
OUTPUT_DIR = "SOURCE_DOCUMENTS"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)


def remove_images_from_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for img_tag in soup.find_all("img"):
        img_tag.extract()
    return str(soup)


def extract_text_html(msg):
    content_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                content_parts.append(part.get_payload(decode=True))
    else:
        content_type = msg.get_content_type()
        if content_type == "text/html":
            content_parts.append(msg.get_payload(decode=True))

    return b"\n".join(content_parts)


def get_available_filename(base_filename, folder):
    name, ext = os.path.splitext(base_filename)
    index = 1
    new_filename = base_filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{name} ({index}){ext}"
        index += 1
    return new_filename


def download_emails_as_pdf(mail, args):
    email_ids = get_emails(mail)
    if not email_ids:
        logger.info("No emails found.")
        return

    for email_id in email_ids:
        result, data = mail.uid("fetch", email_id, "(RFC822)")
        if result == "OK":
            raw_email = data[0][1]

            # Parse the email using the email library
            msg = email.message_from_bytes(raw_email)

            # Get the date of the email
            if args.password is None:
                date_obj = email.utils.parsedate_to_datetime(msg["Date"])
                date_str = date_obj.strftime("%Y-%m-%d")
            else:
                date_str = ""

            # Get the subject of the email to use as the PDF filename
            subject = msg.get("Subject", "No Subject")
            pdf_filename = f"{date_str}_{subject}.pdf"
            pdf_filename = get_available_filename(pdf_filename, OUTPUT_DIR)

            # Extract text/html parts from the email content
            email_html = extract_text_html(msg)
            email_html = remove_images_from_html(email_html)

            # Save the email content as a PDF file
            try:
                pdfkit.from_string(email_html, os.path.join(OUTPUT_DIR, pdf_filename))
                logger.info(f"Saved email '{subject}' as PDF: {pdf_filename}")
            except Exception as e:
                logger.error(f"Failed to save email '{subject}' as PDF: {e}")

    # Run script2.py from script1.py
    try:
        result = subprocess.run(["python3", "ingest.py"], capture_output=True, text=True)
        logger.info(result.stdout)
    except Exception as e:
        logger.error(f"Failed to run script2.py: {e}")


def get_emails(mail):
    # Connect to the IMAP server
    mail.select(MAILBOX)

    # Search for all emails
    result, data = mail.uid("search", None, "ALL")
    if result != "OK":
        logger.error("Error searching emails.")
        return []

    email_ids = data[0].split()
    return email_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download emails and save as PDF.")
    parser.add_argument("--server", default=IMAP_SERVER, help="IMAP server address")
    parser.add_argument("--username", default=USERNAME, help="Email username")
    parser.add_argument("--mailbox", default=MAILBOX, help="Mailbox to fetch emails from")
    parser.add_argument("--password", default=None, help="Email password")

    args = parser.parse_args()

    IMAP_SERVER = args.server
    USERNAME = args.username
    MAILBOX = args.mailbox

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    if args.password is None:
        args.password = input("Password: ")

    try:
        mail.login(USERNAME, args.password)
        download_emails_as_pdf(mail, args)
    except Exception as e:
        logger.error(f"Failed to download emails: {e}")
    finally:
        mail.logout()


# TODO: Mail analysis client
# TODO: All the sender's and receivers email-address
# TODO: All the sender's and receivers email-address with suject in dictionary
# TODO: Download every attachment available till date and sort them in folders like pdfs and images and etc, depending on the filename.
# TODO: Extract attachments also and save in their respective folders


# TODO: To create a analytical tool to analyse all your past behaviour and dataset
