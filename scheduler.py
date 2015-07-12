import csv
import lp_maker as lpm
import lpsolve55 as lps

from argparse import ArgumentParser

DEFAULT_RANK = 0  # make any time not in the tutor's rankings really, really bad

### INSERT MAPPING OF TIMES TO NUMBERS HERE ###
ID_TO_TIMES = {
    0: "After School, Washington: Tuesday, 4:00-5:00pm",
    1: "After School, Le Conte: Monday, 4:00-4:45pm",
    2: "After School, Rosa Parks: Tuesday, 4:45-5:45pm",
    3: "After School, John Muir: Wednesday, 3:15-4:00pm",
    4: "After School, Longfellow: Wednesday, 3:15-4:00pm",
    5: "After School, Thousand Oaks: Thursday, 2:45-3:30pm",
    6: "After School, Oxford: Friday, 2:45-3:30pm",
    7: "After School, Martin Luther King: Monday, 3:10-4:00pm",
    8: "After School, Martin Luther King: Thursday, 3:10-4:00pm",
    9: "After School, Willard: Friday, 3:15-4:00pm",
    10: "After School, Malcolm X: Wednesday, 2:00-3:00pm",
    11: "Monday, 7:23-8:21 (Berkeley High Orchestra)",
    12: "Monday, 7:45-8:30 (King Band)",
    13: "Monday, 7:45-8:30 (King Orchestra)",
    14: "Monday, 7:45-8:30 (King Chorus)",
    15: "Monday, 7:45-8:30 (Willard Band)",
    16: "Monday, 7:45-8:30 (Willard Orchestra)",
    17: "Monday, 8:05-8:50 (Longfellow Band)",
    18: "Monday, 8:05-8:50 (Longfellow Orchestra)",
    19: "Monday, 8:27-9:25 (Berkeley High Concert Band)",
    20: "Monday, 9:00-10:01 (Longfellow Concert Band)",
    21: "Monday, 9:00-10:01 (Longfellow Rock Music)",
    22: "Monday, 10:30-11:15 (Malcolm X)",
    23: "Monday, 10:35-11:20 (Emerson)",
    24: "Monday, 10:40-11:38 (Berkeley High Guitar)",
    25: "Monday, 11:20-12:05 (Malcolm X)",
    26: "Monday, 11:20-12:05 (Emerson)",
    27: "Monday, 12:35-1:20 (Thousand Oaks)",
    28: "Monday, 12:40-1:25 (Le Conte)",
    29: "Monday, 12:45-1:30 (Jefferson)",
    30: "Monday, 1:30-2:15 (Le Conte)",
    31: "Monday, 1:25-2:10 (Thousand Oaks)",
    32: "Monday, 1:28-2:26 (Berkeley High Chorus)",
    33: "Monday, 1:35-2:20 (Jefferson)",
    34: "Monday, 3:00-3:45 (Longfellow Jazz)",
    35: "Monday, 3:00-3:45 (King Jazz)",
    36: "Monday, 3:00-3:45 (King Modern Music)",
    37: "Monday, 3:00-3:45 (Willard Jazz)",
    38: "Tuesday, 7:23-8:21 (Berkeley High Orchestra)",
    39: "Tuesday, 7:45-8:30 (King Band)",
    40: "Tuesday, 7:45-8:30 (King Orchestra)",
    41: "Tuesday, 7:45-8:30 (King Chorus)",
    42: "Tuesday, 7:45-8:30 (Willard Band)",
    43: "Tuesday, 7:45-8:30 (Willard Orchestra)",
    44: "Tuesday, 8:05-8:50 (Longfellow Band)",
    45: "Tuesday, 8:05-8:50 (Longfellow Orchestra)",
    46: "Tuesday, 8:27-9:25 (Berkeley High Concert Band)",
    47: "Tuesday, 9:00-10:01 (Longfellow Concert Band)",
    48: "Tuesday, 9:10-11:00 (Washington)",
    49: "Tuesday, 9:45-10:30 (Rosa Parks)",
    50: "Tuesday, 10:40-11:38 (Berkeley High Guitar)",
    51: "Tuesday, 10:45-11:30 (Rosa Parks)",
    52: "Tuesday, 12:20-1:05 (Oxford)",
    53: "Tuesday, 1:10-1:55 (Oxford)",
    54: "Tuesday, 1:35-2:20 (Cragmont)",
    55: "Tuesday, 1:40-2:25 (Berkeley Arts Magnet)",
    56: "Tuesday, 1:28-2:26 (Berkeley High Chorus)",
    57: "Tuesday, 2:25-3:10 (Cragmont)",
    58: "Tuesday, 2:30-3:20 (Berkeley Arts Magnet)",
    59: "Tuesday, 3:00-3:45 (King Jazz)",
    60: "Tuesday, 3:00-3:45 (King Modern Music)",
    61: "Tuesday, 3:00-3:45 (Longfellow Jazz)",
    62: "Wednesday, 7:23-8:21 (Berkeley High Orchestra)",
    63: "Wednesday, 7:45-8:30 (King Band)",
    64: "Wednesday, 7:45-8:30 (King Orchestra)",
    65: "Wednesday, 7:45-8:30 (King Chorus)",
    66: "Wednesday, 7:45-8:30 (Willard Band)",
    67: "Wednesday, 7:45-8:30 (Willard Orchestra)",
    68: "Wednesday, 8:05-8:50 (Longfellow Band)",
    69: "Wednesday, 8:05-8:50 (Longfellow Orchestra)",
    70: "Wednesday, 8:27-9:25 (Berkeley High Concert Band)",
    71: "Wednesday, 9:00-10:01 (Longfellow Concert Band)",
    72: "Wednesday, 10:35-11:20 (Emerson)",
    73: "Wednesday, 10:30-11:15 (Malcolm X)",
    74: "Wednesday, 10:40-11:38 (Berkeley High Guitar)",
    75: "Wednesday, 11:15-12:50 (John Muir)",
    76: "Wednesday, 11:20-12:05 (Malcolm X)",
    77: "Wednesday, 11:25-12:05 (Emerson)",
    78: "Wednesday, 1:28-2:26 (Berkeley High Chorus)",
    79: "Wednesday, 3:00-3:45 (King Jazz)",
    80: "Wednesday, 3:00-3:45 (King Modern Music)",
    81: "Wednesday, 3:00-3:45 (Longfellow Jazz)",
    82: "Wednesday, 3:00-3:45 (Willard Jazz)",
    83: "Thursday, 7:23-8:21 (Berkeley High Orchestra)",
    84: "Thursday, 7:45-8:30 (King Band)",
    85: "Thursday, 7:45-8:30 (King Orchestra)",
    86: "Thursday, 7:45-8:30 (King Chorus)",
    87: "Thursday, 7:45-8:30 (Willard Band)",
    88: "Thursday, 7:45-8:30 (Willard Orchestra)",
    89: "Thursday, 8:05-8:50 (Longfellow Band)",
    90: "Thursday, 8:05-8:50 (Longfellow Orchestra)",
    91: "Thursday, 8:27-9:25 (Berkeley High Concert Band)",
    92: "Thursday, 9:00-10:01 (Longfellow Concert Band)",
    93: "Thursday, 9:00-10:01 (Longfellow Rock Music)",
    94: "Thursday, 10:10-10:55 (John Muir)",
    95: "Thursday, 10:40-11:38 (Berkeley High Guitar)",
    96: "Thursday, 11:15-12:00 (John Muir)",
    97: "Thursday, 12:40-1:25 (Le Conte)",
    98: "Thursday, 12:35-1:20 (Thousand Oaks)",
    99: "Thursday, 12:45-1:30 (Jefferson)",
    100: "Thursday, 1:30-2:15 (Le Conte)",
    101: "Thursday, 1:25-2:10 (Thousand Oaks)",
    102: "Thursday, 1:28-2:26 (Berkeley High Chorus)",
    103: "Thursday, 1:35-2:20 (Jefferson)",
    104: "Thursday, 3:00-3:45 (Longfellow Jazz)",
    105: "Thursday, 3:00-3:45 (King Jazz)",
    106: "Thursday, 3:00-3:45 (King Modern Music)",
    107: "Thursday, 3:00-3:45 (Willard Jazz)",
    108: "Friday, 7:23-8:21 (Berkeley High Orchestra)",
    109: "Friday, 7:45-8:30 (King Band)",
    110: "Friday, 7:45-8:30 (King Orchestra)",
    111: "Friday, 7:45-8:30 (King Chorus)",
    112: "Friday, 7:45-8:30 (Willard Band)",
    113: "Friday, 7:45-8:30 (Willard Orchestra)",
    114: "Friday, 8:05-8:50 (Longfellow Band)",
    115: "Friday, 8:05-8:50 (Longfellow Orchestra)",
    116: "Friday, 8:27-9:25 (Berkeley High Concert Band)",
    117: "Friday, 9:00-10:01 (Longfellow Concert Band)",
    118: "Friday, 9:10-11:00 (Washington)",
    119: "Friday, 9:45-10:30 (Rosa Parks)",
    120: "Friday, 10:40-11:38 (Berkeley High Guitar)",
    121: "Friday, 10:45-11:30 (Rosa Parks)",
    122: "Friday, 12:20-1:05 (Oxford)",
    123: "Friday, 1:10-1:55 (Oxford)",
    124: "Friday, 1:35-2:20 (Cragmont)",
    125: "Friday, 1:40-2:25 (Berkeley Arts Magnet)",
    126: "Friday, 1:28-2:26 (Berkeley High Chorus)",
    127: "Friday, 2:25-3:10 (Berkeley Arts Magnet)",
    128: "Friday, 2:25-3:10 (Cragmont)",
    129: "Friday, 3:00-3:45 (King Jazz)",
    130: "Friday, 3:00-3:45 (King Modern Music)",
    131: "Friday, 3:00-3:45 (Longfellow Jazz)",
    132: "Friday, 3:00-3:45 (Willard Jazz)",
}

