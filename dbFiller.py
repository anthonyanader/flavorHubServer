import urllib2
import urllib
import requests
from requests.exceptions import HTTPError
import json
import random
import datetime
from models import User, Restaurant, Location, Rating, MenuItem, CuisineType, MenuItemRating
from sqlalchemy import distinct
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

IMAGE_DIR = 'static/images'

def populateUserTable(db):
    fnames = ['Joe', 'Filip', 'Anthony', 'Peter', 'Rami', 'Zuhan', 'James', 'Julia', 'Julien', 'Costa', 'Zarif', 'Pasoon', 'Killy', 'Gabriel', 'Bond', 'Praiyon', 'Konst', 'Ladan']
    lnames = ['Jones', 'Abraham', 'Nader', 'Micheal', 'Jamerson', 'Kendo', 'Lokost', 'Slatinac', 'Taleb']

    for i in range(100):
        fname = fnames[random.randint(0, len(fnames)-1)]
        lname = lnames[random.randint(0, len(lnames)-1)]
        username = fname[0]+lname[0]+str(random.randint(0, 100))
        email = username+'@hotmail.com'

        Hashedpassword = generate_password_hash('12345', method='sha256')
        new_user = User.query.filter_by(username=username).first()

        if not new_user:
            user = User(username=username, email=email, password=Hashedpassword, fname=fname, lname=lname, public_id=str(uuid.uuid4()))
            db.session.add(user)
            db.session.commit()

def populateRestaurantTable(db):
    fnames = ['Joe', 'Filip', 'Anthony', 'Peter', 'Rami', 'Zuhan', 'James', 'Julia', 'Julien']
    lnames = ['Jones', 'Abraham', 'Nader', 'Micheal', 'Jamerson', 'Kendo', 'Lokost', 'Slatinac', 'Taleb']

    start = 20
    while start < 2700:
        url = "https://developers.zomato.com/api/v2.1/search?q=Ottawa?start="+str(start)+"&lat=40.748&lon=-73.985"
        start+=20
        page = ""
        jsonResponse = {}
        try:
            request = urllib2.Request(url, headers={"user-key" : "21524a1242003830e7d41d90a2918c3e"})
            jsonResponse = json.load(urllib2.urlopen(request))
        except HTTPError:
            print "Error"

        restaurants = jsonResponse['restaurants']

        for restaurantObject in restaurants:
            restaurant = restaurantObject['restaurant']
            name = restaurant['name']

            restaurantObject = Restaurant.query.filter_by(name=name).first()

            if not restaurantObject:

                imageLink = ""
                imageName = "noPicture.svg"
                imgPath = '{}/{}'.format(IMAGE_DIR, imageName)

                if restaurant['featured_image'] != "":
                    imgPath = '{}/{}'.format(IMAGE_DIR, str(restaurant['id'])+".jpg")

                    imageLink = restaurant["featured_image"]
                    urllib.urlretrieve(imageLink, imgPath)

                new_restaurant = Restaurant(name=name, img_pathfile=imgPath)
                restaurantObject = new_restaurant
                db.session.add(restaurantObject)
                db.session.commit()

                db.session.refresh(restaurantObject)

            locationObject = Location.query.filter_by(restaurantId=restaurantObject.id, address=restaurant['location']['address']).first()

            if not locationObject:

                address = restaurant['location']['address']
                managerName = fnames[random.randint(0, len(fnames)-1)] +" "+ lnames[random.randint(0, len(lnames)-1)]
                phoneNumber = "819" + " " + str(random.randint(111, 999)) + " " + str(random.randint(1111,9999))
                openTime = "09:00:00"
                closeTime = "24:00:00"

                new_location = Location(restaurantId=restaurantObject.id, address=address, phoneNumber=phoneNumber, managerName=managerName, openTime=openTime, closeTime=closeTime)
                db.session.add(new_location)
                db.session.commit()

            cuisines = restaurant['cuisines'].strip().split(',')

            for cuisine in cuisines:
                cuisineObject = CuisineType.query.filter_by(restaurantId=restaurantObject.id, name=cuisine).first()
                if not cuisineObject:
                    new_cuisine = CuisineType(restaurantId=restaurantObject.id, name=cuisine)
                    db.session.add(new_cuisine)
                    db.session.commit()


