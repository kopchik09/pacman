from sqlalchemy import Column, Integer, String
from .db_session import sqlalchemybase
class Player(sqlalchemybase):
    __tablename__ = 'players'
    id = Column(Integer, primary_key = True, autoincrement = True)
    adress = Column(String)
    name = Column(String(15))
    color = Column(String(100), default = 'white')
    size = Column(Integer, default = 50)
    x = Column(Integer, default = 500)
    y = Column(Integer, default = 500)
    speed_y = Column(Integer, default = 2)
    speed_x = Column(Integer, default = 2)
    speed_abs = Column(Integer, default = 2)
    w_vision = Column(Integer, default = 800)
    h_vision = Column(Integer, default = 600)
    error = Column(Integer, default = 0)
    def __init__(self, name, adress):
        self.name = name
        self.adress = adress
    
    