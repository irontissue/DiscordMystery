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

    def __init__(self, name=None, tags=None, dependencies=None, exclusions=None, knowledge=None, knows_self_role=True, limit=10):
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
        self.member = None
        self.knows_self_role = knows_self_role

    # Returns True/False if the given role list (list of Strings) is a valid role list. Then, returns it as
    # a list of Role objects, using the given dictionary. If False is returned, then instead of a list of Roles
    # this returns a String with the error in the role list.
    @staticmethod
    def check_valid_roles(role_list, all_roles_dict):
        roles_count = collections.defaultdict(int)
        true_roles = []
        for r in role_list:
            role = r.lower()
            if role not in all_roles_dict:
                return False, "Role \"" + str(role) + "\" is not a valid role for this game type!"
            else:
                my_role = all_roles_dict[role]()
                true_roles.append(my_role)
                roles_count[role] += 1
                if roles_count[role] > my_role.limit:
                    return False, "You can't have more than " + str(my_role.limit) + \
                           " of role \"" + str(role) + "\" in this game!"

        for role in true_roles:
            for dependent in role.dependencies:
                if dependent not in role_list:
                    return False, "\"" + str(role.name) + "\" requires that \"" + str(dependent) + "\" is in the game!"
            for exclusion in role.exclusions:
                if exclusion in role_list:
                    return False, "\"" + str(role.name) + "\" requires that \"" + str(exclusion) +\
                           "\" can't be in the game!"
        return True, true_roles

    def __eq__(self, other):
        if other.name == self.name:
            return True
        return False

    def __str__(self):
        return self.name


class LoyalServant(Role):

    OFFICIAL_NAME = 'Loyal Servant'

    def __init__(self):
        super().__init__(LoyalServant.OFFICIAL_NAME, tags=[LoyalServant.OFFICIAL_NAME, 'Good'])


class MinionOfMordred(Role):

    OFFICIAL_NAME = 'Minion of Mordred'

    def __init__(self):
        super().__init__(MinionOfMordred.OFFICIAL_NAME, tags=[MinionOfMordred.OFFICIAL_NAME, 'Bad'])


class Mordred(Role):

    OFFICIAL_NAME = 'Mordred'

    def __init__(self):
        knowledge = {'Bad': Role.KNOWS_KNOWLEDGE, 'Oberon': Role.EXISTS_NUM_KNOWLEDGE}
        super().__init__(Mordred.OFFICIAL_NAME, tags=[Mordred.OFFICIAL_NAME, 'Bad'], dependencies=['Merlin'],
                         knowledge=knowledge, limit=1)


class Merlin(Role):

    OFFICIAL_NAME = 'Merlin'

    def __init__(self):
        knowledge = {'Good': Role.KNOWS_KNOWLEDGE,
                     'Bad': Role.KNOWS_KNOWLEDGE,
                     Mordred.OFFICIAL_NAME: Role.EXISTS_NUM_KNOWLEDGE}
        super().__init__(Merlin.OFFICIAL_NAME, tags=[Merlin.OFFICIAL_NAME, 'Good', 'MerlinOrMorgana'],
                         knowledge=knowledge, limit=1)


class Morgana(Role):

    OFFICIAL_NAME = 'Morgana'

    def __init__(self):
        knowledge = {'Bad': Role.KNOWS_KNOWLEDGE, 'Oberon': Role.EXISTS_NUM_KNOWLEDGE}
        super().__init__(Morgana.OFFICIAL_NAME, tags=[Morgana.OFFICIAL_NAME, 'Bad', 'MerlinOrMorgana'],
                         dependencies=['Percival'], knowledge=knowledge, limit=1)


class Oberon(Role):

    OFFICIAL_NAME = 'Oberon'

    def __init__(self):
        super().__init__(Oberon.OFFICIAL_NAME, tags=[Oberon.OFFICIAL_NAME, 'Bad'], limit=1)


class Percival(Role):

    OFFICIAL_NAME = 'Percival'

    def __init__(self):
        knowledge = {'MerlinOrMorgana': Role.KNOWS_KNOWLEDGE}
        super().__init__(Percival.OFFICIAL_NAME, tags=[Percival.OFFICIAL_NAME, 'Good'], knowledge=knowledge, limit=1)
