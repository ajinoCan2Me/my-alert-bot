import os
import requests
import imaplib
import email

# Discord Webhook URL（Secrets から環境変数で取得）
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# Gmail の設定（Secrets で管理すること推奨）
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
IMAP_SERVER = "imap.gmail.com"

# Gmail に接続して Google アラートの最新メールを取得
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

    # 本文抽出（プレーンテキスト優先）
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            return part.get_payload(decode=True).decode()
    return "本文が取得できませんでした"

# Discord に送信
def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("送信成功")
    else:
        print("送信失敗", response.status_code, response.text)

if __name__ == "__main__":
    alert_message = get_latest_alert()
    send_to_discord(alert_message)