def populateMenuTable(db):

    menus = [
            {'name':'chicken burger', 'description': 'chicken burger served with fries', 'category': 'main'},
            {'name':'beef burger', 'description': 'beef burger served with fries', 'category': 'main'},
            {'name':'mac and cheese', 'description': 'mac and cheese served with cheese bread', 'category': 'main'},
            {'name':'lobster', 'description': 'lobster served with rice or brocolie', 'category': 'main'},
            {'name':'crab', 'description': 'crab served with rice or brocolie', 'category': 'main'},
            {'name':'oysters', 'description': 'oyster served with rice or brocolie', 'category': 'main'},
            {'name':'lamb', 'description': 'lamb served with rice or brocolie', 'category': 'main'},
            {'name':'chicken shawarma', 'description': 'chicken shawarma served with patatos', 'category': 'main'},
            {'name':'beef shawarma', 'description': 'beef shawarma served with patatos', 'category': 'main'},
            {'name':'ravioli', 'description': 'ravioli served with bread', 'category': 'main'},
            {'name':'donuts', 'description': 'delicious donuts served with chocolate milk', 'category': 'desert'},
            {'name':'cream cookies', 'description': 'delicious cookies served with chocolate milk', 'category': 'desert'},
            {'name':'roast beef sandwich', 'description': 'delicious roast beef sandwich with fries or rice', 'category': 'desert'},
            {'name':'club sandwich', 'description': 'club sandwich served fries', 'category': 'main'},
            {'name':'chicken sandwich', 'description': 'chicken sandwich served fries', 'category': 'main'},
            {'name':'chicken panini', 'description': 'chicken panini served fries', 'category': 'main'},
            {'name': 'beef panini', 'description': 'beef panini served fries', 'category': 'main'},
            {'name': 'mushroom soup', 'description': 'mushroom soup served with bread and crackers', 'category': 'starter'},
            {'name':'chicken soup', 'description': 'chicken soup served with bread and crackers', 'category': 'starter'},
            {'name':'lamb soup', 'description': 'lamb soup served with bread and crackers', 'category': 'starter'},
            {'name':'tomato soup', 'description': 'tomato soup served with bread and crackers', 'category': 'starter'},
            {'name':'ceasar soup', 'description': 'delicious salad served with a glass of flavoured water', 'category': 'starter'},
            {'name':'garden salad', 'description': 'delicious salad served with a glass of flavoured water', 'category': 'starter'},
            {'name':'chicken nuggets', 'description': 'chicken nuggets served with fries', 'category': 'main'},
            {'name':'chicken tenders', 'description': 'chicken tenders served with fries', 'category': 'main'},
            {'name':'grilled cheese', 'description': 'grilled cheese served with fries', 'category': 'main'},
            {'name':'peperoni pizza', 'description': 'delicious pizza served with your choice of pop', 'category': 'main'},
            {'name':'greek pizza', 'description': 'delicious pizza served with your choice of pop', 'category': 'main'},
            {'name':'vegeterian pizza', 'description': 'delicious pizza served with your choice of pop', 'category': 'main'},
            {'name':'cheese pizza', 'description': 'delicious pizza served with your choice of pop', 'category': 'main'},
            {'name':'bmt bagel', 'description': 'delicious bagel served with chips', 'category': 'main'},
            {'name':'cream cheese bagel', 'description': 'delicious bagel served with chips', 'category': 'main'},
            {'name':'steak', 'description': 'good cut steak served with mashed patatos', 'category': 'main'},
            {'name':'tuna', 'description': 'best tuna in town', 'category': 'main'},
            {'name':'filet mignon', 'description': 'best filet mignon served with a glass of wine or water', 'category': 'main'},
            {'name':'milkshake', 'description': 'banana, chocolate, vanila or cookies and cream', 'category': 'desert'},
            {'name':'rice and chicken', 'description': 'very basic meal for the ones in a hurry', 'category': 'main'},
            {'name':'chicken noodles', 'description': 'chicken noodles served in a large bowl', 'category': 'main'},
            {'name':'beef noodles', 'description': 'beef noodles served in a large bowl', 'category': 'main'}
            ]

    cuisines = CuisineType.query.distinct(CuisineType.name).all()
    for i in range(len(menus)):
        index = random.randint(0, len(cuisines)-1)
        menus[i]['type'] = cuisines[index].name
        menus[i]['price'] = random.randint(5, 30)

    restaurants = Restaurant.query.all()

    for restaurant in restaurants:
        print(restaurant.id)
        restaurantId = restaurant.id

        randomAmount = random.randint(3,len(menus))
        randomItems = []

        for i in range(randomAmount):
            index = random.randint(0, len(menus)-1)
            randomItems.append(menus[index])

        for item in randomItems:
            menuItem = MenuItem.query.filter_by(restaurantId=restaurantId, name=item['name']).first()
            if not menuItem:
                menuItemObject = MenuItem(name=item['name'], price=item['price'], restaurantId=restaurantId, description=item['description'], type=item['type'], category=item['category'])
                db.session.add(menuItemObject)
                db.session.commit()


def populateRatingTable(db):
    restaurants = Restaurant.query.all()
    users = User.query.all()
    comments = [
        'This restaurant was absolutely great, the food, staff, mood and price were fantastic',
        'The restaurant had great food and mood, but not so much of a staff and the prices were a bit too high',
        'This restaurant had great food but the mood and staff were not as good as we thought it would be, it does not help that the prices were quite high',
        'This restaurant was okay, the food was decent',
        'This restaurant was not good at all'
    ]

    prices = [
        5,
        4,
        3,
        2,
        1
    ]

    moods = [
        5,
        5,
        3,
        2,
        1
    ]

    staffs = [
        5,
        4,
        3,
        2,
        1
    ]

    foods = [
        5,
        5,
        4,
        3,
        1
    ]

    for restaurant in restaurants:
        restaurantId = restaurant.id
        user = users[random.randint(0, len(users)-1)]
        userId = user.id

        commentLevel = random.randint(0, 4)
        comment = comments[commentLevel]
        price = prices[commentLevel]
        mood = moods[commentLevel]
        staff = staffs[commentLevel]
        food = foods[commentLevel]
        date = str(datetime.date.today())[:10]

        RatingObject = Rating(comment=comment, price=price, restaurantId=restaurantId, userId=userId, mood=mood, staff=staff, food=food, date=date)
        db.session.add(RatingObject)
        db.session.commit()
