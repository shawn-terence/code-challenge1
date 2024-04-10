from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship
    powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # serialization rules 
    serialize_rules = ('-powers.hero', '-powers.power')

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    #add relationship
    heroes = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

     # serialization rules 
    serialize_rules = ('-heroes.power',)

    #add validation
    @validates('description')
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError('Description must be at least 20 characters long')
        return description


    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    hero = db.relationship('Hero', back_populates='powers')

    # Define the relationship between HeroPower and Power
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    power = db.relationship('Power', back_populates='heroes')

    # serialization rules 
    serialize_rules = ('-hero.powers', '-power.heroes')

    #add validation
    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in {'Strong', 'Weak', 'Average'}:
            raise ValueError('Strength must be one of: Strong, Weak, Average')
        return strength
    def __repr__(self):
        return f'<HeroPower {self.id}>'
