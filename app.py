from flask import Flask, request, jsonify, make_response
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, text, asc
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
from functools import wraps
import re
import uuid
from settings import app, db
from models import User, Restaurant, Location, Rating, MenuItem, CuisineType, MenuItemRating
from utils import validateUserData, checkUserExistance, validateRestaurantCreation, randomStringGeneratorForImages, validateMenuItemCreation
from sqlQueries import queries
from dbFiller import populateRestaurantTable, populateMenuTable, populateRatingTable, populateUserTable

IMAGE_DIR = 'static/images'

def token_required(requiredToken=True):
    def token_required_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers and request.headers['x-access-token'] != 'null':
                token = request.headers['x-access-token']

            else:
                if requiredToken:
                    return jsonify({'message' : 'Invalid Token'}), 401
                else:
                    return f(loggedInUser=None, *args, **kwargs)

            try:
                userData = jwt.decode(token, app.config['SECRET_KEY'])
                loggedInUser = User.query.filter_by(public_id=userData['public_id']).first()

            except:
                if requiredToken:
                    return jsonify({'message' : 'Invalid Token'}), 401
                else:
                    return f(loggedInUser=None, *args, **kwargs)

            return f(loggedInUser, *args, **kwargs)

        return decorated

    return token_required_decorator

@app.route('/check_token', methods=['GET'])
@token_required()
def check_token(loggedInUser):

    if loggedInUser:
        userData = {
        'fname': loggedInUser.fname,
        'lname': loggedInUser.lname,
        'isAdmin': loggedInUser.isAdmin,
        'username': loggedInUser.username
        }

        return jsonify(userData)

    return make_response('Cannot verify user', 401, {'WWW-Ahtenticate' : 'Basic realm="Login Required !"'})

@app.route('/register', methods=['POST'])
def register():
    dataReceived = request.get_json()

    validRegistration = validateUserData(dataReceived)

    if validRegistration['valid']:
        userExistance = checkUserExistance(dataReceived['email'], dataReceived['username'])

        if userExistance['valid']:
            Hashedpassword = generate_password_hash(dataReceived['password'], method='sha256')
            new_user = User(username=dataReceived['username'], email=dataReceived['email'], password=Hashedpassword, fname=dataReceived['fname'], lname=dataReceived['lname'], public_id=str(uuid.uuid4()))

            db.session.add(new_user)
            db.session.commit()

            return make_response('User Created', 200, {'WWW-Ahtenticate' : 'Basic realm="'+userExistance['message']+' and '+validRegistration['message']+'!"'})

        else:
            return make_response('User Already Exists', 400, {'WWW-Ahtenticate' : 'Basic realm="'+userExistance['message']+'!"'})

    else:
        return make_response('Registration Information Invalid', 400, {'WWW-Ahtenticate' : 'Basic realm="'+validRegistration['message']+'!"'})


@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()

    if not auth or not auth['username'] or not auth['password']:
        return make_response('Cannot verify user', 401, {'WWW-Ahtenticate' : 'Basic realm="Login Required !"'})

    user = User.query.filter_by(username=auth['username']).first()

    if not user:
        return make_response('Cannot verify user', 401, {'WWW-Ahtenticate' : 'Basic realm="Login Required !"'})

    if check_password_hash(user.password, auth['password']):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])

        return jsonify(token.decode('UTF-8'))

    else:
        return make_response('Cannot verify user', 401, {'WWW-Ahtenticate' : 'Basic realm="Login Required !"'})


@app.route('/basic_info', methods=['GET'])
@token_required()
def get_basic_info(loggedInUser):

    if loggedInUser:
        userData = {
        'fname': loggedInUser.fname,
        'lname': loggedInUser.lname,
        'isAdmin': loggedInUser.isAdmin,
        'username': loggedInUser.username
        }

        return jsonify(userData)

    return make_response('Cannot verify user', 401, {'WWW-Ahtenticate' : 'Basic realm="Login Required !"'})

@app.route('/user_info', methods=['GET'])
@token_required(False)
def get_user_info(loggedInUser):
    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    userData = {
    'fname': user.fname,
    'lname': user.lname,
    'rating': user.rating,
    'username': user.username
    }

    return jsonify(userData)


