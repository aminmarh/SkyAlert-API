import os
import pytest
import smtplib

from unittest.mock import patch, MagicMock
from app.helpers.email_helper import Email


def test_send_email_success():
    with patch("app.helpers.email_helper.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        sender = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")

        Email.send_email("test@example.com", "Test Subject", "Test Body")

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(sender, password)
        mock_server.sendmail.assert_called_once()


def test_send_email_error_authentication():
    with patch("app.helpers.email_helper.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(
            535, "Authentication failed"
        )
        mock_smtp.return_value.__enter__.return_value = mock_server

        with pytest.raises(Exception) as excinfo:
            Email.send_email("test@example.com", "Test Subject", "Test Body")

        assert "SMTP Authentication Error: Check your email or password." in str(
            excinfo.value
        )


def test_send_email_error_smtp_exception():
    with patch("app.helpers.email_helper.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = smtplib.SMTPException("General SMTP error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        with pytest.raises(Exception) as excinfo:
            Email.send_email("test@example.com", "Test Subject", "Test Body")

        assert "SMTP Error: General SMTP error" in str(excinfo.value)


def test_send_email_error_general_exception():
    with patch("app.helpers.email_helper.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = Exception("Unexpected error")
        mock_smtp.return_value.__enter__.return_value = mock_server

        with pytest.raises(Exception) as excinfo:
            Email.send_email("test@example.com", "Test Subject", "Test Body")

        assert "Error sending email: Unexpected error" in str(excinfo.value)