# these can be ranges, not overlapping
# i.e., every time gets its own unique 'id'
AS_TIMES = range(0, 11)
IC_TIMES = range(11, 133)

TIME_CAPS = {time: 5 for time in AS_TIMES}
TIME_CAPS.update({time: 1 for time in IC_TIMES})  # mapping of each time 'id' to its cap

OPTION_TO_TIMES = (
        AS_TIMES, IC_TIMES, AS_TIMES + IC_TIMES,
)

NUM_OPTIONS = len(OPTION_TO_TIMES)


class Tutor(object):

    def __init__(self, name, email, option, hours, rankings):
        self.name = name
        self.email = email
        self.option = option  # 0 - 2

        assert option in range(NUM_OPTIONS), 'illegal option'

        self.hours = hours
        self.rankings = rankings
        self.placements = set()


def import_tutors(csv_file):
    """
    Takes in a CSV file, and creates list of tutors based on the file.

    CSV file must be of the form:
    |name| |email| |option| |hours| |rankings ...|
    """

    tutors = set()

    with open(csv_file, 'rU') as f:
        reader = csv.reader(f)

        for row in reader:
            first_name = row[0]
            last_name = row[1]
            email = row[2]
            option = int(row[3])
            hours = int(row[4])
            rankings = prefs_to_rankings(row[5:])

            tutor = Tutor(first_name + ' ' + last_name, email, option, hours, rankings)
            tutors.discard(tutor)  # in case of duplicates, take most recent
            tutors.add(tutor)

    return sorted(tutors, key=lambda tutor: tutor.name.split()[-1])


