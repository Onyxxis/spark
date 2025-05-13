from django.core.mail import send_mail

def send_reservation_confirmation_email(user_email, service_nom, date, heure):
    subject = "Confirmation de votre réservation - SparkWash Pro"
    message = f"""
Bonjour,

Votre réservation a été confirmée !

🧼 Service : {service_nom}
📅 Date : {date}
⏰ Heure : {heure}
📍 Adresse : SparkWash Pro - Lomé, Togo (quartier Agoè)

Merci pour votre confiance !
L'équipe SparkWash Pro.
    """.strip()

    send_mail(subject, message, None, [user_email])
