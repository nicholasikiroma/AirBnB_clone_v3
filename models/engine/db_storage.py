#!/usr/bin/python3
"""
Database engine
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models import base_model, amenity, city, place, review, user
from models.state import State


class DBStorage:
    """
        handles long term storage of all class instances
    """
    CNC = {
        'Amenity': amenity.Amenity,
        'City': city.City,
        'Place': place.Place,
        'Review': review.Review,
        'State': State,
        'User': user.User
    }

    """
        handles storage for database
    """
    __engine = None
    __session = None

    def __init__(self):
        """
            creates the engine self.__engine
        """
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                os.environ.get('HBNB_MYSQL_USER'),
                os.environ.get('HBNB_MYSQL_PWD'),
                os.environ.get('HBNB_MYSQL_HOST'),
                os.environ.get('HBNB_MYSQL_DB')))
        if os.environ.get("HBNB_ENV") == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
           returns a dictionary of all objects
        """
        if not self.__session:
            self.reload()
        obj_dict = {}

        if type(cls) == str:
            cls = DBStorage.CNC.get(cls, None)

        if cls:
            for obj in self.__session.query(cls):
                obj_dict[obj.__class__.__name__ + '.' + obj.id] = obj
        else:
            for c in DBStorage.CNC.values():
                for obj in self.__session.query(cls):
                    obj_dict[obj.__class__.__name__ + '.' + obj.id] = obj
        return obj_dict

    def new(self, obj):
        """
            adds objects to current database session
        """
        self.__session.add(obj)

    def save(self):
        """
            commits all changes of current database session
        """
        self.__session.commit()

    def rollback_session(self):
        """
            rollsback a session in the event of an exception
        """
        self.__session.rollback()

    def delete(self, obj=None):
        """
            deletes obj from current database session if not None
        """
        if obj:
            self.__session.delete(obj)
            self.save()

    def delete_all(self):
        """
           deletes all stored objects, for testing purposes
        """
        for c in DBStorage.CNC.values():
            a_query = self.__session.query(c)
            all_objs = [obj for obj in a_query]
            for obj in range(len(all_objs)):
                to_delete = all_objs.pop(0)
                to_delete.delete()
        self.save()

    def reload(self):
        """
           creates all tables in database & session from engine
        """
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(
            sessionmaker(
                bind=self.__engine,
                expire_on_commit=False))

    def close(self):
        """
            calls remove() on private session attribute (self.session)
        """
        self.__session.remove()

    def get(self, cls, id):
        """
            retrieves one object based on class name and id
        """
        if cls is not None and type(cls) is str and id is not None and\
           type(id) is str and cls in DBStorage.CNC:
            cls = DBStorage.CNC[cls]
            result = self.__session.query(cls).filter(cls.id == id).first()
            return result
        else:
            None

    def count(self, cls=None):
        """
            returns the count of all objects in storage
        """
        total = 0
        if type(cls) == str and cls in DBStorage.CNC:
            cls = DBStorage.CNC[cls]
            total = self.__session.query(cls).count()
        elif cls is None:
            for cls in DBStorage.CNC.values():
                total += self.__session.query(cls).count()
        return total
