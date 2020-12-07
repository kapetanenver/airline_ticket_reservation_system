#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import mysql.connector
from datetime import datetime
#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = mysql.connector.connect(host='localhost',
                       user='root',
                       password='',
                       database='airline_reservation')


#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = "SELECT * FROM user WHERE username = \'{}\' and password = md5(\'{}\')"
    cursor.execute(query.format(username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        session['account_type'] = data[2] #data[2] is the account_type :)
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    account_type = request.form['radio_answer']

#   if not len(password) >= 4:
#                flash("Password length must be at least 4 characters")
 #               return redirect(request.url)

    #cursor used to send queries

    cursor = conn.cursor()
    #executes query
    query = "SELECT * FROM user WHERE username = \'{}\'" # removed account_type check as username is primary key anyway
    cursor.execute(query.format(username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None

    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = "INSERT INTO user VALUES(\'{}\', md5(\'{}\'), \'{}\')"
        cursor.execute(ins.format(username, password, account_type))
        conn.commit()
        cursor.close()
        #flash("You are logged in") #additional functionality see comments in index.hmtl
        session['username'] = username
        session['account_type'] = account_type 
        session['password'] = password


        if account_type == 'customer':
            url_for = 'cus_register.html'
        elif account_type == 'booking_agent':
            url_for = 'booking_register.html'
        elif account_type == 'airline_staff':
            url_for = 'staff_register.html'

        return render_template(url_for, username = username, account_type = account_type)

@app.route('/home')
def home():
    username = session['username']
    account_type = session['account_type']
    cursor = conn.cursor()
    if account_type == 'customer':
        page_to_render = 'user_home_page.html'
        query_purchased_flights = "SELECT * FROM flight, purchases, ticket WHERE purchases.customer_email = \'{}\' AND purchases.ticket_id = ticket.ticket_id AND ticket.flight_num = flight.flight_num"
        cursor.execute(query_purchased_flights.format(username))
        data1 = cursor.fetchall() 

        #FOR SOME REASON NOT ALL UPCOMING FLIGHTS ARE DISPLAYED UPON SIGN IN
        #---------------------------------------------------------------------
        #SEEMS TO BE WORKING NOW???!!!

        query_all_flights= "SELECT * FROM flight WHERE flight.status = 'upcoming'"
        cursor.execute(query_all_flights)
        data2 = cursor.fetchall()


    elif account_type == 'booking_agent':
        page_to_render = 'booking_home_page.html'
        query2 = "SELECT * FROM flight, purchases, booking_agent, ticket WHERE booking_agent.email = \'{}\' AND purchases.booking_agent_id = booking_agent.booking_agent_id  AND purchases.ticket_id = ticket.ticket_id and flight.flight_num = ticket.flight_num"
        cursor.execute(query2.format(username))
        data1 = cursor.fetchall() 

        query_all_flights= "SELECT * FROM flight WHERE flight.status = 'upcoming'"
        cursor.execute(query_all_flights)
        data2 = cursor.fetchall()

    elif account_type == 'airline_staff':
        page_to_render = 'staff_home_page.html'
        cursor.execute(query)
        data1 = cursor.fetchall() 

    cursor.close()

    return render_template(page_to_render, username=username, purchased_flights=data1, all_flights=data2, account_type=account_type)

@app.route('/cus_register', methods=['GET', 'POST'])
def cus_register():
    #inserts details from customer_register into database
    account_type = session['account_type']
    if account_type == 'customer':
        username = session['username']
        password = session['password'] #PROLLY NOT THE SAFEST WAY TO GET PASSWORD FROM 1ST FROM TO 2ND FORM
        session['password'] = ''
    elif account_type == 'booking_agent':
        username = request.form['username']
        password = request.form['password']
    name = request.form['name']
    building_num = request.form['building_num']
    street = request.form['street']
    city = request.form['city']
    state = request.form['state']
    phone_num = request.form['phone_num']
    pass_num = request.form['pass_num']
    pass_exp = request.form['pass_exp']
    pass_country = request.form['pass_country']
    dob = request.form['dob']

    cursor = conn.cursor()
    ins = "INSERT INTO customer VALUES(\'{}\',\'{}\', md5(\'{}\'), \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')"
    cursor.execute(ins.format(username, name, password, building_num, street, city, state, phone_num, pass_num,pass_exp,pass_country,dob))
    conn.commit()   
    cursor.close()
    #then calls /home to get the new users homepage
    if account_type == 'customer':
        return redirect(url_for('home'))
    elif account_type =='booking_agent':
        flight_num = request.form['flight_num']
        flight_price = request.form['flight_price']
        return render_template('agent_purchase_confirm.html', data = username, flight_num= flight_num[:-1], flight_price= flight_price[:-1])

@app.route('/staff_register', methods=['GET', 'POST'])
def staff_register():
    #inserts details from staff_register into database
    username = session['username']
    password = session['password'] #PROLLY NOT THE SAFEST WAY TO GET PASSWORD FROM 1ST FROM TO 2ND FORM
    session['password'] = ''
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    dob = request.form['dob']
    airline_name = request.form['airline_name']
    
    cursor = conn.cursor()
    ins = "INSERT INTO airline_staff VALUES(\'{}\', md5(\'{}\'), \'{}\',\'{}\', \'{}\', \'{}\')"
    cursor.execute(ins.format(username, password, first_name, last_name, dob, airline_name))
    conn.commit()   
    cursor.close()
    #then calls /home to get the new users homepage
    return redirect(url_for('home'))

@app.route('/booking_register', methods=['GET', 'POST'])
def booking_register():
    #inserts details from booking_register into database
    username = session['username']
    password = session['password'] #PROLLY NOT THE SAFEST WAY TO GET PASSWORD FROM 1ST FROM TO 2ND FORM
    session['password'] = ''
    booking_ID = request.form['bookingID']

    cursor = conn.cursor()
    ins = "INSERT INTO booking_agent VALUES(\'{}\', md5(\'{}\'), \'{}\')"
    cursor.execute(ins.format(username, password, booking_ID))
    conn.commit()   
    cursor.close()
    #then calls /home to get the new users homepage
    return redirect(url_for('home'))

    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST': 
        departure_airport = request.form['dept_airport']
        arrival_airport = request.form['arrival_airport']
        departure_time = request.form['dept_time']

        cursor = conn.cursor();
        query = "SELECT flight_num, departure_time, arrival_time FROM flight"
        if departure_airport !='':
            query+= " where departure_airport = '%s'" %departure_airport

        if arrival_airport !='' and departure_airport =='':
            query += " where arrival_airport = '%s'" % arrival_airport
        elif arrival_airport !='' :
            query += " and arrival_airport = '%s'" %arrival_airport

        if departure_time != '' and (departure_airport =='' and arrival_airport ==''):
            query += ' where departure_time = "%s"' %departure_time
        elif departure_time != '':
            query += ' and departure_time = "%s"' %departure_time
        
        cursor.execute(query)
        data = cursor.fetchall() 
        cursor.close()
        return render_template('index.html', flights=data)
    else:
        return render_template('index.html')

    
@app.route('/user_search', methods=['GET', 'POST'])
def user_search():
    if request.method == 'POST': 
        departure_airport = request.form['dept_airport']
        arrival_airport = request.form['arrival_airport']
        departure_time = request.form['dept_time']

        cursor = conn.cursor();
        query = "SELECT * FROM flight"
        if departure_airport !='':
            query+= " where departure_airport = '%s'" %departure_airport

        if arrival_airport !='' and departure_airport =='':
            query += " where arrival_airport = '%s'" % arrival_airport
        elif arrival_airport !='' :
            query += " and arrival_airport = '%s'" %arrival_airport

        if departure_time != '' and (departure_airport =='' and arrival_airport ==''):
            query += ' where departure_time = "%s"' %departure_time
        elif departure_time != '':
            query += ' and departure_time = "%s"' %departure_time
        
        cursor.execute(query)
        data = cursor.fetchall() 
        cursor.close()
        return render_template('search_results.html', flights=data)
    else:
        return render_template('index.html')
    '''
    if request.method == 'POST': 
        #get input from form 
        departure_airport = request.form['dept_airport']
        arrival_airport = request.form['arrival_airport']
        departure_time = request.form['dept_time']
        #
        cursor = conn.cursor();
        query = "SELECT * FROM flight WHERE departure_airport = %s and arrival_airport = %s and departure_time = %s"
        cursor.execute(query, (departure_airport, arrival_airport, departure_time))
        data = cursor.fetchall() 
        cursor.close()
        return render_template('search_results.html', flights=data)
        '''

@app.route('/agent_search', methods=['GET', 'POST'])
def agent_search():
    '''
    if request.method == 'POST': 
        '''
    departure_airport = request.form['dept_airport']
    arrival_airport = request.form['arrival_airport']
    departure_time = request.form['dept_time']
    max_date = request.form['max_date']
    min_date = request.form['min_date']
    flag = request.form['booking']

    cursor = conn.cursor();
    if flag == "my":
        query = "SELECT * from flight, purchases, booking_agent, ticket WHERE booking_agent.email = '%s' and booking_agent.booking_agent_id = purchases.booking_agent_id and flight.flight_num = ticket.flight_num and purchases.ticket_id = ticket.ticket_id" %session['username']
        page_to_render = 'agent_search_results.html'
    else:
        query = "SELECT * FROM flight"
        if departure_airport =='' and arrival_airport =='' and departure_time =='' and max_date=='' and min_date=='':
            query +=' where flight.status = "upcoming"'
        else:
            query +=' where flight.status != ""'
        page_to_render = 'agent_search_results_all.html'
    if departure_airport !='':
        query+= " and flight.departure_airport = '%s'" %departure_airport
    if arrival_airport !='' :
        query += " and flight.arrival_airport = '%s'" %arrival_airport
    if departure_time != '':
        query += ' and flight.departure_time = "%s"' %departure_time
    if max_date !='' and min_date!='':
        query += ' and (flight.departure_time >= "%s"' %min_date
        query += ' and flight.departure_time <= "%s)"'%max_date
    elif max_date !='' and min_date == '':
        query += ' and flight.departure_time <= "%s"'%max_date
    elif min_date !=''and max_date == '':
        query += ' and flight.departure_time >= "%s"' %min_date
    cursor.execute(query)
    data = cursor.fetchall() 
    cursor.close()
    return render_template(page_to_render, flights=data)
    '''
    else:
        return render_template('booking_home_page.html')
        '''


@app.route('/purchase_flight', methods=['GET', 'POST'])
def purchase_flight():
    flight_num  = request.form['flight_num']
    session['flight_num'] = flight_num

    flight_price = request.form['flight_price']

    sesh = session['account_type']
    if sesh == 'booking_agent':
        page_to_render = 'agent_purchase_flight.html'
    else:
        page_to_render = 'purchase_flight.html'

    return render_template(page_to_render, flight_num=flight_num, flight_price=flight_price)


@app.route('/agent_confim_purchase', methods =['GET', 'POST'])
def agent_confrim_purchase():
    flight_num =session['flight_num']
    flight_price = request.form['flight_price'][:-1]
    username = session['username']
    flag = request.form['customer']
    if flag =='yes':
        page_to_render = 'agent_purchase_confirm.html'
    else:
        page_to_render = 'agent_create_customer.html'

    return render_template(page_to_render, flight_num=flight_num, flight_price=flight_price)


@app.route('/agent_insert_purchase', methods=['GET', 'POST'])
def agent_insert_purchase():
    flight_num = request.form['flight_num']
    username = session['username']
    customer_username = request.form['customer_username']
    cursor = conn.cursor()
    query1 = "SELECT ticket_id FROM ticket WHERE ticket.flight_num = '%s'" %int(flight_num)
    cursor.execute(query1)
    ticket = cursor.fetchall()
    cursor.close()
    ticket_id = ticket[0][0]

    todays_date =datetime.today().strftime('%Y-%m-%d')

    cursor = conn.cursor()
    agent_data = 'select booking_agent_id from booking_agent where email = "%s"' %username
    cursor.execute(agent_data)
    agent = cursor.fetchone()
    cursor.close()
    agent_id = int(agent[0])

    cursor = conn.cursor()
    ins = "INSERT INTO purchases VALUES(\'{}\',\'{}\',\'{}\',\'{}\')"
    cursor.execute(ins.format(ticket_id,customer_username,agent_id,todays_date))
    conn.commit()   
    cursor.close()

    return redirect(url_for('home'))

@app.route('/insert_purchase', methods=['GET', 'POST'])
def insert_purchase():
    if request.method == 'POST': 
        flight_num = session['flight_num']
        username = session['username']

        #use these to findout value of flightnum
        if len(flight_num) == 0:
            error = 'flight num'+ str(flight_num)
            return render_template('login.html', error=error)

        
        #first need to get ticket id from flight number 
        cursor = conn.cursor();
        query = "SELECT * FROM ticket WHERE ticket.flight_num = \'{}\'"
        cursor.execute(query.format(flight_num))
        data = cursor.fetchall()
        cursor.close()

        ticket_id = data[0][0]

        if ticket_id == 0:
            error = ticket_id
            return render_template('login.html', error=ticket_id)

        todays_date =datetime.today().strftime('%Y-%m-%d')

        cursor = conn.cursor()
        ins = "INSERT INTO purchases VALUES(\'{}\',\'{}\',NULL,\'{}\')"
        cursor.execute(ins.format(ticket_id,username,todays_date))
        conn.commit()   
        cursor.close()

        return redirect(url_for('home'))

        

        

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)