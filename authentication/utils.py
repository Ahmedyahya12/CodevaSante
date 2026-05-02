from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import activation_token_generator


def send_activation_email(user):
    if not user.email:
        raise ValueError("L'utilisateur n'a pas d'email.")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip(
        "/"
    )
    activation_link = f"{frontend_url}/set-password/{uid}/{token}/"

    full_name = user.full_name or user.email
    role_name = (
        user.get_role_display() if hasattr(user, "get_role_display") else "مستخدم"
    )

    subject = "CodevaClinic - تفعيل حسابك"

    text_body = f"""
مرحبًا {full_name}

تم إنشاء حسابك في منصة CodevaClinic.

الدور الخاص بك: {role_name}

لتفعيل حسابك وتعيين كلمة المرور، افتح الرابط التالي:
{activation_link}

CodevaSolution - CodevaClinic
    """.strip()

    html_body = render_to_string(
        "accounts/activation_email.html",
        {
            "full_name": full_name,
            "role_name": role_name,
            "activation_link": activation_link,
        },
    )

    from_email = getattr(
        settings,
        "DEFAULT_FROM_EMAIL",
        "CodevaClinic <codeva.erp@gmail.com>",
    )

    reply_to_address = getattr(settings, "EMAIL_REPLY_TO", "codeva.erp@gmail.com")

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[user.email],
        reply_to=[reply_to_address],
        headers={
            "X-Entity-Ref-ID": f"codevaerp-activation-{user.pk}",
            "Precedence": "transactional",
            "List-Unsubscribe": f"<mailto:{reply_to_address}?subject=unsubscribe>",
        },
    )

    email.attach_alternative(html_body, "text/html")

    sent_count = email.send(fail_silently=False)

    if sent_count != 1:
        raise Exception("Email non envoyé par le serveur SMTP.")

    return sent_count


def send_patient_activation_email(user):
    if not user.email:
        raise ValueError("Le patient n'a pas d'email.")

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = activation_token_generator.make_token(user)

    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173").rstrip(
        "/"
    )
    activation_link = f"{frontend_url}/set-password/{uid}/{token}/"

    full_name = user.full_name or user.email

    # ✅ Sujet court, neutre, sans diacritiques ni mots marketing
    subject = "CodevaClinic - تفعيل حسابك"

    # ✅ Corps purement transactionnel, sans liste de bénéfices
    text_body = f"""
مرحبًا {full_name}

تم إنشاء حسابك في منصة .
CodevaClinic
لتفعيل حسابك وتعيين كلمة المرور، افتح الرابط التالي:
{activation_link}

CodevaSolution - CodevaClinic
    """.strip()

    html_body = render_to_string(
        "accounts/patient_activation_email.html",
        {
            "full_name": full_name,
            "activation_link": activation_link,
        },
    )

    return _send_transactional_email(
        user=user,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        entity_ref_prefix="codevaerp-activation",  # ✅ Même préfixe que le mail staff
    )


def _send_transactional_email(user, subject, text_body, html_body, entity_ref_prefix):
    from_email = getattr(
        settings,
        "DEFAULT_FROM_EMAIL",
        "CodevaClinic <codeva.erp@gmail.com>",
    )

    reply_to_address = getattr(settings, "EMAIL_REPLY_TO", "codeva.erp@gmail.com")

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[user.email],
        reply_to=[reply_to_address],
        headers={
            "X-Entity-Ref-ID": f"{entity_ref_prefix}-{user.pk}",
            "Precedence": "transactional",
            # ✅ Format correct RFC pour List-Unsubscribe
            "List-Unsubscribe": f"<mailto:{reply_to_address}?subject=unsubscribe>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",  # ✅ Ajout one-click (Gmail l'apprécie)
        },
    )

    email.attach_alternative(html_body, "text/html")

    sent_count = email.send(fail_silently=False)

    if sent_count != 1:
        raise Exception("Email non envoyé par le serveur SMTP.")

    return sent_count
