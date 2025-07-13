import asyncio
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import logger, EMAIL_PASSWORD, EMAIL_USERNAME, EMAIL_PORT, EMAIL_HOSTNAME

async def send_email_register(to_email: str, code: str) -> bool:
    smtp_config = {
        'hostname': EMAIL_HOSTNAME,
        'port': EMAIL_PORT,
        'username': EMAIL_USERNAME,
        'password': EMAIL_PASSWORD,
        'use_tls': True
    }

    try:
        with open('data/mail.html', 'r', encoding='utf-8') as file:
            html_template = file.read()
    except FileNotFoundError:
        logger.error("Ошибка: Шаблон письма не найден")
        return False

    html_content = html_template.replace(
        '{{confirmation_url}}',
        f"https://online-postupishka.ru/verify-email?token={code}"
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = smtp_config['username']
    msg['To'] = to_email
    msg['Subject'] = 'Подтверждение регистрации | online-postupishka.ru'
    msg.attach(MIMEText(html_content, 'html'))

    for attempt in range(3):
        try:
            async with aiosmtplib.SMTP(
                hostname=smtp_config['hostname'],
                port=smtp_config['port'],
                use_tls=smtp_config['use_tls'],
                validate_certs=False
            ) as server:
                await server.login(smtp_config['username'], smtp_config['password'])
                await server.sendmail(
                    smtp_config['username'],
                    to_email,
                    msg.as_string()
                )
            return True
        except aiosmtplib.SMTPException as e:
            logger.warning(f"Попытка {attempt+1}: Ошибка отправки - {str(e)}")
            if attempt < 2:
                await asyncio.sleep(2**attempt)  # Экспоненциальная задержка 
        except Exception as e:
            logger.error(f"Критическая ошибка: {str(e)}")
            break

    return False