@app.route('/restaurants', methods=['GET'])
@token_required(False)
def get_all_restaurants(loggedInUser):

    if loggedInUser:
        print(Restaurant.query.all())
        return('y')

    else:
        restaurantNoSignIn = Restaurant.query.limit(9).all()
        restaurants = []
        for restaurant in restaurantNoSignIn:
            locations = Location.query.filter_by(restaurantId=restaurant.id).all()
            cuisineObjects = CuisineType.query.filter_by(restaurantId=restaurant.id).all()
            cuisines = []
            for cuisine in cuisineObjects:
                cuisines.append(cuisine.name)
            restaurants.append({
            'locationCount': len(locations),
            'cuisines': cuisines,
            'imagePath': restaurant.img_pathfile,
            'name': restaurant.name
            #add rating average method, make sure its a raw query
            })
        return jsonify(restaurants)

@app.route('/restaurant_on_scroll', methods=["GET"])
@token_required(False)
def restaurant_on_scroll(loggedInUser):
    pageSize = 9
    page = int(request.args.get('page'))
    print(page*pageSize, db.session.query(Restaurant).count())
    hasMore = page*pageSize < db.session.query(Restaurant).count()
    restaurantNoSignIn = Restaurant.query.order_by(asc(Restaurant.name)).offset(page*pageSize).limit(pageSize).all()
    restaurants = []
    for restaurant in restaurantNoSignIn:
        locations = Location.query.filter_by(restaurantId=restaurant.id).all()
        cuisineObjects = CuisineType.query.filter_by(restaurantId=restaurant.id).all()
        averagePrices = db.session.query(MenuItem.category, func.round(func.avg(MenuItem.price),2)).group_by(MenuItem.category).filter_by(restaurantId=restaurant.id).all()
        averageObject = {}
        for i in range(len(averagePrices)):
            averageObject[averagePrices[i].category] = str(averagePrices[i][1])
        cuisines = []
        for cuisine in cuisineObjects:
            cuisines.append(cuisine.name.lower().strip())
        restaurants.append({
        'locationCount': len(locations),
        'cuisines': cuisines,
        'imagePath': restaurant.img_pathfile,
        'name': restaurant.name,
        'averagePrices': averageObject
        #add rating average method, make sure its a raw query
        })
    responseData = {
        'restaurants': restaurants,
        'hasMore': hasMore
    }
    return jsonify(responseData)

@app.route('/restaurant_information/<restaurantName>', methods=['GET'])
@token_required(False)
def restaurant_information(loggedInUser, restaurantName):

    if not restaurantName:
        return make_response('no restaurant provided', 404, {'WWW-Ahtenticate' : 'Basic realm="No restaurant provided !"'})

    else:
        restaurant = Restaurant.query.filter_by(name=restaurantName).first()

        if not restaurant:
            return make_response('no such restaurant', 404, {'WWW-Ahtenticate' : 'Basic realm="No such restaurant !"'})

        locationObjects = Location.query.filter_by(restaurantId=restaurant.id).all()
        cuisineObjects = CuisineType.query.filter_by(restaurantId=restaurant.id).all()
        menuItemObjects = MenuItem.query.filter_by(restaurantId=restaurant.id).all()
        ratingObjects = Rating.query.filter_by(restaurantId=restaurant.id).all()

        cuisines = []

        locations = []
        locationObject = {}

        menuItems = []
        menuItemObject = {}

        ratings = []
        ratingsObject = {}

        for cuisine in cuisineObjects:
            cuisines.append(cuisine.name)

        for location in locationObjects:
            locationObject['phoneNumber'] = location.phoneNumber
            locationObject['managerName'] = location.managerName
            locationObject['address'] = location.address
            # locationObject['openTime'] = location.openTime
            # locationObject['closeTime'] = location.closeTime

            locations.append(locationObject)
            locationObject = {}

        for menuItem in menuItemObjects:

            menuItemRatings = []

            menuItemObject['name'] = menuItem.name
            menuItemObject['category'] = menuItem.category
            menuItemObject['price'] = menuItem.price
            menuItemObject['description'] = menuItem.description
            menuItemObject['type'] = menuItem.type

            menuItemRatingObjects = MenuItemRating.query.filter_by(restaurantId=restaurant.id, menuitemId=menuItem.id).all()
            for menuItemRating in menuItemRatingObjects:
                menuItemRatingsObject = {}

                menuItemRatingsObject['username'] = User.query.filter_by(id=menuItemRating.userId).first().username
                menuItemRatingsObject['rating'] = menuItemRating.rating
                # menuItemRatingsObject['date'] = menuItemRating.date

                menuItemRatings.append(menuItemRatingsObject)

            menuItemObject['ratings'] = menuItemRatings

            menuItems.append(menuItemObject)
            menuItemObject = {}


        for rating in ratingsObject:
            ratingsObject['username'] = User.query.filter_by(id=rating.userId).first().username
            ratingsObject['price'] = rating.price
            ratingsObject['food'] = rating.food
            ratingsObject['mood'] = rating.mood
            ratingsObject['staff'] = rating.staff
            ratingsObject['comment'] = rating.comment
            # ratingsObject['date'] = rating.date

            ratings.append(ratingsObject)
            ratingsObject = {}

        responseObject = {
            'img_pathfile': restaurant.img_pathfile,
            'locations': locations,
            'cuisines': cuisines,
            'menuItems': menuItems,
            'ratings': ratings
        }

        return jsonify(responseObject)


