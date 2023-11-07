from flask import render_template, session, flash, redirect, url_for, Blueprint

delivery = Blueprint('delivery', __name__)


from app import mysql
@delivery.route('/agentdetail', methods=['GET'])
def agentdetail():
    ans = False
    try:
        ans = session['agentbool']
        agent_ID = session['agent_ID']
        print("agent_ID",agent_ID)
        agent_name = False
    except: 
        msg = "Need to login as agent"
        flash(msg)
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("select agent_ID, first_name, last_name, email, phone_no from delivery_agent where agent_ID=%s;",(agent_ID,))
    agent_detail = cur.fetchone()
    query = "SELECT order_ID, order_status, delivery_ID, restaurant_ID, customer_ID FROM orders WHERE order_id IN (SELECT order_id FROM delivery_agent WHERE agent_id = %s) ORDER BY order_placed_time DESC limit 10"
    cust_query = "SELECT phone_no from customers where customer_ID=%s"
    add_query = "SELECT building_name, street_name, city, state, pin_code from address where address_ID=%s"
    delivery_query = "SELECT delivery_address, delivery_charges, pickup_time, delivery_time from delivery_detail where delivery_ID=%s"
    cur.execute(query, (agent_ID,))
    orders_rest = cur.fetchall()
    delivery_order = []
    for detail in orders_rest:
        temp = {
            'order_ID': detail[0],
            'order_status': detail[1],
        }
        delivery_ID = detail[2]
        if (delivery_ID != None):
            cur.execute(delivery_query, (delivery_ID,))
            delivery_detail = cur.fetchone()
            del_add = delivery_detail[0]

            temp['delivery_charge'] = delivery_detail[1]
            temp['pickup_time'] = delivery_detail[2]
            temp['delivery_time'] = delivery_detail[3]
            
            cur.execute(add_query, (del_add,))
            address = cur.fetchone()
            temp['delivery_add'] = str(address[0]) +" " +str(address[1]) + " " + str(address[2]) + " " + str(address[3]) + " " + str(address[4])
        else:
            temp['delivery_charge'] = "None"
            temp['pickup_time'] = "None"
            temp['delivery_time'] = "None"
            temp['delivery_add'] = "Missing for now"
        
        rest_ID = detail[3]
        cur.execute(add_query, (rest_ID,))
        rest_add = cur.fetchone()
        temp['rest_add'] = str(rest_add[0]) +" " +str(rest_add[1]) + " " + str(rest_add[2]) + " " + str(rest_add[3]) + " " + str(rest_add[4])
        
        cust_ID = detail[4]
        cur.execute(cust_query, (cust_ID,))
        cust_contact = cur.fetchone()
        temp['phone_number'] = cust_contact[0]
        delivery_order.append(temp)

    return render_template('delivery/agentdetail.html', address = delivery_order[0]['delivery_add'], agent_detail=agent_detail, delivery_order=delivery_order)

