import re
import requests
import json
import shopify
import datetime
import time
import schedule
import mysql.connector


shop_url = "https://35c4ff16772c0e3f818985daeef94713:1ad54f04c04dbec2f46f3e97c96199da@jerseypickz.myshopify.com/admin"
SHARED_SECRET = '9a9f4429eb151549ddfc756d0458de43'
API_KEY = '35c4ff16772c0e3f818985daeef94713'
PASSWORD = '1ad54f04c04dbec2f46f3e97c96199da'
API_VERSION = '2020-01'
shopify.ShopifyResource.set_user(API_KEY)
shopify.ShopifyResource.set_password(PASSWORD)
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current()
active1dayers = []
active3dayers = []
active7dayers = []
active30dayers = []
active180dayers=[]
active365dayers = []
activelifetimers = []
masterList =[]
userCount = 0

def getNewOrders():
    # get orders by params - Params not working properly - created_at_min works, others don't.
    newOrders = shopify.Order.find(
        status="open", fulfillment_status="null", created_at_min="2019-10-25 00:00")
    return newOrders

def checkAllActives():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Select * from activeusers"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    return mycursor.rowcount

def insertExpiredCustomer(firstName,lastName,customerID,package):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Insert Ignore into expiredusers (customerID, package) Values (%s, %s)"
    val = (customerID,package)
    mycursor.execute(sql,val)
    mydb.commit()

def insertLifeCustomer(firstName, lastName, customerID, package):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Insert ignore into activeusers (firstName, lastName, customerID, package) Values (%s, %s, %s, %s)"
    val = (firstName,lastName,customerID,package)
    mycursor.execute(sql,val)
    mydb.commit()

def insertNewCustomer(firstName, lastName, customerID, package):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Insert ignore into activeusers (firstName, lastName, customerID, package) Values (%s, %s, %s, %s)"
    val = (firstName,lastName,customerID,package)
    print(val)
    mycursor.execute(sql,val)
    mydb.commit()

def insertNewSeasonPass(firstName, lastName, customerID, package):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Insert ignore into seasonpasses (firstName, lastName, customerID, package) Values (%s, %s, %s, %s)"
    val = (firstName,lastName,customerID,package)
    mycursor.execute(sql,val)
    mydb.commit

def updateLifetimeCustomer(firstName, lastName, customerID, package):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Update activeusers set package=lifetime where customerID = %s"
    val = customerID
    mycursor.execute(sql,val)
    mydb.commit()

def removeCustomer(customerID):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()
    sql = "Delete from activeusers where customedID='%s'"
    val = (customerID)
    mycursor.execute(sql,val)
    mydb.commit()

def checkUserActive(customer):
    global active1dayers
    global active3dayers
    global active7dayers
    global active30dayers
    global active365dayers
    global activelifetimers

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="activeusersshopify"
    )

    mycursor = mydb.cursor()

    sql = "Select (customerID) From activeusers"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    mydb.commit()
    for x in myresult:
        if(customer==x):
            print("customer account found\n")
            return 1
    return 2

def getOrderDetails(ord):
    # get basic order details - (ord = your order id)
    order = shopify.Order.find(ord)
    em = order.email
    id = order.id
    nam = order.name
    ful = order.fulfillment_status
    cur = order.currency
    cr = order.created_at
    n = order.note
    tags = order.tags
    # title = order.title

    usefulData = [ful, cr, tags, order.customer]
    print(usefulData)

def checkExpired(package, created_at, tags):

    day1 = datetime.timedelta(days=1)
    day3 = datetime.timedelta(days=3)
    day7 = datetime.timedelta(days=7)
    day30 = datetime.timedelta(days=30)
    day180 = datetime.timedelta(days=180)

    year = datetime.timedelta(days=365)
    lifetime = year*10
    now = datetime.datetime.now()
    # timedelta(days=1)
    expirationDate = created_at
    created_at = datetime.datetime.strptime(expirationDate[:19], '%Y-%m-%dT%H:%M:%S')
    #print('Created At:', created_at)

    # expirationDate.join(exp[0],exp[1])
    # exp = expirationDate.index(0,9)+expirationDate.index(10,18)
    # print(exp)
    status = ''
    print(package)
    if(package == '1day'):
        day1 = datetime.timedelta(days=1)
        if(now > created_at+day1):
            #print('EXPIRED: ', created_at+day1)
            status = 'expired'
        elif(now < created_at+day1):
            status = 'active'
    elif(package == '3day'):
        day3 = datetime.timedelta(days=3)
        if(now > created_at+day3):
            #print('EXPIRED: ', created_at+day3)
            status = 'expired'
        elif(now < created_at+day3):
            status = 'active'
    elif(package == '7day'):
        day7 = datetime.timedelta(days=7)
        if(now > created_at+day7):
            status = 'expired'
        elif(now < created_at+day7):
            status = 'active'
    elif(package == '30day'):
        day30 = datetime.timedelta(days=30)
        if(now > created_at+day30):
            status = 'expired'
        elif(now < created_at+day30):
            status = 'active'
    elif(package == '180day'):
        day180 = datetime.timedelta(days=180)
        if(now > created_at+day180):
            status = 'expired'
        elif(now < created_at+day180):
            status = 'active'
    elif(package == '365day'):
        year = datetime.timedelta(days=365)
        if(now > created_at+year):
            status = 'expired'
        elif(now < created_at+year):
            status = 'active'
    elif(package == 'Weekend Promo'):
        status = 'active'
    else:
        print("ELSE PACKAGE: ", package)
        status = 'unknown'
    if(tags==''):
        return (status,2)
    else:
        return (status,1)

