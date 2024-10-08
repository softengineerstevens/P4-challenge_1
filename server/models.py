from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

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
    # a relationship to map a hero to related hero_powers
    hero_powers = db.relationship("HeroPower", back_populates="hero", cascade="all, delete-orphan")

    # add serialization rules which is a tuple
    serialize_rules = ("-hero_powers", )

    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    # adding validation to description
    description = db.Column(db.String)

    # add relationship
    # a relationship to map power to related hero powers
    hero_powers = db.relationship("HeroPower", back_populates="power", cascade = "all, delete-orphan")

    # add serialization rules which is a tuple
    serialize_rules = ("-hero_powers", )

    # # add validation using @validates method
    @validates("description")
    def validate_description(self, key, description):
        if len(description) < 20:
            raise ValueError("Description must have at least 20 characters")
        else:
            return description

            

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)
    # Foreign Key that stores the heros id
    hero_id = db.Column(db.Integer, db.ForeignKey("heroes.id"))
    # Foreign Key that stores the powers id
    power_id = db.Column(db.Integer, db.ForeignKey("powers.id"))

    # add relationships
    # a relationship to map heropowers to related hero
    hero = db.relationship("Hero", back_populates="hero_powers")
    # a relationship to maps heropowers to related power
    power = db.relationship("Power", back_populates="hero_powers")

    # add serialization rules which is a tuple
    serialize_rules = ("-hero.hero_powers", "-power.hero_powers", )

    # add validation
    # # validating the strengths using the @validates method
    strengths = ["Strong", "Weak", "Average"]
    @validates("strength")
    def validate_strength(self, key, strength):
        if strength not in self.strengths:
            raise ValueError("The strength must be a valid strength ")
        else:
            return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'