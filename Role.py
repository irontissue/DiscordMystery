import collections


# A role is defined by its name, and:
#   Tags:           a list of "tags" - i.e. types it falls under. Tags must contain the role's name as well (e.g
#                   the role "Merlin" would have name = "Merlin" and tags = ["Merlin", "Good"]
#   Dependencies:   a list of other roles it MUST be in the game with, else the game is unplayable.
#   Exclusions:     a list of other roles it CANNOT be in the game with, else the game is unplayable.
#   Knowledge:      a dictionary of other TAGS it has information of when the game starts, mapping TAG (String) to
#                   knowledge level of that role (defined below).
#   Knows Self:     A boolean indicating if this role knows who they themselves are. Usually this will be True...
#   Limit:          an integer value which describes the max number of this role that can be in a single game.
class Role:

    # Knowledge levels:
    # Doesn't have knowledge of a particular tag. This is the default state.
    NO_KNOWLEDGE = 0
    # Knows that this tag exists in the current game, but doesn't know who specifically it is.
    EXISTS_KNOWLEDGE = 1
    # Knows that this tag exists, and how many of this tag are in the game, but not who specifically is that tag.
    EXISTS_NUM_KNOWLEDGE = 2
    # Knows specifically who occupies this tag.
    KNOWS_KNOWLEDGE = 3

    OFFICIAL_NAME = 'Default Role'
    KNOWLEDGE = {}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = []

    def __init__(self, member, name=None, tags=None, dependencies=None, exclusions=None, knowledge=None, knows_self_role=True, limit=10):
        if name is None:
            self.name = "Unknown Role"
        else:
            self.name = name
        if tags is None:
            self.tags =[self.name]
        else:
            self.tags = tags
        if dependencies is None:
            self.dependencies = []
        else:
            self.dependencies = dependencies
        if exclusions is None:
            self.exclusions = []
        else:
            self.exclusions = exclusions
        if knowledge is None:
            self.knowledge = []
        else:
            self.knowledge = knowledge
        self.limit = limit
        self.member = member
        self.knows_self_role = knows_self_role

    # Returns True/False if the given role list (list of Strings) is a valid role list. Then, returns it as
    # a list of Role objects, using the given dictionary. If False is returned, then instead of a list of Roles
    # this returns a String with the error in the role list.
    @staticmethod
    def check_valid_roles(role_list, all_roles_dict, num_players):
        try:
            if len(role_list) != num_players:
                return False, f"Incorrect number of roles ({len(role_list)}) given for {num_players} players."
            roles_count = collections.defaultdict(int)
            true_roles = []
            for r in role_list:
                role = r.lower()
                if role not in all_roles_dict:
                    return False, "Role \"" + str(role) + "\" is not a valid role for this game type!"
                else:
                    my_role = all_roles_dict[role]
                    true_roles.append(my_role)
                    roles_count[role] += 1
                    if roles_count[role] > my_role.LIMIT:
                        return False, "You can't have more than " + str(my_role.LIMIT) + \
                               " of role \"" + str(role) + "\" in this game!"

            for role in true_roles:
                for dependent in role.DEPENDENCIES:
                    if dependent not in role_list:
                        return False, "\"" + str(role.name) + "\" requires that \"" + str(dependent) + "\" is in the game!"
                for exclusion in role.EXCLUSIONS:
                    if exclusion in role_list:
                        return False, "\"" + str(role.name) + "\" requires that \"" + str(exclusion) +\
                               "\" can't be in the game!"
            return True, true_roles
        except Exception as e:
            print(e)
            return False, str(e)

    def __eq__(self, other):
        if other.name == self.name:
            return True
        return False

    def __str__(self):
        return self.name


class LoyalServant(Role):

    OFFICIAL_NAME = 'Loyal Servant'
    KNOWLEDGE = {}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Good']
    LIMIT = 10

    def __init__(self, member):
        super().__init__(member, name=LoyalServant.OFFICIAL_NAME, tags=LoyalServant.TAGS)


