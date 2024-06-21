from tkinter import *
from tkinter import messagebox as msg
import mysql.connector as mysql
import re
import hashlib
import os
import hmac

SALT_LENGTH = 16
HASH_NAME = 'sha256'
ITERATIONS = 100000


def initialize_connection():
    try:
        conn = mysql.connect(host="localhost", user="root", password="asdfg123")
        cursor = conn.cursor()
        create_database(cursor)
        cursor.execute("USE banking")
        create_table(cursor)
        return conn, cursor
    except mysql.Error as e:
        msg.showerror(f"Error connecting to MySQL: {e}")
        raise


def create_database(cursor):
    cursor.execute("SHOW DATABASES")
    temp = cursor.fetchall()
    databases = [item[0] for item in temp]
    if "banking" not in databases:
        cursor.execute("CREATE DATABASE banking")


def create_table(cursor):
    cursor.execute("SHOW TABLES")
    temp = cursor.fetchall()
    tables = [item[0] for item in temp]

    if "users" not in tables:
        cursor.execute("""CREATE TABLE users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            firstname VARCHAR(255),
            lastname VARCHAR(255),
            username VARCHAR(255) UNIQUE,
            password VARCHAR(255),
            email VARCHAR(255) UNIQUE,
            phoneno VARCHAR(10),
            balance DECIMAL(10, 2) DEFAULT 0.00  -- Added balance column
        )""")

    if "account" not in tables:
        cursor.execute("""CREATE TABLE account (
            username VARCHAR(50) NOT NULL,
            acc_no VARCHAR(20),
            IFSC VARCHAR(20),
            branch VARCHAR(50)
        )""")


    if "transactions" not in tables :
        cursor.execute("""CREATE TABLE transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        amount DECIMAL(10, 2),
        description TEXT,
        FOREIGN KEY (username) REFERENCES users(username)
    )""")


conn, cursor = initialize_connection()


