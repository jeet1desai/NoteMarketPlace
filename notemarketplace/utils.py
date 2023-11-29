from django.core.mail import send_mail, EmailMessage

def send_custom_email(subject, message, recipient_list):
    # Send mail using send_mail function
    from_email='notemarketplace4@gmail.com'
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,  # Set this to True to suppress errors (not recommended in production)
    )

    # Alternatively, you can use EmailMessage for more customization
    # email = EmailMessage(subject, message, from_email, recipient_list)
    # email.send()

def send_email_verification_mail(id, email):
    clientURL = 'notemarketplace.netlify.app'
    subject = 'Email Verification Mail'
    message = f'{clientURL}/email/confirm/{id}'
    recipient_list = [email]
    send_custom_email(subject, message, recipient_list)

def send_reset_password_mail(password, email):
    subject = 'Forget Password'
    message = f'{password}'
    recipient_list = [email]
    send_custom_email(subject, message, recipient_list)
