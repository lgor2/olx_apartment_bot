import os
import ssl
import html as html_lib
import smtplib
import requests
import logging
from dotenv import load_dotenv
from utils import normalize_text
import logging_config

load_dotenv()
import time

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

CHAT_IDS_FILE = "/app/chat_ids.txt"


class Messenger():
    """Class used to group the notification sending methods."""

    @staticmethod
    def get_chat_ids() -> list:
        """Loads chat IDs from the chat_ids.txt file."""
        chat_ids = []
        if os.path.exists(CHAT_IDS_FILE):
            try:
                with open(CHAT_IDS_FILE, "r") as f:
                    for line in f:
                        chat_id = line.strip()
                        if chat_id:
                            chat_ids.append(chat_id)
            except Exception as e:
                logging.error(f"Error reading {CHAT_IDS_FILE}: {e}")
        
        # Fallback to .env if file is empty or missing
        if not chat_ids:
            env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if env_chat_id:
                chat_ids.append(env_chat_id)
        
        return list(set(chat_ids)) # Unique IDs

    @staticmethod
    def generate_ad_string(ad: dict) -> str:
        """
        Generates the text body of an advertisement.

        Args:
            ad (dict): A dictionary containing details about
            the ad - title, description, price and URL.

        Returns:
            str: The contents of an ad as a string.
        """
        title = html_lib.escape(normalize_text(ad["title"]).strip())
        description = html_lib.escape(normalize_text(ad["description"]).strip()[:200])
        price = html_lib.escape(normalize_text(ad["price"]).strip())
        url = ad["url"]
        return (
            f"🏷 <b>{title}</b>\n"
            f"💰 <b>{price}</b>\n"
            f"📝 {description}...\n"
            f'🔗 <a href="{url}">Відкрити оголошення →</a>'
        )

    @staticmethod
    def generate_ad_content(new_ads: list) -> tuple[str, str]:
        """
        Generates the subject and the body of a notification containing new ads.

        Params:
            new_ads (List[Dict]): A list of dictionaries containing details about
            the new ads - title, description, price and URL.

        Returns:
            Tuple[str, str]: A tuple containing the subject and the body.
        """
        email_body_elements = []
        for new_ad_details in new_ads:
            ad_string = Messenger.generate_ad_string(new_ad_details)
            email_body_elements.append(ad_string)

        email_subject = "🔔 Нове оголошення на OLX"
        email_body = "\n\n".join(email_body_elements)
        return email_subject, email_body

    @staticmethod
    def send_email_message(subject: str, message: str) -> None:
        """
        Send the recipient an email with the given subject and message.

        Params:
            Subject (str): Subject of the email.
            message (str): Body of the message.

        Returns:
            None

        Raises:
            SMTPAuthenticationError: If the authentication data is incorrect.
            SMTPException: If an error occurs while sending the email.
        """
        try:
            subject = str(subject)
            message = str(message)
            message = f"""Subject: {subject}\n\n{message}"""
            message = normalize_text(message)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
                server.quit()
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPException) as error:
            logging.error(f"Error sending email notification: {error}")
        logging.info("Email notification sent successfully")

    @staticmethod
    def send_telegram_message(message_subject: str, message_body: str, chat_ids: list = None) -> None:
        """
        Send a message via Telegram.

        Args:
            message_subject: Header line of the message.
            message_body: Body of the message (HTML allowed).
            chat_ids: List of chat IDs to send to. Defaults to all configured IDs.
        """
        endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        max_length = 4000
        message_batches = []
        current_message = ""
        chunks = message_body.split("\n\n")
        for chunk in chunks:
            if len(current_message) + len(chunk) <= max_length:
                current_message += chunk + "\n\n"
            else:
                message_batches.append(current_message.strip())
                current_message = chunk + "\n\n"
        message_batches.append(current_message.strip())

        recipients = chat_ids if chat_ids is not None else Messenger.get_chat_ids()
        if not recipients:
            logging.error("No Telegram chat IDs found for broadcasting.")
            return

        for chat_id in recipients:
            for i, message_batch in enumerate(message_batches):
                message_text = f"{message_subject}\n\n{message_batch}" if i == 0 else message_batch
                params = {
                    "chat_id": chat_id,
                    "text": message_text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                }
                try:
                    response = requests.get(endpoint, params=params)
                    response.raise_for_status()
                    if response.json()["ok"]:
                        logging.info(f"Telegram notification sent to {chat_id}")
                    else:
                        logging.error(f"Error sending Telegram notification to {chat_id}")
                except requests.exceptions.RequestException as error:
                    logging.error(f"Telegram connection error for {chat_id}: {error}")

            time.sleep(0.1)

    @staticmethod
    def _get_telegram_bot_chats() -> list:
        """
        Helper function to get the details of all the chats in which
        a bot is participating.

        Returns:
            chats (list[dict]): A unique list of dictionaries, each continaing the details of
            a chat. For a private chat, the details are: 'id', 'type', 'first_name', 'last_name',
            'username'. For a group chat, the details are: 'id', 'type', 'title',
            'all_members_are_administrators'. In case of an error, it returns an emtpy list.
        """
        endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            results = data.get("result", [])
            chats = []
            for result in results:
                chat = result.get("message", {}).get("chat")
                if chat not in chats:
                    chats.append(chat)
            return chats
        except requests.exceptions.RequestException as error:
            logging.error(f"Error getting Telegram bot chat data: {error}")
            return []