def prefs_to_rankings(prefs):
    """
    Takes in a list of preferred times, as well as the corresponding option.
    Outputs a list of rankings, containing every relevant time and its rank.
    """

    for pref in prefs[:]:  # make sure there are no illegal preferences
        if pref == '':
            prefs.remove(pref)
        elif int(pref) not in ID_TO_TIMES:
            print("***\nIllegal preference: {1}\n***\n"
                    .format(str(pref)))
            prefs.remove(pref)

    rankings = [DEFAULT_RANK for _ in ID_TO_TIMES]
    rank = 99

    for pref in prefs:
        pref = int(pref)
        rankings[pref] = rank
        if rank > 97:
            rank -= 1  # top three
        else:
            rank = 90  # slightly worse than top three, way better than others

    return rankings


def assign_placements():
    """
    Takes in an option for which to assign placements for.
    Outputs nothing, but calls output_results which prints all placements.
    """

    num_tutors = len(all_tutors)
    num_times = len(ID_TO_TIMES)
    upper = [1 for _ in range(num_tutors * num_times)]  # max value must be 1

    obj_func = make_obj_func()
    constr_mat = make_constr_mat(num_tutors, num_times)
    b_vector = make_b_vector()
    e_vector = make_e_vector(num_tutors, num_times)

    lp = lpm.lp_maker(obj_func, constr_mat, b_vector, e_vector)

    lps.lpsolve('set_bb_depthlimit', lp, 0)  # set branch and bound depth limit
    lps.lpsolve('set_binary', lp, upper)  # all values must be either 0 or 1

    lps.lpsolve('solve', lp)
    vars = lps.lpsolve('get_variables', lp)[0]
    lps.lpsolve('delete_lp', lp)

    output_results(vars)


