from flask_appbuilder import Model
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


class Competition(Model):
    code = Column(String(50), primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    areaName = Column(String(50), nullable=False)


class Team(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    tla = Column(String(50).evaluates_none(), nullable=True, server_default="default")
    shortName = Column(String(50), nullable=False)
    areaName = Column(String(50), nullable=False)
    email = Column(String(50).evaluates_none(), nullable=True, server_default="default")


class Player(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    position = Column(String(50).evaluates_none(), nullable=True, server_default="default")
    dateOfBirth = Column(DateTime, nullable=True, server_default="default")
    countryOfBirth = Column(String(50).evaluates_none(), nullable=True, server_default="default")
    nationality = Column(String(50).evaluates_none(), nullable=True, server_default="default")


class CompTeamPlayer(Model):
    comp_id = Column(Integer, ForeignKey("competition.code"), primary_key=True, nullable=False)
    competition = relationship("Competition")
    team_id = Column(Integer, ForeignKey("team.id"), primary_key=True, nullable=False)
    team = relationship("Team")
    player_id = Column(Integer, ForeignKey("player.id"), primary_key=True, nullable=False)
    player = relationship("Player")
