from settings import db
from flask.ext.sqlalchemy import SQLAlchemy

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    fname = db.Column(db.String(50), default="")
    lname = db.Column(db.String(50), default="")
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)
    rating = db.Column(db.Integer, default=1)
    isAdmin = db.Column(db.Boolean, default=False)

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    img_pathfile = db.Column(db.String())

class Location(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), unique=True)
    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"), primary_key=True)
    phoneNumber = db.Column(db.String())
    managerName = db.Column(db.String(), server_default="Joe Fresh")
    address = db.Column(db.String(), nullable=False, primary_key=True)
    openTime = db.Column(db.Time)
    closeTime = db.Column(db.Time)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"))
    userId = db.Column(db.Integer, db.ForeignKey("user.id"))
    price = db.Column(db.Integer, nullable=False)
    food = db.Column(db.Integer, db.CheckConstraint('food<6'), db.CheckConstraint('food>0'), nullable=False)
    mood = db.Column(db.Integer, db.CheckConstraint('mood<6'), db.CheckConstraint('mood>0'), nullable=False)
    staff = db.Column(db.Integer, db.CheckConstraint('staff<6'), db.CheckConstraint('staff>0'), nullable=False)
    comment = db.Column(db.Text())
    date = db.Column(db.Date)

class MenuItem(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), unique=True)
    name = db.Column(db.String(50), nullable=False, primary_key=True)
    category = db.Column(db.String(50))
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text())
    type = db.Column(db.String(20))
    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"), primary_key=True)

class MenuItemRating(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), unique=True)
    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"), primary_key=True)
    menuitemId = db.Column(db.Integer, db.ForeignKey("menu_item.id"), primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    rating = db.Column(db.Integer, db.CheckConstraint('rating<6'), db.CheckConstraint('rating>0'))
    date = db.Column(db.Date)

class CuisineType(db.Model):
    id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1), unique=True)
    name = db.Column(db.String(50), nullable=False, primary_key=True)
    restaurantId = db.Column(db.Integer, db.ForeignKey("restaurant.id"), primary_key=True)
