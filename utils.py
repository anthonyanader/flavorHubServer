from models import Restaurant, User
import random
import string

def validateUserData(userData):
    #namePattern = re.compile('\w*')
    #usernamePattern = re.compile('\w[\w-_]{2,10}')
    #passwordPattern = re.compile('[\w]{8,}')write password regex
    #email = re.compile() write email regex

    if not userData:
        return {'valid': False, 'message': 'registration information missing'}

    if not userData['password']:
        return {'valid': False, 'message': 'password is missing'}

    if not userData['username']:
        return {'valid': False, 'message': 'username is missing'}

    if not userData['email']:
        return {'valid': False, 'message': 'email is missing'}

    return {'valid': True, 'message': 'registration information valid'}

def checkUserExistance(email, username):
    userEmailCheck = User.query.filter_by(email=email).first()
    userUsernameCheck = User.query.filter_by(username=username).first()

    if userEmailCheck or userUsernameCheck:
        return {'valid': False, 'message': 'User already exists'}

    return {'valid': True, 'message': 'registration information non-conflicting'}


def validateRestaurantCreation(restaurantData):
    if not restaurantData:
        return {'valid': False, 'message': 'restaurant information missing'}

    if not 'name' in restaurantData:
        return {'valid': False, 'message': 'restaurant name information missing'}

    return {'valid': True, 'message': 'restaurant information valid'}

def validateMenuItemCreation(menuItemData):
#    name = db.Column(db.String(50), nullable=False)
#    category = db.Column(db.String(50))
#    price = db.Column(db.Integer, nullable=False)
#    description = db.Column(db.Text())
#    type = db.Column(db.String(20))
#    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"))

    if not menuItemData:
        return {'valid': False, 'message': 'menu item information missing'}

    if not menuItemData['name']:
        return {'valid': False, 'message': 'name is missing'}

    if not menuItemData['price']:
        return {'valid': False, 'message': 'price is missing'}

    if not menuItemData['restaurantName']:
        return {'valid': False, 'message': 'restaurantName is missing'}
    else:
        restaurant_referenced = Restaurant.query.filter_by(name=menuItemData['restaurantName']).first()

        if not restaurant_referenced:
            return {'valid': False, 'message': 'restaurantName is invalid'}

    return {'valid': True, 'message': 'menu item information valid'}

def randomStringGeneratorForImages():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) \
                for _ in range(30))
