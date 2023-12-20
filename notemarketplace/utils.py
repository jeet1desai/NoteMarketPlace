from django.core.mail import send_mail

def send_custom_email(subject, message, recipient_list):
    from_email='notemarketplace4@gmail.com'
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

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

def send_welcome_mail(password, email):
    subject = 'Welcome! NoteMarketPlace'
    message = f'password: {password}'
    recipient_list = [email]
    send_custom_email(subject, message, recipient_list)

def send_contact_us_mail(data):
    subject = data.get('subject')
    message = f'name: {data.get("full_name")} \nemail: {data.get("user_email")} \n\ncomment: {data.get("comment")}'
    recipient_list = [data.get('email'), data.get('user_email')]
    send_custom_email(subject, message, recipient_list)

def send_buyer_download_mail(user, seller_user, original_note):
    subject = f"Purchased book: {original_note.title}"
    message = f'As this is paid note - seller will contact you for payment \nSeller email: {seller_user.email}'
    recipient_list = [user.email]
    send_custom_email(subject, message, recipient_list)

def send_seller_download_mail(user, buyer_user, original_note):
    subject = f"{buyer_user.first_name} {buyer_user.last_name} wants to purchase your notes"
    message = f'Note: {original_note.title} \nAllow download access to Buyer if you have received the payment from him.'
    recipient_list = [user.email]
    send_custom_email(subject, message, recipient_list)

def send_buyer_allow_download_mail(email, seller, note):
    subject = f"{seller.first_name} {seller.last_name} allow you to download the note {note.title}"
    message = f'Please check my download page.'
    recipient_list = [email]
    send_custom_email(subject, message, recipient_list)