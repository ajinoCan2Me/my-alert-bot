import os
import requests
import imaplib
import email
import re

# Gmail 認証情報（Secrets から）
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
IMAP_SERVER = "imap.gmail.com"

print("DEBUG: Gmail user =", GMAIL_USER)
print("DEBUG: Gmail pass is set =", GMAIL_PASS is not None)

# Gmail から最新の Google アラートを取得
def get_latest_alert():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(GMAIL_USER, GMAIL_PASS)
    mail.select("inbox")

    status, data = mail.search(None, '(FROM "googlealerts-noreply@google.com")')
    mail_ids = data[0].split()
    if not mail_ids:
        return "新しいアラートはありません"

    latest_id = mail_ids[-1]
    status, msg_data = mail.fetch(latest_id, "(RFC822)")
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)

    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True).decode()
            # URL (http) の前で改行
            body = re.sub(r"(?<!\n)(http)", r"\n\1", body)
            return body
    return "本文が取得できませんでした"

# Discord に分割して送信
def send_to_discord(message):
    MAX_LENGTH = 2000
    for i in range(0, len(message), MAX_LENGTH):
        chunk = message[i:i+MAX_LENGTH]
        payload = {"content": chunk}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"送信成功 ({i // MAX_LENGTH + 1} / {(len(message)-1)//MAX_LENGTH + 1})")
        else:
            print("送信失敗", response.status_code, response.text)

if __name__ == "__main__":
    alert_message = get_latest_alert()
    send_to_discord(alert_message)
