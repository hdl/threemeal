# -*- coding:utf-8 -*-

import hashlib
import urllib

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_security import UserMixin, RoleMixin
from flask_security.core import AnonymousUserMixin
from sqlalchemy.ext.associationproxy import association_proxy

from . import db, login_manager


def get_or_create(session, model, **kwargs):
    """
    获取或者创建对象
    :param session: db session对象
    :param model: model类
    :param kwargs: 条件，比如date='2015-01-01'
    :return:如果数据库中存在对应的对象，就返回该对象，否则在数据库中创建这个对象并返回
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal_id = db.Column(db.Integer)
    zip_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=db.func.now())
    update_date = db.Column(db.DateTime, default=db.func.now())
    client_id = db.Column(db.Integer)
    chef_id = db.Column(db.Integer)
    address = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    message = db.Column(db.String(256))
    # 状态：未处理、已处理、确认收货、取消
    status = db.Column(db.Enum('UNHANDLED', 'HANDLED', 'COMPLETED', 'CANCELED'))
    remark = db.Column(db.String(256))

    @property
    def zipcode(self):
        return Zipcode.query.get_or_404(self.zip_id)

    @zipcode.setter
    def zipcode(self, zipcode):
        self.zip_id = zipcode.id

    @property
    def meal(self):
        return Meal.query.get_or_404(self.meal_id)

    @meal.setter
    def meal(self, meal):
        self.meal_id = meal.id

    @property
    def client(self):
        return User.query.get_or_404(self.client_id)

    @client.setter
    def client(self, client):
        self.client_id = client.id

    @property
    def chef(self):
        return User.query.get_or_404(self.chef_id)

    @chef.setter
    def chef(self, chef):
        self.chef_id = chef.id


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    @staticmethod
    def add(role):
        db.session.add(role)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(60))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(36))
    about_me = db.Column(db.String(512))
    last_seen = db.Column(db.DateTime)

    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        # raise AttributeError('password is not a readable attribute')
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '%s(%s)' % (self.nickname, self.email)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def get_gravatar_url(self):
        size = 40
        random = 'identicon'
        # construct the url
        gravatar_url = "http://www.gravatar.com/avatar/" + \
                       hashlib.md5(self.email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d': random, 's': str(size)})
        return gravatar_url

    @property
    def meals(self):
        return Meal.query.filter(Meal.chef_id == self.id)

    @meals.setter
    def meals(self, meals):
        raise AttributeError('password is not a writable attribute')

    @property
    def client_orders(self):
        return Order.query.filter(Order.client_id == self.id)

    @client_orders.setter
    def client_orders(self, orders):
        raise AttributeError('client_orders is not a writable attribute')

    @property
    def chef_orders(self):
        return Order.query.filter(Order.chef_id == self.id)

    @chef_orders.setter
    def chef_orders(self, orders):
        raise AttributeError('chef_orders is not a writable attribute')


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class ChefApply(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    applicant_id = db.Column(db.Integer())
    content = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.Enum('waiting', 'refused', 'approved'))
    update_time = db.Column(db.DateTime, default=db.func.now())
    admin_id = db.Column(db.Integer())

    @property
    def applicant(self):
        return User.query.get_or_404(self.applicant_id)

    @applicant.setter
    def applicant(self, applicant):
        self.applicant_id = applicant.id

    @property
    def admin(self):
        return User.query.get_or_404(self.admin_id)

    @admin.setter
    def admin(self, admin):
        if admin.has_role('admin'):
            self.admin_id = admin.id
        else:
            raise ValueError('The user has not the admin role')


class Meal(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    is_selected = db.Column(db.Boolean, default=False)
    chef_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime, default=db.func.now())
    zipcodes = association_proxy('meal_zipcodes', 'zipcode')

    def __repr__(self):
        return '<Meal %r>' % self.name

    @property
    def orders(self):
        return Order.query.filter(Order.meal_id == self.id)

    @orders.setter
    def orders(self, orders):
        raise AttributeError('orders is not a writable attribute')

    @property
    def chef(self):
        return User.query.get_or_404(self.chef_id)

    @chef.setter
    def chef(self, chef):
        self.chef_id = chef.id


class Zipcode(db.Model):
    __tablename__ = 'zipcode'
    id = db.Column(db.Integer(), primary_key=True)
    zipcode = db.Column(db.String(20))
    meals = association_proxy('meal_zipcodes', 'meal')

    def __repr__(self):
        return '<Zipcode %r>' % self.zipcode

    @staticmethod
    def add_zips(zips):
        """
        批量添加zip
        :param zips: zip list
        :return:所有zip对象
        """
        return [get_or_create(db.session, Zipcode, zipcode=zip.strip()) for zip in zips]

    @staticmethod
    def is_valid(zipcode):
        if zipcode is not None and zipcode != "" and len(zipcode) == 5 and zipcode.isdigit():
            return True
        else:
            return False

    @property
    def orders(self):
        return Order.query.filter(Order.zip_id == self.id)

    @orders.setter
    def orders(self, orders):
        raise AttributeError('orders is not a writable attribute')


class MealZipcode(db.Model):
    __tablename__ = 'meal_zipcode'
    meal_id = db.Column(db.Integer,
                        db.ForeignKey('meal.id'),
                        primary_key=True)
    zipcode_id = db.Column(db.Integer,
                           db.ForeignKey('zipcode.id'),
                           primary_key=True)
    begin_date = db.Column(db.Date, default=db.func.now())
    end_date = db.Column(db.Date, default=db.func.now())
    create_date = db.Column(db.DateTime, default=db.func.now())
    zipcode = db.relationship(Zipcode,
                              backref=db.backref('meal_zipcodes',
                                                 cascade='all, delete-orphan')
                              )
    meal = db.relationship(Meal,
                           backref=db.backref('meal_zipcodes',
                                              cascade='all, delete-orphan'))