@app.route('/add_restaurant', methods=['POST'])
@token_required()
def add_restaurant(loggedInUser):
    dataReceived = request.get_json()
    if loggedInUser and loggedInUser.isAdmin:
        imageName = "noPicture.svg"
        imgPath = '{}/{}'.format(IMAGE_DIR, imageName)
        if 'restaurantPicture' in request.files:
            imgfile = request.files['restaurantPicture']
            if imgfile.filename != '':
                imageName = secure_filename(imgfile.filename)+'.jpg'
                imgPath = '{}/{}'.format(IMAGE_DIR, imageName)
                imgfile.save(imgPath)

        new_restaurant = Restaurant(name=imgfile.filename, img_pathfile=imgPath)
        db.session.add(new_restaurant)
        db.session.commit()
        return make_response('Restaurant created', 200, {'WWW-Ahtenticate' : 'Basic realm="Restaurant created !"'})


    else:
        return make_response('Cannot create restaurant', 401, {'WWW-Ahtenticate' : 'Basic realm="No Permisson to create restaurants !"'})


@app.route('/restaurant/<restaurantName>', methods=['POST'])
@token_required()
def delete_restaurant(loggedInUser, restaurantName):
    if loggedInUser and loggedInUser.isAdmin:
        print(restaurantName)
        restaurant_to_be_deleted = Restaurant.query.filter_by(name=restaurantName).first()

        if restaurant_to_be_deleted:
            db.session.delete(restaurant_to_be_deleted)
            db.session.commit()

            return make_response(restaurantName +' deleted', 200, {'WWW-Ahtenticate' : 'Basic realm="Restaurant deleted!"'})


        else:
            return make_response('Restaurant '+ restaurantID +' cannot be deleted', 403, {'WWW-Ahtenticate' : 'Basic realm="Restaurant does not exist!"'})

    else:
        return make_response('Cannot delete restaurant', 401, {'WWW-Ahtenticate' : 'Basic realm="No Permisson to delete restaurants !"'})

@app.route('/restaurant_menu', methods=['GET'])
@token_required(False)
def restaurant_menu(loggedInUser):
    restaurantName = request.args.get('restaurantName')
    restaurant = Restaurant.query.filter_by(name=restaurantName).first()

    menu = MenuItem.query.filter_by(restaurantId=restaurant.id).all()

    menuItems = []

    for item in menu:
        menuItems.append({
            'name': item.name,
            'price': item.price,
            'type': item.type,
            'category': item.category,
            'description': item.description
        })

    return jsonify(menuItems)