class MinionOfMordred(Role):

    OFFICIAL_NAME = 'Minion of Mordred'
    KNOWLEDGE = {}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Bad']
    LIMIT = 10

    def __init__(self, member):
        super().__init__(member, name=MinionOfMordred.OFFICIAL_NAME, tags=MinionOfMordred.TAGS)


class Mordred(Role):

    OFFICIAL_NAME = 'Mordred'
    KNOWLEDGE = {'Bad': Role.KNOWS_KNOWLEDGE, 'Oberon': Role.EXISTS_NUM_KNOWLEDGE}
    DEPENDENCIES = ['Merlin']
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Bad']
    LIMIT = 1

    def __init__(self, member):
        super().__init__(member, name=Mordred.OFFICIAL_NAME, tags=Mordred.TAGS, dependencies=Mordred.DEPENDENCIES,
                         knowledge=Mordred.KNOWLEDGE, limit=Mordred.LIMIT)


class Merlin(Role):

    OFFICIAL_NAME = 'Merlin'
    KNOWLEDGE = {'Good': Role.KNOWS_KNOWLEDGE,
                 'Bad': Role.KNOWS_KNOWLEDGE,
                 Mordred.OFFICIAL_NAME: Role.EXISTS_NUM_KNOWLEDGE}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Good', 'MerlinOrMorgana']
    LIMIT = 1

    def __init__(self, member):
        super().__init__(member, name=Merlin.OFFICIAL_NAME, tags=Merlin.TAGS,
                         knowledge=Merlin.KNOWLEDGE, limit=Merlin.LIMIT)


class Morgana(Role):

    OFFICIAL_NAME = 'Morgana'
    KNOWLEDGE = {'Bad': Role.KNOWS_KNOWLEDGE, 'Oberon': Role.EXISTS_NUM_KNOWLEDGE}
    DEPENDENCIES = ['Percival']
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Bad', 'MerlinOrMorgana']
    LIMIT = 1

    def __init__(self, member):
        super().__init__(member, name=Morgana.OFFICIAL_NAME, tags=Morgana.TAGS,
                         dependencies=Morgana.DEPENDENCIES, knowledge=Morgana.KNOWLEDGE, limit=Morgana.LIMIT)


class Oberon(Role):

    OFFICIAL_NAME = 'Oberon'
    KNOWLEDGE = {}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Bad']
    LIMIT = 1

    def __init__(self, member):
        super().__init__(member, name=Oberon.OFFICIAL_NAME, tags=Oberon.TAGS, limit=Oberon.LIMIT)


class Percival(Role):

    OFFICIAL_NAME = 'Percival'
    KNOWLEDGE = {'MerlinOrMorgana': Role.KNOWS_KNOWLEDGE}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Good']
    LIMIT = 1

    def __init__(self, member):
        super().__init__(member, name=Percival.OFFICIAL_NAME, tags=Percival.TAGS,
                         knowledge=Percival.KNOWLEDGE, limit=Percival.LIMIT)


class DarkServant(Role):

    OFFICIAL_NAME = 'Dark Servant'
    KNOWLEDGE = {'Bad': Role.EXISTS_KNOWLEDGE}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Bad']
    LIMIT = 999

    def __init__(self, member):
        super().__init__(member, name=DarkServant.OFFICIAL_NAME, tags=DarkServant.TAGS,
                         knowledge=DarkServant.KNOWLEDGE, knows_self_role=False, limit=DarkServant.LIMIT)


class LightServant(Role):

    OFFICIAL_NAME = 'Light Servant'
    KNOWLEDGE = {'Good': Role.EXISTS_KNOWLEDGE}
    DEPENDENCIES = []
    EXCLUSIONS = []
    TAGS = [OFFICIAL_NAME, 'Good']
    LIMIT = 999

    def __init__(self, member):
        super().__init__(member, name=LightServant.OFFICIAL_NAME, tags=LightServant.TAGS,
                         knowledge=LightServant.KNOWLEDGE, knows_self_role=False, limit=DarkServant.LIMIT)
