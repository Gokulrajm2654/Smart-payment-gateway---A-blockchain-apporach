from flask import Blueprint, request, flash, redirect, url_for, render_template 
import db_conns
import email_sender
import uuid
from datetime import datetime, timedelta

forgot_password_bp = Blueprint('forgot_password', __name__)

@forgot_password_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = db_conns.get_user_by_email(email)

        if user:
            # Generate a unique token
            token = str(uuid.uuid4())  
            expiration_time = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

            # Save the token and expiration in the database
            db_conns.save_reset_token(email, token, expiration_time)  # Implement this function in db_conns

            # Create a reset link with the token
            reset_link = url_for('reset_password', token=token, _external=True)

            # Send the reset email
            email_sender.send_reset_email(email, reset_link)
            flash("A password reset link has been sent to your email address.")
        else:
            flash("Email not found. Please check and try again.")

        return redirect(url_for('forgot_password.forgot_password'))

    return render_template('forgot_password.html')  # Render the forgot password template