def output_results(vars):
    """
    Takes in the minimized values for the variables of the objective function,
    along with the list of relevant tutors and times.
    Outputs nothing, but prints all tutors and their placements.
    """

    i = 0  # index variable to traverse through vars
    
    for tutor in all_tutors:
        
        for time in ID_TO_TIMES:
            if vars[i] == 1:
                tutor.placements.add(time)

            i += 1

        assigned = ', '.join([ID_TO_TIMES[id] for id in tutor.placements])

        print('{0}: {1}\n'
                .format(tutor.name, assigned))

#        for placement in tutor.placements:  # check for illegal placements
#            if placement not in OPTION_TO_TIMES[tutor.option]:
#                print("***\nIllegal time for tutor {0} with option {1}: {2}\n***\n"
#                        .format(str(option), str(pref)))


def make_obj_func():
    """
    Takes in list of tutors. Outputs a coefficient matrix of their rankings.
    """

    coeffs = []

    for tutor in all_tutors:
        coeffs.extend(tutor.rankings)

    return coeffs


def make_constr_mat(num_tutors, num_times):
    """
    Takes in the number of tutors and the number of times.
    Outputs the left side of the constraint matrix, which constrains two things:
    1. the maximum number of tutors that can be assigned to a given time
    2. the maximum number of times that can be assigned to a given tutor
    """

    coeffs = []

    for tutor in range(num_tutors):
        hour_coeffs = [0 for _ in range(num_tutors * num_times)]
        
        # constraint of the form:
        # tutorX_time1 + tutorX_time2 + ... + tutorX_timeN <= tutorX.hours
        for i in range(tutor * num_times, (tutor+1) * num_times):
            hour_coeffs[i] = 1

        coeffs.append(hour_coeffs)

    for time in range(num_times):
        cap_coeffs = [0 for _ in range(num_tutors * num_times)]

        # constraint of the form:
        # tutor1_timeY + tutor2_timeY + ... + tutorM_timeY <= TIME_CAPS[timeY]
        for i in range(time, num_tutors * num_times, num_times):
            cap_coeffs[i] = 1

        coeffs.append(cap_coeffs)

    return coeffs


def make_b_vector():
    """
    Takes in a list of relevant tutors and a list of relevant times.
    Outputs the right side of the constraint matrix corresponding to make_constr_mat.
    """

    return [tutor.hours for tutor in all_tutors] + [TIME_CAPS[time] for time in ID_TO_TIMES]


def make_e_vector(num_tutors, num_times):
    """
    Takes in the number of tutors and the number of times.
    Outputs the vector representing the form of inequality for the constraint matrix.
    -1 is equivalent to <=
    """

    return [-1 for _ in range(num_tutors + num_times)]


parser = ArgumentParser()
parser.add_argument('csv_file', help='csv file containing tutor rankings')
args = parser.parse_args()

all_tutors = import_tutors(args.csv_file)

assign_placements()

