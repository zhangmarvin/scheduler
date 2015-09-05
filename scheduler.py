import csv
import lp_maker as lpm
import lpsolve55 as lps

from argparse import ArgumentParser


DEFAULT_RANK = 0  # make any time not in the tutor's rankings really, really bad

ID_TO_TIMES = {}
AS_TIMES = set()
IC_TIMES = set()

times_csv_file = raw_input('Input the name of the CSV file containing times: ')
with open(times_csv_file, 'rU') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        time = row[0]
        ID_TO_TIMES[i] = time
        if time.startswith('After School'):
            AS_TIMES.add(i)
        else:
            IC_TIMES.add(i)

TIME_CAPS = {time: 5 for time in AS_TIMES}
TIME_CAPS.update({time: 1 for time in IC_TIMES})  # mapping of each time 'id' to its cap

OPTION_TO_TIMES = (
        AS_TIMES, IC_TIMES, AS_TIMES.union(IC_TIMES),
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
            print("***\nIllegal preference: {1}\n***\n".format(str(pref)))
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
        print('{0}: {1}\n'.format(tutor.name, assigned))
        for placement in tutor.placements:  # check for illegal placements
            if placement not in OPTION_TO_TIMES[tutor.option]:
                print("***\nIllegal time for tutor {0} with option {1}: {2}\n***\n"
                        .format(tutor.name, tutor.option, placement))


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


tutor_csv_file = raw_input('Input the name of the CSV file containing tutors: ')
all_tutors = import_tutors(tutor_csv_file)
assign_placements()
