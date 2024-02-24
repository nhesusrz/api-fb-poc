import datetime
import time
from http import HTTPStatus
from random import random

import requests
from flask_appbuilder.api import BaseApi, expose, ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app import db
from . import appbuilder
from .models import Competition, Player, Team, CompTeamPlayer


class ImportApi(BaseApi):

    @expose('/import-league/<string:league_code>', methods=['GET'])
    def import_league(self, league_code):
        """Import league data including teams and players using the Football Data API.
        API reference: https://www.football-data.org/documentation/api
            ---
            get:
              summary: Import a league data from league code. https://www.football-data.org/docs/v1/index.html#league_codes
              parameters:
              - in: path
                name: league_code
                schema:
                  type: string
                  required: true
                description: League code id.
              responses:
                201:
                  description: Successfully imported
                  content:
                    application/json:
                      schema:
                        type: object
                        properties:
                          message:
                            type: string
                            example: Successfully imported

                409:
                  description: League already imported
                  content:
                    application/json:
                      schema:
                        type: object
                        properties:
                          message:
                            type: string
                            example: League already imported
                404:
                  description: League code not found on Football Data API.
                  content:
                    application/json:
                      schema:
                        type: object
                        properties:
                          message:
                            type: string
                            example: Not Found
                504:
                  description: If a connectivity issue occurs with DB server or Football Data API.
                  content:
                    application/json:
                      schema:
                        type: object
                        properties:
                          message:
                            type: string
                            example: Server Error
        """
        try:
            exists = bool(db.session.query(Competition.code).filter_by(code=league_code).first())
            if exists:
                return self.response(409, message="League already imported")
            if import_data(league_code):
                return self.response(201, message="Successfully imported")
            return self.response(404, message="Not Found")
        except requests.HTTPError or SQLAlchemyError as err:
            db.session.rollback()
            return self.response(504, message="Server Error")

    @expose('/total-players/<string:league_code>', methods=['GET'])
    def total_players(self, league_code):
        """Return the total amount of players related to League Code using the imported data in DB.
            ---
        get:
          summary: Import a league data from league code. https://www.football-data.org/docs/v1/index.html#league_codes
          parameters:
          - in: path
            name: league_code
            schema:
              type: string
              required: true
            description: League code id.
          responses:
            200:
              description: Return the total amount of players related to League Code using the imported data in DB.
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      total:
                        type: integer
                        example: 55
            404:
              description: The given League Code not exists in DB.
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
                        example: Not Found
            504:
              description: If a connectivity issue occurs with DB server.
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
                        example: Server Error
        """
        try:
            exists = bool(db.session.query(Competition.code).filter_by(code=league_code).first())
            if exists:
                count = db.session.query(CompTeamPlayer.comp_id).filter_by(comp_id=league_code).count()
                return self.response(200, total=count)
            return self.response(404, message="Not Found")
        except SQLAlchemyError as err:
            return self.response(504, message="Server Error")


class CompetitionModelApi(ModelRestApi):
    resource_name = 'competition'
    datamodel = SQLAInterface(Competition)


class TeamModelApi(ModelRestApi):
    resource_name = 'team'
    datamodel = SQLAInterface(Team)


class PlayerModelApi(ModelRestApi):
    resource_name = 'player'
    datamodel = SQLAInterface(Player)


class FootballApi(BaseApi):
    COMP_URL = 'http://api.football-data.org/v2/competitions/'
    TEAM_URL = 'https://api.football-data.org/v2/teams/'
    HEADERS = {'X-Auth-Token': '8b9659010ca14b6ebcffa5cc7c30ae43', 'Accept-Encoding': ''}

    @classmethod
    def get_competitions(cls, league_code: str):
        return requests.get(cls.COMP_URL + league_code, headers=cls.HEADERS)

    @classmethod
    def get_teams(cls, competition_id: str):
        response = requests.get(cls.COMP_URL + competition_id + '/teams', headers=cls.HEADERS)
        if (response.status_code == HTTPStatus.TOO_MANY_REQUESTS):
            current_app.logger.error(response.text + "\n" + str(response.headers))
            retry_duration = int(response.headers.get('X-RequestCounter-Reset'))
            time.sleep(retry_duration)
            response = requests.get(cls.COMP_URL + competition_id + '/teams', headers=cls.HEADERS)
        return response

    @classmethod
    def get_team_players(cls, team_id: str):
        response = requests.get(cls.TEAM_URL + team_id, headers=cls.HEADERS)
        if (response.status_code == HTTPStatus.TOO_MANY_REQUESTS):
            current_app.logger.error(response.text + "\n" + str(response.headers))
            retry_duration = int(response.headers.get('X-RequestCounter-Reset'))
            time.sleep(retry_duration)
            response = requests.get(cls.TEAM_URL + team_id, headers=cls.HEADERS)
        return response.json()['squad']


def import_data(league_code):
    comp_resp = FootballApi().get_competitions(league_code)
    if comp_resp.status_code != HTTPStatus.OK:
        return False
    comp_data = comp_resp.json()
    comp_model = Competition(code=league_code,
                             name=comp_data['name'],
                             areaName=comp_data['area']['name'])
    db.session.add(comp_model)
    teams_data = FootballApi().get_teams(str(comp_data['id'])).json()['teams']
    for team_data in teams_data:
        if not bool(db.session.query(Team.id).filter_by(id=team_data['id']).first()):
            team_model = Team(id=team_data['id'],
                              name=team_data['name'],
                              tla=team_data['tla'],
                              shortName=team_data['shortName'],
                              areaName=team_data['area']['name'],
                              email=team_data['email'])
            db.session.add(team_model)
        players_data = FootballApi().get_team_players(str(team_data['id']))
        for player_data in players_data:
            if not bool(db.session.query(Player.id).filter_by(id=player_data['id']).first()):
                player_model = Player(id=player_data['id'],
                                      name=player_data['name'],
                                      position=player_data['position'],
                                      dateOfBirth=None if player_data[
                                                              'dateOfBirth'] is None else datetime.datetime.strptime(
                                          player_data['dateOfBirth'], '%Y-%m-%dT%H:%M:%SZ'),
                                      countryOfBirth=player_data['countryOfBirth'],
                                      nationality=player_data['nationality'])
                db.session.add(player_model)
            helper_model = CompTeamPlayer(comp_id=league_code,
                                          team_id=team_data['id'],
                                          player_id=player_data['id'])
            db.session.add(helper_model)
    db.session.commit()
    return True


appbuilder.add_api(ImportApi)
appbuilder.add_api(CompetitionModelApi)
appbuilder.add_api(TeamModelApi)
appbuilder.add_api(PlayerModelApi)
appbuilder.add_api(FootballApi)
