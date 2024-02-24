from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from . import appbuilder, db
from .models import Competition, Player, Team, CompTeamPlayer


class CompTeamPlayerView(ModelView):
    datamodel = SQLAInterface(CompTeamPlayer)
    list_columns = ['comp_id', 'team_id', 'player_id']
    show_template = "appbuilder/general/model/show_cascade.html"


class CompetitionView(ModelView):
    datamodel = SQLAInterface(Competition)
    related_views = [CompTeamPlayerView]
    show_template = "appbuilder/general/model/show_cascade.html"


class TeamView(ModelView):
    datamodel = SQLAInterface(Team)
    related_views = [CompTeamPlayerView]
    show_template = "appbuilder/general/model/show_cascade.html"


class PlayerView(ModelView):
    datamodel = SQLAInterface(Player)
    related_views = [CompTeamPlayerView]
    show_template = "appbuilder/general/model/show_cascade.html"


db.create_all()

appbuilder.add_view(CompTeamPlayerView, "Comp Team Player", icon="fa-folder-open-o", category="League")
appbuilder.add_view(CompetitionView, "Competitions", icon="fa-folder-open-o", category="League")
appbuilder.add_view(TeamView, "Teams", icon="fa-folder-open-o", category="League")
appbuilder.add_view(PlayerView, "Players", icon="fa-folder-open-o", category="League")
