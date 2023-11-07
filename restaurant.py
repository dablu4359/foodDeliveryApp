from flask import jsonify, render_template, session, flash, request, redirect, url_for, Blueprint

restaurant = Blueprint('restaurant', __name__)

from app import mysql

@restaurant.route('/restaurants', methods=['GET'])
def get_restaurants():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT name FROM restaurant')
    restaurants = cursor.fetchall()
    cursor.close()
    return jsonify(restaurants)

@restaurant.route('/restdetail', methods=['GET'])
def restdetail():
    rest_name = False
    try:
        ans = session['restbool']
        rest_ID = session['restaurant_ID']
        rest_name = False
    except: 
        msg = "Need to login as restaurant"
        flash(msg)
        return render_template('restaurant/restdetail.html', rest_name=rest_name)

    cur = mysql.connection.cursor()
    query = "select name, email, phone_number, rating from restaurant where restaurant_ID=%s;"
    cur.execute(query,(rest_ID,))
    rest_details = cur.fetchone()
    rest = {
        'name': rest_details[0],
        'phone_number': rest_details[2],
        'email': rest_details[1],
        'rating': rest_details[3]
    }
    rest_name = rest['name']

    cur.execute("SELECT Orders.order_ID, Orders.order_placed_time, Orders.order_status, order_totals.net_price FROM Orders inner join restaurant on Orders.restaurant_ID = restaurant.restaurant_ID inner join ( SELECT Orders.order_ID, SUM(Menu_Item.unit_price * Order_Items.quantity) AS net_price FROM Orders JOIN Order_Items ON Orders.order_ID = Order_Items.order_ID JOIN Menu_Item ON Order_Items.item_ID = Menu_Item.item_ID GROUP BY Orders.order_ID ) order_totals on Orders.order_ID = order_totals.order_ID WHERE Orders.restaurant_ID = %s ORDER BY order_placed_time DESC LIMIT 10;", (rest_ID,))
    orders_rest = cur.fetchall()
    orders = []
    for order in orders_rest:
        temp = {
            'order_placed_time':order[1],
            'order_status': order[2],
            'net_price': order[3], 
        }
        items = []
        cur.execute("select name, unit_price, quantity from order_items left join menu_item on order_items.item_ID=menu_item.item_ID where order_items.order_ID=%s;", (order[0],))
        order_items = cur.fetchall()
        for order_item in order_items:
            it = {
                'name': order_item[0],
                'unit_price': order_item[1],
                'quantity': order_item[2],
            }
            items.append(it)
        temp['order_items'] = items
        orders.append(temp)
    return render_template('restaurant/restdetail.html', rest=rest, rest_name=rest_name, orders=orders)

 

@restaurant.route('/restmenu', methods=['GET', 'POST'])
def restmenu():
    # adding add new menu bottom
    if (session['restbool']):
        rest_ID = session.get("restaurant_ID")
        cursor = mysql.connection.cursor()
        cursor.execute("select name from restaurant where restaurant_ID = %s;", [rest_ID])
        rest = cursor.fetchone()
        rest_name = rest[0]
        cursor.execute("select name, unit_price, veg, item_type, item_ID, availability from menu_item where restaurant_ID = %s;", [rest_ID])
        menu_items = cursor.fetchall()
        items = []
        for item in menu_items:
            temp = {
                'name': item[0],
                'unit_price': item[1],
                'veg_nonveg': int(item[2]),
                'type': item[3],
                'ID': item[4],
                'availability': "YES" if (int(item[5])) else "NO"
            }
            items.append(temp)
        return render_template('restaurant/menu.html', rest_name=rest_name, items=items, rest_ID=rest_ID)
    return render_template('restaurant/menu.html')


@restaurant.route('/menuedit', methods=['GET', 'POST'])
def menuedit():
    if request.method == 'GET':
        if (request.values.get("newitem_ID")):
            rest_ID = request.values.get("newitem_ID")
            cur = mysql.connection.cursor()
            cur.execute("select max(item_ID) from menu_item")
            item_ID = cur.fetchone()[0]
            item = {
                'ID': str(int(item_ID) + 1),
                'veg': 0,
                'availability': 0,
                'name': "name",
                "unit_price": "0.00",
                "item_type": "type"
            }
            cur.execute("insert into menu_item(item_ID, name, unit_price, availability, veg, item_type, restaurant_ID) values(%s,%s,%s,%s,%s,%s,%s);", (item['ID'], item['name'], item['unit_price'], item['availability'], item['veg'], item['item_type'], rest_ID,))
            mysql.connection.commit()
            cur.close()
            return render_template('restaurant/editmenu.html', item=item)
        
        item_ID = request.values.get("item_ID")
        cur = mysql.connection.cursor()
        cur.execute("select item_ID, veg, availability, name, unit_price, item_type from menu_item where item_ID = %s;", [item_ID])
        item_detail = cur.fetchone()
        item = {
            'ID': item_detail[0],
            'veg': item_detail[1],
            'availability': item_detail[2],
            'name': item_detail[3],
            'unit_price': item_detail[4],
            'item_type': item_detail[5]
        }
        return render_template('restaurant/editmenu.html', item = item) 
    if request.method == 'POST':
        item_ID = request.values.get("item_ID")
        veg_novveg = request.values.get("veg")
        availability = request.values.get("availability")
        item_name = request.values.get("name")
        unit_price = request.values.get("unit_price")
        item_type = request.values.get("item_type")
        cur = mysql.connection.cursor()
        cur.execute("UPDATE menu_item SET veg = %s, availability=%s, name=%s, unit_price =%s, item_type=%s where item_ID = %s;", (veg_novveg, availability, item_name, unit_price, item_type, item_ID,))
        mysql.connection.commit()
        cur.close()
        msg = "Edited menu successfully!!"
        flash(msg)
        return redirect(url_for('restaurant.restmenu'))
    redirect(url_for('restaurant.restmenu'))

