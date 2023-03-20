# objective-save data from HTML form to mysql using python
# flask-is a python library/framework used to develop web application
# flask uses HTML/CSS/python/SQL
from requests.auth import HTTPBasicAuth  # for developer authenticaton
import datetime  # get current time needed for transcation
import requests  # to post request to safaricom url
from werkzeug.security import generate_password_hash, check_password_hash
import base64   # its encoding scheme to encode data to be sent to url
from flask import *
import pymysql


# build a flask app
# (_name_) gives our app a default name
app = Flask(__name__)
app.secret_key = "hjhjgj6767jhjhghjghj"
# Routing Concept.
# To run a flask app you specify base url http://127.0.0.1:5000/your route


@app.route('/home')
def home():
    return 'This is my Good Home Page'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']
        phone = request.form['phone']

        if len(password1) < 8:
            return render_template('register.html', message="Password must be 8 XTERS")
        elif password1 != password2:
            return render_template('register.html', message="Password Do not match")
        else:
            connection = pymysql.connect(
                host='localhost', user='root', password='', database='oeridb')
            sql = "insert into signup(firstname, lastname, email, password, phone) VALUES(%s, %s, %s, %s, %s)"
            cursor = connection.cursor()
            cursor.execute(sql, (firstname, lastname, email, password2, phone))
            connection.commit()
            return render_template('signup.html', message="Account Created Successful")
    else:
        return render_template('signup.html')


# TODO LOGIN
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':  # works if users post
        email = request.form['email']
        password = request.form['password']

        connection = pymysql.connect(
            host='localhost', user='root', password='', database='oeridb')
        sql = 'select * from signup where email = %s and password = %s'

        # create a cursor
        cursor = connection.cursor()
        # execute sql,replacing placeholders with really values
        cursor.execute(sql, (email, password))

        # use cursor to check what SQL found in yuor table,count rows returned
        if cursor.rowcount == 0:
            return render_template('login.html', message="Wrong Credentials,Try Again")
        elif cursor.rowcount == 1:
            # return render_template('login.html', message = "Welcome, Login successful")-helps to see if code is working
            return redirect('/shop')  # after success login route to /book
        else:
            return render_template('login.html', message="Something went wrong, Contact Admin")

    else:
        # shows the form to the users to fill in detail
        return render_template('login.html')



# objective:retrive all products
@app.route('/shop')
def shop():
    connection = pymysql.connect(
        host='localhost', user='root', password='', database='oeridb')
    sql = "select * from buy "
    cursor = connection.cursor()
    cursor.execute(sql)

    # check if there is any product on the table
    if cursor.rowcount == 0:
        return render_template('shop.html', message='No product Found')
    else:
        rows = cursor.fetchall()
        return render_template('shop.html', data=rows)


@app.route('/single/<item_id>')
def single(item_id):
    # this route receives the item_id of the selected product
    # we do an sql and retrive details of the car above with item_id
    connection = pymysql.connect(
        host='localhost', user='root', password='', database='oeridb')
    sql = "select * from buy where item_id = %s"
    cursor = connection.cursor()
    cursor.execute(sql, (item_id))  # replace placeholder %s with item_id

    #  get the row holding this i product details
    row = cursor.fetchone()
    # we return the data holding one row to single.html
    return render_template('single.html', data=row)


# mpesa route

# https://github.com/modcomlearing/mpesa_sample
# open app.py
# copy from line 7 to 58


@app.route('/mpesa', methods=['POST', 'GET'])
def mpesa():
    if request.method == 'POST':
        # receive the phone and the amount
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # GENERATING THE ACCESS TOKEN
        # your get them from daraja portal
        consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
        consumer_secret = "amFbAoUByPV2rM5A"

        # we use the above credetials to aunthenticate

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(
            consumer_key, consumer_secret))
        # get an access token

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']
        print(access_token)

        #  GETTING THE PASSWORD
        # get current time from your comp
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        # pass the paybill pass key
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"  # This is daraja test paybill
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')
        print(password)

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": "account",
            "TransactionDesc": "account"
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return 'Please Complete Payment in Your Phone'
    else:
        return redirect('/hire')


