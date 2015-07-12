import csv
import lp_maker as lpm
import lpsolve55 as lps
from argparse import ArgumentParser


DEFAULT_RANK = 0
SECTION_TO_TIMES = {
        0: "Tu/Th 9:30-11A",
        1: "Tu/Th 11-12:30P",
        2: "Tu/Th 12:30-2P",
        3: "Tu/Th 2-3:30P",
        4: "Tu/Th 3:30-5P",
        5: "Tu/Th 5-6:30P",
        6: "W/F 9:30-11A",
        7: "W/F 11-12:30P",
        8: "W/F 12:30-2P",
}
SECTION_CAPS = {
        0: 2,
        1: 4,
        2: 4,
        3: 4,
        4: 4,
        5: 4,
        6: 2,
        7: 2,
        8: 3,
}
OH_TO_TIMES = {
        0: "M 11",
        1: "M 12",
        2: "M 1",
        3: "M 3",
        4: "M 4",
        5: "T 11",
        6: "T 12",
        7: "T 1",
        8: "T 2",
        9: "T 3",
        10: "T 4",
        11: "T 5",
        12: "W 11",
        13: "W 12",
        14: "W 1",
        15: "W 3",
        16: "W 4",
        17: "Th 11",
        18: "Th 12",
        19: "Th 1",
        20: "Th 2",
        21: "Th 3",
        22: "Th 4",
        23: "Th 5",
        24: "F 11",
        25: "F 12",
        26: "F 1",
}
OH_CAPS = {time: 2 for time in OH_TO_TIMES}
for id in [24, 25, 26]:
    OH_CAPS[id] = 1
OH_CAPS[16] = 0


class TA(object):
    """
    TA's have a name, number of sections (1 or 2), and section rankings.
    """
    def __init__(self, name, sections, rankings):
        self.name = name
        self.sections = sections
        self.rankings = rankings
        self.placements = set()


def import_tas(csv_file):
    """
    Takes in a CSV file, and creates a list of TA's based on the file.

    CSV file must be of the form:
    |name| |sections| |rankings ...|
    """
    tas = set()
    with open(csv_file, 'rU') as f:
        reader = csv.reader(f)
        for row in reader:
            name = row[0]
            sections = int(row[1])
            rankings = prefs_to_rankings(row[2:])
            ta = TA(name, sections, rankings)
            tas.add(ta)
    return sorted(tas, key=lambda ta: ta.name)


def prefs_to_rankings(prefs):
    """
    Takes in a list of preferred times, outputs a list of rankings.
    """
    rankings = [DEFAULT_RANK for _ in ID_TO_TIMES]
    rank = 99
    for pref in prefs:
        if pref == '':
            continue
        pref = int(pref)
        rankings[pref] = rank
        if rank > 97:
            rank -= 1  # top three
        else:
            rank = 90  # slightly worse than top three, way better than others
    return rankings


def assign_placements():
    num_tas = len(all_tas)
    num_times = len(ID_TO_TIMES)
    upper = [1 for _ in range(num_tas * num_times)]  # max value must be 1
    obj_func = make_obj_func()
    constr_mat = make_constr_mat(num_tas, num_times)
    b_vector = make_b_vector()
    e_vector = make_e_vector(num_tas, num_times)
    lp = lpm.lp_maker(obj_func, constr_mat, b_vector, e_vector)
    lps.lpsolve('set_bb_depthlimit', lp, 0)  # set branch and bound depth limit
    lps.lpsolve('set_binary', lp, upper)  # all values must be either 0 or 1
    lps.lpsolve('solve', lp)
    vars = lps.lpsolve('get_variables', lp)[0]
    lps.lpsolve('delete_lp', lp)
    output_results(vars)


def output_results(vars):
    """
    Takes in the maximized values for the variables of the objective function,
    along with the list of relevant TA's and times.
    Outputs nothing, but prints all TA's and their placements.
    """
    i = 0
    for ta in all_tas:
        for time in ID_TO_TIMES:
            if vars[i] == 1:
                ta.placements.add(time)
                TIME_CAPS[time] -= 1
            i += 1
        assigned = ', '.join(ID_TO_TIMES[id] for id in ta.placements)
        print('{0}: {1}\n'.format(ta.name, assigned))
    print('leftover sections:\n{}'.format('\n'.join(str((ID_TO_TIMES[time], TIME_CAPS[time])) \
            for time in TIME_CAPS if TIME_CAPS[time] > 0)))


def make_obj_func():
    """
    Takes in list of TA's. Outputs a coefficient matrix of their rankings.
    """
    coeffs = []
    for ta in all_tas:
        coeffs.extend(ta.rankings)
    return coeffs


def make_constr_mat(num_tas, num_times):
    """
    Takes in the number of TA's and the number of times.
    Outputs the left side of the constraint matrix, which constrains two things:
    1. the maximum number of TA's that can be assigned to a given time
    2. the maximum number of times that can be assigned to a given TA's
    """
    coeffs = []
    for ta in range(num_tas):
        hour_coeffs = [0 for _ in range(num_tas * num_times)]
        # constraint of the form:
        # taX_time1 + taX_time2 + ... + taX_timeN <= taX.sections
        for i in range(ta * num_times, (ta+1) * num_times):
            hour_coeffs[i] = 1
        coeffs.append(hour_coeffs)
    for time in range(num_times):
        cap_coeffs = [0 for _ in range(num_tas * num_times)]
        # constraint of the form:
        # ta1_timeY + ta2_timeY + ... + taM_timeY <= TIME_CAPS[timeY]
        for i in range(time, num_tas * num_times, num_times):
            cap_coeffs[i] = 1
        coeffs.append(cap_coeffs)
    return coeffs


def make_b_vector():
    """
    Takes in a list of relevant tas and a list of relevant times.
    Outputs the right side of the constraint matrix corresponding to make_constr_mat.
    """
    return [ta.sections for ta in all_tas] + [TIME_CAPS[time] for time in ID_TO_TIMES]


def make_e_vector(num_tas, num_times):
    """
    Takes in the number of tas and the number of times.
    Outputs the vector representing the form of inequality for the constraint matrix.
    -1 is equivalent to <=
    """
    return [-1 for _ in range(num_tas + num_times)]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('csv_file', help='csv file containing TA rankings')
    parser.add_argument('-s', '--section', action='store_true', help='assign sections')
    args = parser.parse_args()
    if args.section:
        ID_TO_TIMES = SECTION_TO_TIMES
        TIME_CAPS = SECTION_CAPS
    else:
        ID_TO_TIMES = OH_TO_TIMES
        TIME_CAPS = OH_CAPS
    all_tas = import_tas(args.csv_file)
    assign_placements()

