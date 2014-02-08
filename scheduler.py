import csv
import lp_maker as lpm
import lpsolve55 as lps

from argparse import ArgumentParser

DEFAULT_RANK = 0  # make any time not in the tutor's rankings really, really bad

### INSERT MAPPING OF TIMES TO NUMBERS HERE ###
ID_TO_TIMES = {
    0: "After School, Washington: Monday, 3:45-4:30pm",
    1: "After School, Rosa Parks: Tuesday, 4:45-5:30pm",
    2: "After School, John Muir: Wednesday, 3:15-4:00pm",
    3: "After School, Cragmont: Thursday, 3:30-4:15pm",
    4: "After School, Thousand Oaks: Thursday, 2:45 - 3:30",
    5: "After School, Oxford: Friday, 2:45-3:30pm",
    6: "After School, Martin Luther King: Friday, 3:00-4:00pm",
    7: "Monday, 7:23-8:21 (Berkeley High Orchestra)",
    8: "Monday, 7:45-8:30 (King Band)",
    9: "Monday, 7:45-8:30 (King Orchestra)",
    10: "Monday, 7:45-8:30 (King Chorus)",
    11: "Monday, 7:45-8:30 (Willard Band)",
    12: "Monday, 7:45-8:30 (Willard Orchestra)",
    13: "Monday, 8:05-8:50 (Longfellow Band)",
    14: "Monday, 8:05-8:50 (Longfellow Orchestra)",
    15: "Monday, 8:27-9:25 (Berkeley High Concert Band)",
    16: "Monday, 9:00-10:01 (Longfellow Concert Band)",
    17: "Monday, 9:00-10:01 (Longfellow Rock Music)",
    18: "Monday, 10:35-11:20 (Emerson)",
    19: "Monday, 10:35-12:05 (Malcolm X)",
    20: "Monday, 10:40-11:38 (Berkeley High Guitar)",
    21: "Monday, 11:20-12:05 (Emerson)",
    22: "Monday, 12:30-1:15 (Le Conte)",
    23: "Monday, 12:35-1:20 (Thousand Oaks)",
    24: "Monday, 12:45-1:30 (Jefferson)",
    25: "Monday, 1:20-2:05 (Le Conte)",
    26: "Monday, 1:25-2:10 (Thousand Oaks)",
    27: "Monday, 1:28-2:26 (Berkeley High Chorus)",
    28: "Monday, 1:35-2:20 (Jefferson)",
    29: "Monday, 3:00-3:45 (Longfellow Jazz)",
    30: "Monday, 3:00-3:45 (King Jazz)",
    31: "Monday, 3:00-3:45 (King Modern Music)",
    32: "Monday, 3:00-3:45 (Willard Jazz)",
    33: "Tuesday, 7:23-8:21 (Berkeley High Orchestra)",
    34: "Tuesday, 7:45-8:30 (King Band)",
    35: "Tuesday, 7:45-8:30 (King Orchestra)",
    36: "Tuesday, 7:45-8:30 (King Chorus)",
    37: "Tuesday, 7:45-8:30 (Willard Band)",
    38: "Tuesday, 7:45-8:30 (Willard Orchestra)",
    39: "Tuesday, 8:05-8:50 (Longfellow Band)",
    40: "Tuesday, 8:05-8:50 (Longfellow Orchestra)",
    41: "Tuesday, 8:27-9:25 (Berkeley High Concert Band)",
    42: "Tuesday, 9:00-10:01 (Longfellow Concert Band)",
    43: "Tuesday, 9:45-10:30 (Rosa Parks)",
    44: "Tuesday, 10:15-11:00 (Washington)",
    45: "Tuesday, 10:40-11:38 (Berkeley High Guitar)",
    46: "Tuesday, 10:45-11:30 (Rosa Parks)",
    47: "Tuesday, 11:05-11:50 (Washington)",
    48: "Tuesday, 1:05-1:55 (Oxford)",
    49: "Tuesday, 1:10-1:55 (Oxford)",
    50: "Tuesday, 1:35-2:20 (Cragmont)",
    51: "Tuesday, 1:40-2:25 (Berkeley Arts Magnet)",
    52: "Tuesday, 1:28-2:26 (Berkeley High Chorus)",
    53: "Tuesday, 2:25-3:10 (Cragmont)",
    54: "Tuesday, 2:30-3:20 (Berkeley Arts Magnet)",
    55: "Tuesday, 3:00-3:45 (King Jazz)",
    56: "Tuesday, 3:00-3:45 (King Modern Music)",
    57: "Tuesday, 3:00-3:45 (Longfellow Jazz)",
    58: "Wednesday, 7:23-8:21 (Berkeley High Orchestra)",
    59: "Wednesday, 7:45-8:30 (King Band)",
    60: "Wednesday, 7:45-8:30 (King Orchestra)",
    61: "Wednesday, 7:45-8:30 (King Chorus)",
    62: "Wednesday, 7:45-8:30 (Willard Band)",
    63: "Wednesday, 7:45-8:30 (Willard Orchestra)",
    64: "Wednesday, 8:05-8:50 (Longfellow Band)",
    65: "Wednesday, 8:05-8:50 (Longfellow Orchestra)",
    66: "Wednesday, 8:27-9:25 (Berkeley High Concert Band)",
    67: "Wednesday, 9:00-10:01 (Longfellow Concert Band)",
    68: "Wednesday, 10:35-11:20 (Emerson)",
    69: "Wednesday, 10:30-11:15 (Malcolm X)",
    70: "Wednesday, 10:40-11:38 (Berkeley High Guitar)",
    71: "Wednesday, 11:15-12:50 (John Muir)",
    72: "Wednesday, 11:20-12:05 (Malcolm X)",
    73: "Wednesday, 11:25-12:05 (Emerson)",
    74: "Wednesday, 1:28-2:26 (Berkeley High Chorus)",
    75: "Wednesday, 3:00-3:45 (King Jazz)",
    76: "Wednesday, 3:00-3:45 (King Modern Music)",
    77: "Wednesday, 3:00-3:45 (Longfellow Jazz)",
    78: "Wednesday, 3:00-3:45 (Willard Jazz)",
    79: "Thursday, 7:23-8:21 (Berkeley High Orchestra)",
    80: "Thursday, 7:45-8:30 (King Band)",
    81: "Thursday, 7:45-8:30 (King Orchestra)",
    82: "Thursday, 7:45-8:30 (King Chorus)",
    83: "Thursday, 7:45-8:30 (Willard Band)",
    84: "Thursday, 7:45-8:30 (Willard Orchestra)",
    85: "Thursday, 8:05-8:50 (Longfellow Band)",
    86: "Thursday, 8:05-8:50 (Longfellow Orchestra)",
    87: "Thursday, 8:27-9:25 (Berkeley High Concert Band)",
    88: "Thursday, 9:00-10:01 (Longfellow Concert Band)",
    89: "Thursday, 9:00-10:01 (Longfellow Rock Music)",
    90: "Thursday, 10:10-10:55 (John Muir)",
    91: "Thursday, 10:40-11:38 (Berkeley High Guitar)",
    92: "Thursday, 11:15-12:00 (John Muir)",
    93: "Thursday, 12:30-1:15 (Le Conte)",
    94: "Thursday, 12:35-1:20 (Thousand Oaks)",
    95: "Thursday, 12:45-1:30 (Jefferson)",
    96: "Thursday, 1:20-2:05 (Le Conte)",
    97: "Thursday, 1:25-2:10 (Thousand Oaks)",
    98: "Thursday, 1:28-2:26 (Berkeley High Chorus)",
    99: "Thursday, 1:35-2:20 (Jefferson)",
    100: "Thursday, 3:00-3:45 (Longfellow Jazz)",
    101: "Thursday, 3:00-3:45 (King Jazz)",
    102: "Thursday, 3:00-3:45 (King Modern Music)",
    103: "Thursday, 3:00-3:45 (Willard Jazz)",
    104: "Friday, 7:23-8:21 (Berkeley High Orchestra)",
    105: "Friday, 7:45-8:30 (King Band)",
    106: "Friday, 7:45-8:30 (King Orchestra)",
    107: "Friday, 7:45-8:30 (King Chorus)",
    108: "Friday, 7:45-8:30 (Willard Band)",
    109: "Friday, 7:45-8:30 (Willard Orchestra)",
    110: "Friday, 8:05-8:50 (Longfellow Band)",
    111: "Friday, 8:05-8:50 (Longfellow Orchestra)",
    112: "Friday, 8:27-9:25 (Berkeley High Concert Band)",
    113: "Friday, 9:00-10:01 (Longfellow Concert Band)",
    114: "Friday, 9:45-10:30 (Rosa Parks)",
    115: "Friday, 10:15-11:50 (Washington)",
    116: "Friday, 10:40-11:38 (Berkeley High Guitar)",
    117: "Friday, 10:45-11:30 (Rosa Parks)",
    118: "Friday, 12:20-1:05 (Oxford)",
    119: "Friday, 1:05-1:55 (Oxford)",
    120: "Friday, 1:35-2:20 (Cragmont)",
    121: "Friday, 1:40-2:25 (Berkeley Arts Magnet)",
    122: "Friday, 1:28-2:26 (Berkeley High Chorus)",
    123: "Friday, 2:25-3:10 (Berkeley Arts Magnet)",
    124: "Friday, 2:25-3:10 (Cragmont)",
    125: "Friday, 3:00-3:45 (King Jazz)",
    126: "Friday, 3:00-3:45 (King Modern Music)",
    127: "Friday, 3:00-3:45 (Longfellow Jazz)",
    128: "Friday, 3:00-3:45 (Willard Jazz)",
}

# these can be ranges, not overlapping
# i.e., every time gets its own unique 'id'
AS_TIMES = range(0, 7)
IC_TIMES = range(7, 129)

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