@app.route('/menuitem', methods=['POST'])
@token_required()
def add_menu_item(loggedInUser):
    dataReceived = request.get_json()
    validMenuItemCheck = validateMenuItemCreation(dataReceived)

    if loggedInUser and loggedInUser.isAdmin:

        if  validMenuItemCheck['valid']:
            restaurant = Restaurant.query.filter_by(name=dataReceived['restaurantName']).first()
            new_menu_item = MenuItem.query.filter_by(name=dataReceived['name'], restaurantId=restaurant.id).first()
            print(new_menu_item)
            if not new_menu_item:
                item_to_be_added = MenuItem(name=dataReceived['name'], restaurantId=restaurant.id, description=dataReceived['description'], price=dataReceived['price'], category=dataReceived['category'], type=dataReceived['type'])
                db.session.add(item_to_be_added)
                db.session.commit()

                return make_response('Menu item created', 200, {'WWW-Ahtenticate' : 'Basic realm="Menu Item created!'})

            else:
                return make_response('Cannot create menu item', 401, {'WWW-Ahtenticate' : 'Basic realm="'+ validMenuItemCheck['message'] +'!"'})

        else:
            return make_response('Cannot create menu item', 401, {'WWW-Ahtenticate' : 'Basic realm="'+ validMenuItemCheck['message'] +'!"'})

    else:
        return make_response('Cannot create menu item', 401, {'WWW-Ahtenticate' : 'Basic realm="No Permisson to create menu items !"'})


@app.route('/menuitem/delete', methods=['POST'])
@token_required()
def delete_menu_item(loggedInUser):
    if loggedInUser and loggedInUser.isAdmin:
        dataReceived = request.get_json()
        print(dataReceived)
        restaurantId = Restaurant.query.filter_by(name=dataReceived['restaurantName']).first().id
        for item in dataReceived['itemsToBeDeleted']:

            menu_item_to_be_deleted = MenuItem.query.filter_by(name=item, restaurantId=restaurantId).first()

            if  menu_item_to_be_deleted:
                db.session.delete(menu_item_to_be_deleted)
                db.session.commit()

            else:
                return make_response('Menu Item cannot be deleted', 403, {'WWW-Ahtenticate' : 'Basic realm="Menu item does not exist!"'})

        return make_response('Menu items deleted', 200, {'WWW-Ahtenticate' : 'Basic realm="Menu Item deleted!'})


    else:
        return make_response('Cannot delete menu item', 401, {'WWW-Ahtenticate' : 'Basic realm="No Permisson to delete menu items !"'})

@app.route('/get_restaurant_reviews', methods=['GET'])
@token_required(False)
def restaurant_reviews(loggedInUser):
    restaurantName = request.args.get('restaurantName')
    restaurant = Restaurant.query.filter_by(name=restaurantName).first()

    reviews = Rating.query.filter_by(restaurantId=restaurant.id).all()
    reviewsObject = []

    for review in reviews:
        user = User.query.filter_by(id=review.userId).first()
        fname = user.fname
        lname = user.lname
        username = user.username

        reviewObject = {
        'fname': fname,
        'lname': lname,
        'username': username,
        'priceRating': review.price,
        'moodRating': review.mood,
        'staffRating': review.staff,
        'foodRating': review.food,
        'comment': review.comment,
        'data': str(review.date)
        }

        reviewsObject.append(reviewObject)

    return jsonify(reviewsObject)

@app.route('/raw_query_execute', methods=['GET'])
@token_required(False)
def execute_raw_query(loggedInUser):
    query = request.args.get('query')

    results = db.engine.execute(text(queries[query])).fetchall()
    columnNames = []
    rows = []

    if len(results) > 0:
        columnNames = results[0].keys()

    for result in results:
        row = []
        for col in columnNames:
            row.append(result[col])
        rows.append(row)

    returnObject = {
        'columnNames': columnNames,
        'rows': rows
    }

    return jsonify(returnObject)


@app.route('/user/delete', methods=['POST'])
@token_required()
def delete_user(loggedInUser):
    userInfo = request.get_json()

    if 'username' in userInfo:
        user = User.query.filter_by(username=userInfo['username']).first()
        if user:
            db.session.delete(user)
            db.session.commit()

            return make_response('user deleted', 200, {'WWW-Ahtenticate' : 'Basic realm="User deleted!'})

        else:
            return make_response('Cannot delete user', 401, {'WWW-Ahtenticate' : 'Basic realm="User does not exist"'})
    else:
        return make_response('Cannot delete user', 401, {'WWW-Ahtenticate' : 'Basic realm="No username sent !"'})



# @app.route('/create_restaurant_review', methods=['POST'])
# @token_required()
# def create_restaurant_review(loggedInUser):

if __name__ =="__main__":
	app.run(debug=True)
