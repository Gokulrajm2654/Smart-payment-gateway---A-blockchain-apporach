from flask import Flask, request, send_file, make_response, url_for, render_template, flash, session, redirect
import db_conns
import email_sender
from web3 import Web3, exceptions
import qr_gen
import hashlib
import time
import re
from forgot_password import forgot_password_bp

PERF_METRICS = " ---PERFORMANCE METRICS--- "

def validate_password(password):
    # Define the password constraints
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    # At least one capital letter, one small letter, and one number
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):   
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    if not re.match(r"^[A-Za-z0-9!@#$%^&*()_+{}\[\]:;<>,.?~\\-]+$", password):
        return False, "Password can only contain alphanumeric characters and special characters."

    return True, "Password is valid."

def hash_password(password):
    # Check if the password meets the constraints
    valid, message = validate_password(password)
    if not valid:
        raise ValueError(message)

    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    
    return hashed_password

def hash_passwordlogin(password):

    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    
    return hashed_password

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Register the forgot password blueprint
app.register_blueprint(forgot_password_bp)

URL = "HTTP://127.0.0.1:7545"

@app.route('/')
def Login():
    return render_template("loader.html")

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form['new_password']
        
        # Verify the token and retrieve the associated email
        email = db_conns.get_email_by_token(token)  # Ensure this function is implemented in your db_conns module
        if email:
            hashed_password = hash_password(new_password)  # Hash the new password
            db_conns.update_password_by_email(email, hashed_password)  # Update the password in the database
            db_conns.delete_token(token)  # Optionally delete the token after use
            flash("Your password has been reset successfully.")
            return redirect(url_for('login'))  # Redirect to the login page
        else:
            flash("Invalid or expired token.")

    return render_template('reset_password.html', token=token)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Hash the entered password
        try:
            hashed_password = hash_passwordlogin(password)
        except ValueError as ve:
            flash(str(ve), 'error')  # Send the error message to the template
            return render_template("login.html")  # Return to the login page with error

        # Check the login credentials
        lis = db_conns.login(username, hashed_password)
        
        # Get the current number of failed attempts
        failed_attempts = db_conns.get_failed_attempts(username) or 0
        
        if len(lis) > 0:
            # Reset failed attempts on successful login
            db_conns.update_failed_attempts(username, 0)
            return redirect(url_for('home') + f"?username={username}")
        else:
            # Increment the failed attempts
            failed_attempts += 1
            db_conns.update_failed_attempts(username, failed_attempts)

            if failed_attempts >= 3:
                # Send alert email
                email_sender.send_alert_email(username)  # Add the receiver_email parameter as needed
                
            flash("Login failed, Check your credentials...")
            return render_template("login.html")
    else:
        return render_template("login.html")


  


@app.route('/signup', methods=["GET", "POST"])
def signup():
    global PERF_METRICS 
    if request.method == "POST":
        t1 = time.time()
        username = request.form['username']
        password = request.form['password']
        priv_key = request.form['priv_key']
        acc_addr = request.form['acc_addr']
        email = request.form['email']

        # Validate password before hashing
        try:
            hashed_password = hash_password(password)
        except ValueError as ve:
            flash(str(ve), 'error')  # Send the error message to the template
            return render_template("login.html")  # Show the signup page again with error

        db_conns.signup(username, acc_addr, priv_key, hashed_password, email)
        email_sender.send_confirmation_email(email,username)
        flash("Account Created Successfully...")
        PERF_METRICS += "\nTime taken to create account: " + str(time.time() - t1)
        with open("performance.txt", "w") as f:
            f.write(PERF_METRICS)
        
    return redirect(url_for('login'))

@app.route('/home', methods=["GET", "POST"])
def home():
    username = request.args.get('username').replace("'", "")
    
    print("username is: -----------------------: ", username)
    priv_key = db_conns.getPrivateKey(username)
    acc_addr = db_conns.getAccountAddress(username)
    return render_template("home.html", user=username, address=acc_addr, privateKey=priv_key)

@app.route('/sendEth', methods=["GET", "POST"])
def sendEth():
    username = request.form['username']
    priv_key = db_conns.getPrivateKey(username)
    from_acc = db_conns.getAccountAddress(username)
    
    return render_template("sendEth.html", user=username, address=from_acc, privateKey=priv_key)

@app.route('/sentMsg', methods=["GET", "POST"])
def sentMsg():
    global PERF_METRICS 
    t1 = time.time()
    username = request.form['username']
    priv_key = db_conns.getPrivateKey(username)
    from_acc = db_conns.getAccountAddress(username)
    
    if 'Amount' in request.form.keys():
        amount = request.form['Amount']
        to_acc = request.form['ReceiverAddress']
        url = URL
        web3 = Web3(Web3.HTTPProvider(url))
        nonce = web3.eth.get_transaction_count(from_acc)

        tx = {
            'nonce': nonce,
            'to': to_acc,
            'value': web3.to_wei(amount, 'ether'),
            'gas': 2_000_000,
            'gasPrice': web3.to_wei('50', 'gwei')
        }
        message = ""
        try:
            signed_tx = web3.eth.account.sign_transaction(tx, priv_key)
            tx_hash = (web3.eth.send_raw_transaction(signed_tx.raw_transaction)) 
            tx_hash = web3.to_hex(tx_hash)
            message = "Sent Successfully!!!"
        except ValueError:
            message = "Insufficient Funds!!!"
            tx_hash = "---"
        except exceptions.InvalidAddress as e:
            message = "Invalid Sender Address: " + e.args[0].split(" ")[-1][1:-1]
            tx_hash = "---"
        except TypeError as e:
            error_message = str(e)
            start = error_message.find("'to': '") + 6
            end = error_message.find("'", start)
            address = error_message[start:end]
            message = "Invalid Receiver Address: " + address
            tx_hash = "---"
        
        PERF_METRICS += "\nTime taken to send eth: " + str(time.time() - t1)
        with open("performance.txt", "w") as f:
            f.write(PERF_METRICS)
        return render_template("sentMsg.html", message=message,
                               username=username, s_addr=from_acc, r_addr=to_acc, amt=amount, txn_hash=tx_hash)

@app.route('/receiveEth', methods=["GET", "POST"])
def receiveEth():
    global PERF_METRICS 
    t1 = time.time()
    username = request.form['username']
    from_acc = db_conns.getAccountAddress(username)
    qr_gen.generate_qr_code(from_acc)
    PERF_METRICS += "\nTime taken for qr generation: " + str(time.time() - t1)
    with open("performance.txt", "w") as f:
        f.write(PERF_METRICS)
    return render_template('receiveEth.html', addr=from_acc, username=username)

@app.route('/checkBalance', methods=["GET", "POST"])
def checkBalance():
    global PERF_METRICS 
    t1 = time.time()
    username = request.form['username']
    url = URL
    web3 = Web3(Web3.HTTPProvider(url))
    address = db_conns.getAccountAddress(username)
    balance_wei = web3.eth.get_balance(address)
    balance_ether = web3.from_wei(balance_wei, 'ether')
    PERF_METRICS += "\nTime taken to check balance: " + str(time.time() - t1)
    with open("performance.txt", "w") as f:
        f.write(PERF_METRICS)
    return render_template('checkBalance.html', addr=address, bal=balance_ether, username=username)

if __name__ == '__main__':
    try:
        app.run(host="0.0.0.0", port=5002, debug=True)
    except KeyboardInterrupt:
        print(PERF_METRICS)