# shopping Cart


@app.route('/add', methods=['POST'])
def add_product_to_cart():
    _quantity = int(request.form['quantity'])
    _code = request.form['code']
    # validate the received values
    if _quantity and _code and request.method == 'POST':
        connection = pymysql.connect(
        host='localhost', user='root', password='', database='oeridb')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM buy WHERE item_id= %s", _code)
        row = cursor.fetchone()
        # An array is a collection of items stored at contiguous memory locations. The idea is to store multiple items of the same type together

        itemArray = {str(row['item_id']): {'description': row['description'], 'item_id': row['item_id'], 'quantity': _quantity, 'offer_cost': row['offer_cost'],
                                         'image': row['image'], 'total_price': _quantity * row['offer_cost']}}
        print((itemArray))

        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        # if there is an item already
        if 'cart_item' in session:
            # check if the product you are adding is already there
            if row['item_id'] in session['cart_item']:

                for key, value in session['cart_item'].items():
                    # check if product is there
                    if row['item_id'] == key:
                        # take the old quantity  which is in session with cart item and key quantity
                        old_quantity = session['cart_item'][key]['quantity']
                        # add it with new quantity to get the total quantity and make it a session
                        total_quantity = old_quantity + _quantity
                        session['cart_item'][key]['quantity'] = total_quantity
                        # now find the new price with the new total quantity and add it to the session
                        session['cart_item'][key]['total_price'] = total_quantity * \
                            row['offer_cost']

            else:
                # a new product added in the cart.Merge the previous to have a new cart item with two products
                session['cart_item'] = array_merge(
                    session['cart_item'], itemArray)

            for key, value in session['cart_item'].items():
                individual_quantity = int(
                    session['cart_item'][key]['quantity'])
                individual_price = float(
                    session['cart_item'][key]['total_price'])
                all_total_quantity = all_total_quantity + individual_quantity
                all_total_price = all_total_price + individual_price

        else:
            # if the cart is empty you add the whole item array
            session['cart_item'] = itemArray
            all_total_quantity = all_total_quantity + _quantity
            # get total price by multiplyin the cost and the quantity
            all_total_price = all_total_price + _quantity * row['offer_cost']

        # add total quantity and total price to a session
        session['all_total_quantity'] = all_total_quantity
        session['all_total_price'] = all_total_price
        return redirect(url_for('.cart'))
    else:
        return 'Error while adding item to cart'


@app.route('/cart')
def cart():
    return render_template('cart.html')


def array_merge( first_array , second_array ):
     if isinstance( first_array , list) and isinstance( second_array , list ):
      return first_array + second_array
     #takes the new product add to the existing and merge to have one array with two products
     elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
      return dict( list( first_array.items() ) + list( second_array.items() ) )
     elif isinstance( first_array , set ) and isinstance( second_array , set ):
      return first_array.union( second_array )
     return False


@app.route('/empty')
def empty_cart():
    try:
        if 'cart_item' in session or 'all_total_quantity' in session or 'all_total_price' in session:
            session.pop('cart_item', None)
            session.pop('all_total_quantity', None)
            session.pop('all_total_price', None)
            return redirect(url_for('.cart'))
        else:
            return redirect(url_for('.cart'))

    except Exception as e:
        print(e)


@app.route('/delete/<string:code>')
def delete_product(code):
    try:
        all_total_price = 0
        all_total_quantity = 0
        session.modified = True
        for item in session['cart_item'].items():
            if item[0] == code:
                session['cart_item'].pop(item[0], None)
                if 'cart_item' in session:
                    for key, value in session['cart_item'].items():
                        individual_quantity = int(session['cart_item'][key]['quantity'])
                        individual_price = float(session['cart_item'][key]['total_price'])
                        all_total_quantity = all_total_quantity + individual_quantity
                        all_total_price = all_total_price + individual_price
                break

        if all_total_quantity == 0:
            session.clear()
        else:
            session['all_total_quantity'] = all_total_quantity
            session['all_total_price'] = all_total_price

        # return redirect('/')
        return redirect(url_for('.cart'))
    except Exception as e:
        print(e)


# debug=True enables debug mode on
app.run(debug=True)