def main_screen():
    global login_screen, username_entry, password_entry, username_verify, password_verify

    login_screen = Tk()
    login_screen.title("Login")
    login_screen.geometry("850x850")
    login_screen.state('zoomed')
    login_screen.resizable(False, False)
    Label(login_screen, text="IT Bank'Infinity Bank' - Together Towards Prosperity", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
    login_screen['background'] = "#f0f0f0"

    username_verify = StringVar()
    password_verify = StringVar()

    Label(login_screen, text="Login", font=("Calibri", 40, 'italic'), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)
    
    Label(login_screen, text="Username * ", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
    
    username_entry = Entry(login_screen, textvariable=username_verify, font=("Calibri", 20), bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    username_entry.place(x=350, y=350)
    
    Label(login_screen, text="Password * ", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=430)
    
    password_entry = Entry(login_screen, textvariable=password_verify, show='*', font=("Calibri", 20), bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    password_entry.place(x=350, y=430)

    checkbox = Checkbutton(login_screen, command=show_password,cursor="hand2", bg="#f0f0f0", fg="#001f3f").place(x=350, y=470)
    Label(login_screen, text="Show password", bg="#f0f0f0", fg="#001f3f").place(x=375, y=472)

    Button(login_screen, text="Sign In", height="1", width="8", fg='black', bg='#aeafb3', font=("Arial Bold", 15),cursor="hand2", command=login_verify).place(x=200, y=500)
    
    Button(login_screen, text="Sign up", height="1", width="8", fg='#001f3f', bg='#f0f0f0', bd='0', font=("Arial Bold", 10),cursor="hand2", command=sign_up_btn).place(x=360, y=572) 
    Label(login_screen, text="Don't have an account?", font=("Calibri", 13), bg="#f0f0f0", fg="#001f3f").place(x=200, y=570)


    login_screen.mainloop()

def login_verify():
    global username_entry, password_entry
    username = username_entry.get()
    password = password_entry.get()

    if username == "" or password == "":
        msg.showerror("Warning", "Enter all fields")
    else:
        if is_user_in_database(username, password):
            msg.showinfo("", f"Logged in successfully as {username}")
            login_screen.destroy()
            home_page(username)
        
        else:
            msg.showerror("Error", "Invalid username or password")

def is_user_in_database(username, password):
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    return cursor.fetchone() is not None


def verify_password(stored_password, provided_password):
    try:
        stored_password_bytes = bytes.fromhex(stored_password)
    except ValueError:
        return False
    
    salt = stored_password_bytes[:SALT_LENGTH]
    stored_hash = stored_password_bytes[SALT_LENGTH:]
    
    provided_hash = hashlib.pbkdf2_hmac(HASH_NAME, provided_password.encode(), salt, ITERATIONS)
    
    return hmac.compare_digest(stored_hash, provided_hash)




def register():
    global register_screen, firstname_entry, lastname_entry, username_entry, password_entry, email_entry, phoneno_entry

    register_screen = Tk()
    register_screen.title("Register")
    register_screen.geometry("850x850")
    register_screen.state('zoomed')
    register_screen.resizable(False, False)
    Label(register_screen, text="IT Bank'Infinity Bank' - Together Towards Prosperity", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
    register_screen['background'] = "#f0f0f0"

    username_var = StringVar()
    password_var = StringVar()
    firstname_var = StringVar()
    lastname_var = StringVar()
    email_var = StringVar()
    phoneno_var = StringVar()

    f1 = ("Calibri", 16)
    f2 = ("Calibri", 18)

    Label(register_screen, text="Register", font=("Calibri", 40, 'italic'), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)

    Label(register_screen, text="First name * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
    Label(register_screen, text="Last name * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=650, y=350)
    Label(register_screen, text="Username * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=200, y=430)
    Label(register_screen, text="Password * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=650, y=430)
    Label(register_screen, text="E-mail * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=200, y=510)
    Label(register_screen, text="Phone no. * ", font=f1, bg="#f0f0f0", fg="#001f3f").place(x=650, y=510)

    firstname_entry = Entry(register_screen, textvariable=firstname_var, font=f2,bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    firstname_entry.place(x=330, y=350)
    lastname_entry = Entry(register_screen, textvariable=lastname_var, font=f2,bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    lastname_entry.place(x=850, y=350)
    username_entry = Entry(register_screen, textvariable=username_var, font=f2,bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    username_entry.place(x=330, y=430)
    password_entry = Entry(register_screen, textvariable=password_var, font=f2, show='*',bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    password_entry.place(x=850, y=430)
    

    checkbox = Checkbutton(register_screen, command=show_password_register,cursor="hand2", bg="#f0f0f0", fg="#001f3f").place(x=850, y=470)
    Label(register_screen, text="Show password", bg="#f0f0f0", fg="#001f3f").place(x=875, y=472)


    email_entry = Entry(register_screen, textvariable=email_var, font=f2,bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    email_entry.place(x=330, y=510)
    phoneno_entry = Entry(register_screen, textvariable=phoneno_var, font=f2,bg='#001f3f', fg="#f0f0f0",insertbackground='white')
    phoneno_entry.place(x=850, y=510)

    Button(register_screen, text="Sign Up", height="1", width="8", fg='black', bg='#aeafb3', font=("Arial Bold", 15),cursor="hand2", command=register_user).place(x=200, y=600)

    Button(register_screen, text="Sign in", height="1", width="8", bg="#f0f0f0", fg="#001f3f", bd='0', font=("Arial Bold", 10),cursor="hand2", command=sign_in_btn).place(x=372, y=662) 
    Label(register_screen, text="Already have an account?", font=("Calibri", 13),bg="#f0f0f0", fg="#001f3f").place(x=200, y=660)

    register_screen.mainloop()


def sign_up_btn():
    login_screen.destroy()
    register()
    
def sign_in_btn():
    register_screen.destroy()
    main_screen()

def sign_out_btn():
    home_screen.destroy()
    main_screen()

def back_to_home(username, screen):
    screen.destroy()
    home_page(username)
    

def show_password():
    global password_entry
    
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
    else:
        password_entry.config(show='*')

def show_password_register():
    global password_entry
    
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
    else:
        password_entry.config(show='*')


def register_user():
    global username_entry, password_entry, firstname_entry, lastname_entry, email_entry, phoneno_entry

    username_info = username_entry.get()
    password_info = password_entry.get()
    firstname_info = firstname_entry.get()
    lastname_info = lastname_entry.get()
    email_info = email_entry.get()
    phoneno_info = phoneno_entry.get()

    
    if username_info == "" or password_info == "" or firstname_info == "" or lastname_info == "" or email_info == "" or phoneno_info == "":
        msg.showerror("Warning", "Enter All Fields")
        return
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email_info):
        msg.showerror("Warning", "Invalid Email Address")
        return
    elif not re.match(r"^\d{10}$", phoneno_info):
        msg.showerror("Warning", "Invalid Phone Number")
        return

    conn, cursor = initialize_connection()

    try:
        cursor.execute("INSERT INTO users (firstname, lastname, username, password, email, phoneno) VALUES (%s, %s, %s, %s, %s, %s)",
                       (firstname_info, lastname_info, username_info, password_info, email_info, phoneno_info))
        conn.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        last_inserted_id = cursor.fetchone()[0]

        acc_no = f"100123{last_inserted_id + 10}"

        cursor.execute("INSERT INTO account (username, acc_no, IFSC, branch) VALUES (%s, %s, %s, %s)",
                       (username_info, acc_no, "IT0001201", "Chennai"))
        conn.commit()

        msg.showinfo("Success", "Registration Successful")
        register_screen.destroy()
        main_screen()

    except mysql.Error as err:
        conn.rollback()
        if err.errno == 1062:
            msg.showerror("Error", "Username or Email already exists")
        else:
            msg.showerror("Error", f"Error inserting data into database: {err}")
    finally:
        conn.close()


def user_info(username):
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    return cursor.fetchone()

def fetch_account_details(username):
    try:
        cursor.execute("""
            SELECT u.firstname, u.lastname, u.email, u.phoneno, a.acc_no, a.IFSC, a.branch
            FROM users u
            JOIN account a ON u.username = a.username
            WHERE u.username = %s
        """, (username,))
        return cursor.fetchone()
    except mysql.Error as e:
        msg.showerror("Error", f"Error fetching account details: {e}")


def account_details_page(username):
    global account_details_screen
    account_details_screen = Tk()
    account_details_screen.title("Account Details")
    account_details_screen.geometry("850x850")
    account_details_screen.state('zoomed')
    account_details_screen.resizable(False, False)
    

    home_screen.destroy()


    Label(account_details_screen, text="IT Bank'Infinity Bank' - Together Towards Prosperity", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
    account_details_screen['background'] = "#f0f0f0"

    Label(account_details_screen, text="Account Details", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)

    details = fetch_account_details(username)
    if details:
        firstname, lastname, email, phoneno, acc_no, ifsc, branch = details
        Label(account_details_screen, text=f"First Name: {firstname}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
        Label(account_details_screen, text=f"Last Name: {lastname}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=400)
        Label(account_details_screen, text=f"Email: {email}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=450)
        Label(account_details_screen, text=f"Phone Number: {phoneno}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=500)
        Label(account_details_screen, text=f"Account Number: {acc_no}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=550)
        Label(account_details_screen, text=f"IFSC Code: {ifsc}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=600)
        Label(account_details_screen, text=f"Branch: {branch}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=650)

    Button(account_details_screen, text="Back to Home", height="1", width="11", fg='white', bg='#001f3f', bd='0', font=("Arial Bold", 10), command=lambda: back_to_home(username, account_details_screen)).place(x=1400, y=700)


def home_page(username):
    global home_screen
    user_data = user_info(username)

    balance = fetch_account_balance(username)

    if balance is not None:

        firstname, lastname = user_data[1], user_data[2]
        
        home_screen = Tk()
        home_screen.title("Home Page")
        home_screen.geometry("850x850")
        home_screen.state('zoomed')
        home_screen.resizable(False, False)
        Label(home_screen, text="IT Bank'Infinity Bank' - Together Towards Prosperity", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
        home_screen['background'] = "#f0f0f0"
    
        Label(home_screen, text=f"Welcome, {firstname} {lastname}", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)
        Label(home_screen, text=f"Your Account Balance: {balance}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
    
        Button(home_screen, text="Account Details", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: account_details_page(username)).place(x=230, y=450)
        Button(home_screen, text="Transactions", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: transactions_page(username)).place(x=230, y=550)
        Button(home_screen, text="Transfer funds", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: transfer_funds_page(username)).place(x=230, y=650)
        Button(home_screen, text="Log out", height="1", width="8", fg='white', bg='#001f3f', bd='0', font=("Arial Bold", 10), cursor="hand2", command=sign_out_btn).place(x=1450, y=700)
    
        home_screen.mainloop()
    
    elif balance is None:
        home_screen = Tk()
        home_screen.title("Home Page")
        home_screen.geometry("850x850")
        home_screen.state('zoomed')
        home_screen.resizable(False, False)
        Label(home_screen, text="IT Bank'Infinity Bank' - Together Towards Prosperity", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
        home_screen['background'] = "#f0f0f0"
    
        Label(home_screen, text=f"Welcome, {username}", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)
        Label(home_screen, text=f"Your Account Balance: {balance}", font=("Calibri", 20), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
    
        Button(home_screen, text="Account Details", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: account_details_page(username)).place(x=230, y=450)
        Button(home_screen, text="Transactions", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: transactions_page(username)).place(x=230, y=550)
        Button(home_screen, text="Transfer funds", height="1", width="17", bg='#001f3f', fg='#f0f0f0', bd='2', font=("Arial Bold", 15), cursor="hand2", command=lambda: transfer_funds_page(username)).place(x=230, y=650)
        Button(home_screen, text="Log out", height="1", width="8", fg='white', bg='#001f3f', bd='0', font=("Arial Bold", 10), cursor="hand2", command=sign_out_btn).place(x=1450, y=700)
    
        home_screen.mainloop()

def fetch_account_balance(username):
    try:
        cursor.execute("SELECT balance FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            return result[0]
        else:
            return None  # Handle case where user not found or balance is not retrieved
        
    except mysql.Error as e:
        msg.showerror("Error", f"Error fetching account balance: {e}")
        return None




def transactions_page(username):
    global transactions_screen

    home_screen.destroy()

    transactions_screen = Tk()
    transactions_screen.title("Transactions")
    transactions_screen.geometry("850x850")
    transactions_screen.state('zoomed')
    transactions_screen.resizable(False, False)
    
    Label(transactions_screen, text="IT Bank'Infinity Bank' - Transactions", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
    transactions_screen['background'] = "#f0f0f0"

    Label(transactions_screen, text="Recent Transactions", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)

    transactions = fetch_transactions(username)

    if transactions:
        y_position = 350
        for transaction in transactions:
            transaction_date, amount, description = transaction
            Label(transactions_screen, text=f"Date: {transaction_date}", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=y_position)
            Label(transactions_screen, text=f"Amount: {amount}", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=400, y=y_position)
            Label(transactions_screen, text=f"Description: {description}", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=600, y=y_position)
            y_position += 50
    else:
        Label(transactions_screen, text="No transactions found.", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)

    Button(transactions_screen, text="Back to Home", height="1", width="11", fg='white', bg='#001f3f', bd='0', font=("Arial Bold", 10), command=lambda: back_to_home(username, transactions_screen)).place(x=1400, y=700)

    transactions_screen.mainloop()




def fetch_transactions(username):
    try:
        cursor.execute("""
            SELECT transaction_date, amount, description
            FROM transactions
            WHERE username = %s
            ORDER BY transaction_date DESC
        """, (username,))
        return cursor.fetchall()
    except mysql.Error as e:
        msg.showerror("Error", f"Error fetching transactions: {e}")


def transfer_funds(username, to_account, ifsc, amount):
    try:
        # Fetch current user's balance
        cursor.execute("SELECT balance FROM users WHERE username = %s", (username,))
        current_balance = cursor.fetchone()
        
        if current_balance is None:
            msg.showerror("Error", "Could not fetch your current balance.")
            return False
        
        current_balance = current_balance[0]
        
        # Check if current balance is sufficient
        if current_balance < amount:
            msg.showerror("Error", "Insufficient funds.")
            return False
        
        # Fetch recipient's balance
        cursor.execute("SELECT balance FROM account WHERE acc_no = %s AND IFSC = %s", (to_account, ifsc))
        recipient_balance = cursor.fetchone()
        
        if recipient_balance is None:
            msg.showerror("Error", "Recipient account not found.")
            return False
        
        recipient_balance = recipient_balance[0]
        
        # Update balances
        updated_sender_balance = current_balance - amount
        updated_recipient_balance = recipient_balance + amount
        
        # Perform the transaction
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (updated_sender_balance, username))
        cursor.execute("UPDATE account SET balance = %s WHERE acc_no = %s AND IFSC = %s", (updated_recipient_balance, to_account, ifsc))
        
        conn.commit()
        msg.showinfo("Success", f"Amount of {amount} transferred successfully.")
        return True
    
    except mysql.Error as e:
        conn.rollback()
        msg.showerror("Error", f"Transaction failed: {e}")
        return False



def deposit_funds(username, amount):
    try:
        cursor.execute("SELECT balance FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result is None:
            msg.showerror("Error", f"User '{username}' not found.")
            return False
        
        current_balance = result[0]
        
        if current_balance is None:
            current_balance = 0
        
        updated_balance = current_balance + amount
        cursor.execute("UPDATE users SET balance = %s WHERE username = %s", (updated_balance, username))
        conn.commit()
        msg.showinfo("Success", f"Successfully deposited {amount} into your account.")
        
        return True

    except mysql.Error as e:
        conn.rollback()
        msg.showerror("Error", f"Error depositing funds: {e}")
        return False



def transfer_funds_page(username):
    global transfer_screen

    home_screen.destroy()

    transfer_screen = Tk()
    transfer_screen.title("Transfer Funds")
    transfer_screen.geometry("850x850")
    transfer_screen.state('zoomed')
    transfer_screen.resizable(False, False)
    
    Label(transfer_screen, text="IT Bank'Infinity Bank' - Transfer Funds", bg='#001f3f', fg="#f0f0f0", width="300", height="5", font=("Calibri", 25, 'italic')).pack()
    transfer_screen['background'] = "#f0f0f0"

    Label(transfer_screen, text="Transfer Funds", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=250)

    Label(transfer_screen, text="To Account: ", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=350)
    to_account_entry = Entry(transfer_screen, font=("Calibri", 18))
    to_account_entry.place(x=350, y=350)

    Label(transfer_screen, text="IFSC: ", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=400)
    ifsc_entry = Entry(transfer_screen, font=("Calibri", 18))
    ifsc_entry.place(x=350, y=400)

    Label(transfer_screen, text="Amount: ", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=450)
    amount_entry = Entry(transfer_screen, font=("Calibri", 18))
    amount_entry.place(x=350, y=450)

    Button(transfer_screen, text="Transfer", height="1", width="10", fg='black', bg='#aeafb3', font=("Arial Bold", 15), cursor="hand2", command=lambda: transfer_funds(username, to_account_entry.get(), ifsc_entry.get(), float(amount_entry.get()))).place(x=200, y=500)

    Label(transfer_screen, text="Deposit Funds", font=("Calibri", 30), bg="#f0f0f0", fg="#001f3f").place(x=200, y=550)

    Label(transfer_screen, text="Amount: ", font=("Calibri", 18), bg="#f0f0f0", fg="#001f3f").place(x=200, y=600)
    deposit_amount_entry = Entry(transfer_screen, font=("Calibri", 18))
    deposit_amount_entry.place(x=350, y=600)

    Button(transfer_screen, text="Deposit", height="1", width="10", fg='black', bg='#aeafb3', font=("Arial Bold", 15), cursor="hand2", command=lambda: deposit_funds(username, float(deposit_amount_entry.get()))).place(x=200, y=650)

    Button(transfer_screen, text="Back to Home", height="1", width="12", fg='white', bg='#001f3f', bd='0', font=("Arial Bold", 10), command=lambda: back_to_home(username, transfer_screen)).place(x=1400, y=700)

    transfer_screen.mainloop()


if __name__ == "__main__":
    conn, cursor = initialize_connection()
    main_screen()