def tagCustomer(firstName, lastName, orderTitle, customer, tags, created_at):
    global active1dayers
    global active3dayers
    global active7dayers
    global active30dayers
    global active365dayers
    global activelifetimers
    package = orderTitle.split('-', 1)[0]
    if(package != 'lifetime' and package != 'NFLpass' and package != 'NBApass' and package != 'Weekend Promo'):
        package = package+"day"

    status = checkExpired(package, created_at, tags)
    if(status[0] == 'active'):
        tagActiveCustomer(customer, package)
        insertNewCustomer(firstName, lastName, customer, package)
    if(status[0] == 'expired'):
        insertExpiredCustomer(firstName,lastName,customer,tags)
        if(tags != ''):
            print("Package expired")
            print("Removing tags...")
            shopper = shopify.Customer.find(customer)
            shopper.tags = ''
            shopper.save()
    if(tags == 'lifetime'):
        updateLifetimeCustomer(firstName,lastName,customer,'lifetime')
    return

def extractActiveShoppers():
    global active1dayers
    global active3dayers
    global active7dayers
    global active30dayers
    global active180dayers
    global active365dayers
    global activelifetimers
    f = open("ActiveCustomers.txt", "r")
    currentDayers=-1
    while True:
        line = f.readline().strip()
        if line == '':
            break
        activeshopper = line.split(" ")
        if(len(activeshopper)==1):
            if(activeshopper[0] == 'active1dayers'):
                currentDayers=1
            if(activeshopper[0] == 'active3dayers'):
                currentDayers=3
            if(activeshopper[0] == 'active7dayers'):
                currentDayers=7
            if(activeshopper[0] == 'active30dayers'):
                currentDayers=30
            if(activeshopper[0] == 'active180dayers'):
                currentDayers=180
            if(activeshopper[0] == 'active365dayers'):
                currentDayers=365
            if(activeshopper[0] == 'activelifetimers'):
                currentDayers = 0

        if(currentDayers == 1 and len(activeshopper)>2):
            active1dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 3 and len(activeshopper)>2):
            active3dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 7 and len(activeshopper)>2):
            active7dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 30 and len(activeshopper)>2):
            active30dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 180 and len(activeshopper)>2):
            active180dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 365 and len(activeshopper)>2):
            active365dayers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])
        if(currentDayers == 0 and len(activeshopper)>2):
            activelifetimers.append([activeshopper[0],activeshopper[1],activeshopper[2],activeshopper[3]])

def taggerBot():
    global userCount
    r = requests.get(
        'https://35c4ff16772c0e3f818985daeef94713:1ad54f04c04dbec2f46f3e97c96199da@jerseypickz.myshopify.com/admin/api/2019-10/customers.json?limit=250')
    customersJ = json.loads((r.text))['customers']
    r = requests.get(
        'https://35c4ff16772c0e3f818985daeef94713:1ad54f04c04dbec2f46f3e97c96199da@jerseypickz.myshopify.com/admin/orders.json?limit=250')
    ordersJ = json.loads((r.text))['orders']

    # Todo fetch customer list, for each customer, check tags+last order id, use ID to find name of package, maybe last update time to check timeleft
    # octoberOrders = getNewOrders()
    # for order in octoberOrders:
    # (di, nam, ful, cr, em)
    # orderData = getOrderDetails(order.id)
    # tagCustomer(orderData)

    orderList = []
    for order in ordersJ:
        # print(order)
        id = order["id"]
        created_at = order["created_at"]
        order = order["line_items"]
        title = order[0]["title"]
        # variantID = order[0]["id"]
        orderList.append([created_at, title, id])

    customerList = []
    for user in customersJ:
        firstName = user["first_name"]
        lastName = user["last_name"]
        id = user["id"]
        last_order_id = user["last_order_id"]
        tags = user["tags"]
        # order = shopify.Order.find(last_order_id)
        # if user["tags"] == '':
        # print("MISSING TAGS")
        # print(user["last_order_name"])
        customerList.append([firstName, lastName, id, last_order_id, tags])

    count = 0
    for user in customerList:
        firstname = user[0]
        lastname = user[1]
        id = user[2]
        orderID = user[3]
        tags = user[4]
        for order in orderList:
            created_at = order[0]
            title = order[1]
            variantID = order[2]
            if(variantID == orderID):
                if("LOTY" in title or "LOCK" in title or "UNIT" in title):
                    #print("1 Time Deal\n")
                    onetime=1
                else:
                    userCount = userCount+1
                    tagCustomer(firstname, lastname, title, id, tags, created_at)
    print("Total ActiveUsers count: " + str(checkAllActives()))
    writeActiveAccounts()

