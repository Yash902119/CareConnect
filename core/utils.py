"""
Utility functions for sending emails via Resend API (HTTP-based, works on Railway)
"""
import threading
import os
import resend


def send_otp_email(email, otp_code, purpose='email_verification'):
    """
    Send OTP code via Resend API (HTTP, not SMTP — works on Railway).

    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: 'email_verification' or 'password_reset'

    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        resend.api_key = os.getenv('RESEND_API_KEY', '')

        if not resend.api_key:
            print("[Email] RESEND_API_KEY not set — cannot send email.")
            return False

        if purpose == 'password_reset':
            subject = 'CareConnect - Password Reset OTP'
            body = f"""
Hello,

You have requested to reset your password for your CareConnect account.

Your OTP code is: {otp_code}

This OTP will expire in 15 minutes.

If you did not request this, please ignore this email.

Best regards,
CareConnect Team
"""
        else:
            subject = 'CareConnect - Email Verification OTP'
            body = f"""
Hello,

Thank you for registering with CareConnect!

Your OTP code for email verification is: {otp_code}

This OTP will expire in 10 minutes.

If you did not create an account with CareConnect, please ignore this email.

Best regards,
CareConnect Team
"""

        params: resend.Emails.SendParams = {
            "from": "CareConnect <onboarding@resend.dev>",
            "to": [email],
            "subject": subject,
            "text": body,
        }

        response = resend.Emails.send(params)
        print(f"[Email] Sent to {email} via Resend. ID: {response.get('id', 'N/A')}")
        return True

    except Exception as e:
        print(f"[Email Error] Failed to send to {email}: {str(e)}")
        return False


def send_email_async(email, otp_code, purpose='email_verification'):
    """
    Send OTP email in a background thread so the HTTP request is not blocked.
    """
    def _send():
        try:
            send_otp_email(email, otp_code, purpose)
        except Exception as e:
            print(f"[Async Email Error] {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()
    return True


def send_email_with_fallback(email, otp_code, purpose='email_verification'):
    """
    Send OTP email via Resend API in background thread.
    Falls back to console logging if API key not configured.

    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: Purpose of OTP

    Returns:
        bool: Always True (fire-and-forget)
    """
    api_key = os.getenv('RESEND_API_KEY', '')

    if not api_key:
        # Fallback: print to console/logs for development
        purpose_text = "Password Reset" if purpose == 'password_reset' else "Email Verification"
        print(f"\n{'='*50}")
        print(f"{purpose_text} OTP for {email}: {otp_code}")
        print(f"{'='*50}\n")
        return True

    # Send via Resend HTTP API in background thread (non-blocking)
    return send_email_async(email, otp_code, purpose)