def tagActiveCustomer(customer, package):
    shopper = shopify.Customer.find(customer)
    shopper.tags = package
    print('New Active ', package)
    shopper.save()

def printActiveAccounts():
    global active1dayers
    global active3dayers
    global active7dayers
    global active30dayers
    global active365dayers
    global activelifetimers
    print("Active 1 dayers", active1dayers)
    print("Active 3 Dayers", active3dayers)
    print("Active 7 Dayers", active7dayers)
    print("Active 30 Dayers", active30dayers)
    print("Active 365 Dayers", active365dayers)
    print("Active Lifetimers", activelifetimers)

def writeActiveAccounts():
    global active1dayers
    global active3dayers
    global active7dayers
    global active30dayers
    global active365dayers
    global activelifetimers
    f = open("ActiveCustomers.txt", "w")
    f.write("active1dayers\n")
    for i in active1dayers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.write("active3dayers\n")
    for i in active3dayers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.write("active7dayers\n")
    for i in active7dayers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.write("active30dayers\n")
    for i in active30dayers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.write("active365dayers\n")
    for i in active365dayers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.write("activelifetimers\n")
    for i in activelifetimers:
        for j in i:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    f.close()


if __name__ == "__main__":
    updateCustomers = 0
    if(updateCustomers == 0):
        extractActiveShoppers()
        #writeActiveAccounts()
        taggerBot()
        schedule.every(2).minutes.do(taggerBot)
        schedule.every(2).minutes.do(writeActiveAccounts)
        #mysqlInit()
        while True:
            schedule.run_pending()
            time.sleep(1) # wait one minute
    else:
        r = requests.get(
            'https://197616a1076bfb32f99ef7bd22737b7d:9270856490ffa420421f10dd1cd3935d@royal-sports-profits.myshopify.com/admin/api/2019-10/customers.json?limit=250')
        customersJ = json.loads((r.text))['customers']
        r = requests.get(
            'https://197616a1076bfb32f99ef7bd22737b7d:9270856490ffa420421f10dd1cd3935d@royal-sports-profits.myshopify.com/admin/orders.json?limit=250')
        ordersJ = json.loads((r.text))['orders']

        # Todo fetch customer list, for each customer, check tags+last order id, use ID to find name of package, maybe last update time to check timeleft
        # octoberOrders = getNewOrders()
        # for order in octoberOrders:
        # (di, nam, ful, cr, em)
        # orderData = getOrderDetails(order.id)
        # tagCustomer(orderData)

        orderList = []
        for order in ordersJ:
            # print(order)
            id = order["id"]
            created_at = order["created_at"]
            order = order["line_items"]
            title = order[0]["title"]
            # variantID = order[0]["id"]
            orderList.append([created_at, title, id])
            print(title)

        customerList = []
        for user in customersJ:
            firstName = user["first_name"]
            lastName = user["last_name"]
            id = user["id"]
            last_order_id = user["last_order_id"]
            tags = user["tags"]
            # order = shopify.Order.find(last_order_id)
            # if user["tags"] == '':
            # print("MISSING TAGS")
            # print(user["last_order_name"])
            customerList.append([firstName, lastName, id, last_order_id, tags])

        count = 0
        for user in customerList:
            firstname = user[0]
            lastname = user[1]
            id = user[2]
            orderID = user[3]
            tags = user[4]
            for order in orderList:
                created_at = order[0]
                title = order[1]
                variantID = order[2]
                if(variantID == orderID):
                    if("LOTY" in title or "LOCK" in title or "UNIT" in title):
                        print("1 Time Deal\n")
                    else:
                        count = count+1
                        tagCustomer(title, id, tags, created_at)
                        #tagCustomer(title, id, tags, created_at)
                    # tagCustomer(customer,title,tags)
        print("Total ActiveUsers count: " + count)

        writeActiveAccounts()
