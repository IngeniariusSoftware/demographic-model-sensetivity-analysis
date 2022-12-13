import numpy
import numpy as np
import pandas as pd
from tqdm import tqdm
from ast import literal_eval
from SALib.analyze import sobol
from SALib.sample import saltelli

ages = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64',
        '65-69', '70-74', '75-79', '80-84', '85-89', '90-94', '95-99', '100+']

fertility_groups_count = 4.0

survival_changed_variables_indexes = [0, 2, 5, 7, 10]
changed_variables_indexes = [0, 1] + list(map(lambda x: x + 2, survival_changed_variables_indexes)) + list(
    map(lambda x: x + 22, survival_changed_variables_indexes))
survival_unchanged_variables_indexes = set(range(0, 20)) - set(survival_changed_variables_indexes)

start_year = 2021
step_year = 5
steps = [1, 3, 9, 19]


def model(women, female_birth_rate, female_survival_rates, men, male_birth_rate, male_survival_rates, steps_number):
    women = list(women)
    men = list(men)
    result = []
    step = 0
    while step < steps_number:
        population = 0
        i = len(women) - 1
        fertility_women = women[4] + women[5] + women[6] + women[7]

        while i > -1:
            survived_women = women[i - 1] * female_survival_rates[i - 1]
            women[i] = survived_women
            population += survived_women

            survived_men = men[i - 1] * male_survival_rates[i - 1]
            men[i] = survived_men
            population += survived_men

            i -= 1

        female_children = fertility_women * female_birth_rate
        women[0] = female_children
        population += female_children

        male_children = fertility_women * male_birth_rate
        men[0] = male_children
        population += male_children

        result.append(population)
        step += 1

    return result


def model_facade(fertility, female_percentage, women, female_survival_rates, men, male_survival_rates, steps_number):
    fertility /= fertility_groups_count
    women_birth_rate = fertility * female_percentage
    men_birth_rate = fertility * (1.0 - female_percentage)
    return model(women, women_birth_rate, female_survival_rates, men, men_birth_rate, male_survival_rates, steps_number)


def evaluate(data, params_list):
    last_women = list(data.iloc[0])
    women = list(data.iloc[2])
    last_men = list(data.iloc[1])
    men = list(data.iloc[3])
    result = [[], [], [], []]
    survival_rates = [[], []]
    for i in range(len(women) - 1):
        if last_women[i] == 0:
            last_women[i] = 1
        survival_rates[0].append(women[i + 1] / last_women[i])
        if last_men[i] == 0:
            last_men[i] = 1
        survival_rates[1].append(men[i + 1] / last_men[i])

    for params in params_list:
        fertility = params[0]
        female_percentage = params[1]
        for i, j in enumerate([0, 2, 5, 7, 10]):
            survival_rates[0][j] = params[2 + i]
            survival_rates[1][j] = params[7 + i]

        population = model_facade(fertility, female_percentage, women, survival_rates[0], men, survival_rates[1], 20)
        result[0].append(population[1])
        result[1].append(population[3])
        result[2].append(population[9])
        result[3].append(population[19])

    return [np.array(result[0]), np.array(result[1]), np.array(result[2]), np.array(result[3])]


def evaluate_range(data, params_list):
    last_women = list(data.iloc[0])
    women = list(data.iloc[2])
    last_men = list(data.iloc[1])
    men = list(data.iloc[3])
    result = [[], [], [], []]
    survival_rates = [[0.0] * 20, [0.0] * 20]
    for i in range(len(women) - 1):
        survival_rates[0].append(women[i + 1] / last_women[i])
        survival_rates[1].append(men[i + 1] / last_men[i])

    min_population = None
    max_population = None
    for params in params_list:
        fertility = params[0]
        female_percentage = params[1]
        for i, j in enumerate(survival_changed_variables_indexes):
            print(i, j)

        # for i, j in enumerate(range(20)):
        #     survival_rates[0][j] = params[2 + i]
        #     survival_rates[1][j] = params[22 + i]

        population = model_facade(fertility, female_percentage, women, survival_rates[0], men, survival_rates[1], 15)
        if min_population is None or min_population[-1] > population[-1]:
            min_population = population

        if max_population is None or max_population[-1] < population[-1]:
            max_population = population

    return min_population, max_population


def test():
    population = [
        [4609465, 4024755, 3533982, 3260485, 3987011, 5958673, 6145860, 5605733, 5288769, 4750801, 5382475, 6114708,
         5498509, 4481741, 2180709, 3522448, 1818669, 1205980, 365890, 46189, 6288],
        [4872040, 4232445, 3702589, 3419312, 4163057, 6125318, 6147438, 5430433, 4945739, 4376376, 4634895, 4859152,
         3865909, 2802033, 1149423, 1493858, 661974, 357454, 70912, 8464, 1204],
        [3836611, 4635743, 4041370, 3591364, 3401107, 4145188, 6068610, 6198024, 5610823, 5257968, 4686765, 5247889,
         5866238, 5099956, 3963419, 1799526, 2555100, 1065362, 522047, 108310, 8684],
        [4053692, 4896880, 4247345, 3751083, 3538361, 4290943, 6175349, 6111248, 5318361, 4778909, 4155226, 4273108,
         4298075, 3186549, 2151705, 804388, 889007, 320190, 130678, 19652, 1914]]

    fertility_women = population[2][4] + population[2][5] + population[2][6] + population[2][7]
    birt_rates = [population[2][0] / fertility_women, population[3][0] / fertility_women]
    survival_rates = [[], []]
    for i in range(len(population[0]) - 1):
        survival_rates[0].append(population[2][i + 1] / population[0][i])
        survival_rates[1].append(population[3][i + 1] / population[1][i])

    result = model(population[2], birt_rates[0], survival_rates[0], population[3], birt_rates[1], survival_rates[1], 20)

    if result[0] != 144491868 or result[-1] != 97305749:
        raise Exception(f'{result[0]} != 144491868 and {result[-1]} != 97305749')


def get_range(x):
    result = literal_eval(x)
    if result[0] >= result[1]:
        result[1] += 0.0000001
    return result


def main():
    numpy.set_printoptions(precision=4, suppress=True, linewidth=np.inf)
    countries_ranges = pd.read_csv('countries_ranges.csv', sep=',')
    countries_for_prediction = pd.read_csv('countries_for_prediction.csv', sep=',').drop(labels=['year', 'sex'], axis=1)
    result = pd.DataFrame()
    names = ['fertility', 'female_percentage', '0-4_female', '10-14_female', '25-29_female', '35-39_female',
             '50-54_female', '0-4_male', '10-14_male', '25-29_male', '35-39_male', '50-54_male']

    result = ['country,year,min,max\n']
    for (_, row) in countries_ranges.iterrows():
        country = row['country']
        row = row.drop(labels='country')
        problem = {
            'num_vars': 12,
            'bounds': list(map(lambda x: get_range(x), list(row[names])))
        }

        data = countries_for_prediction.loc[countries_for_prediction['country'] == country]
        data = data.drop(labels='country', axis=1).reset_index(drop=True)

        # min_population, max_population = evaluate_range(data, params)
        # result.append(
        #     f'{country},{2021},{sum(list(data.iloc[2])) + sum(list(data.iloc[3]))},{sum(list(data.iloc[2])) + sum(list(data.iloc[3]))}\n')
        # for i in range(len(min_population)):
        #     result.append(f'{country},{2026 + (i * 5)},{round(min_population[i])},{round(max_population[i])}\n')


        params = saltelli.sample(problem, 2 ** 11)
        evaluated = evaluate(data, params)

        print(country)
        print(f'normal fertility: {numpy.array(problem["bounds"][0])}')
        print(names)
        for i, year in enumerate([10, 20, 50, 100]):
            print(f'{year} years:', sobol.analyze(problem, evaluated[i])['S1'])
            # analysis = pd.DataFrame([analysis], columns=problem['names'])
            # analysis.insert(0, 'country', country)
            # analysis.insert(1, 'years', (steps[i] + 1) * step_year)
            # result = pd.concat([result, analysis])

        fertility = problem['bounds'][0]
        fertility_range = fertility[1] - fertility[0]
        coeff = 0.25

        problem['bounds'][0] = [fertility[0] + (fertility_range * coeff), fertility[1] - (fertility_range * coeff)]

        params = saltelli.sample(problem, 2 ** 11)
        evaluated = evaluate(data, params)
        print(f'\ndecreased fertility: {numpy.array(problem["bounds"][0])}')
        print(names)
        for i, year in enumerate([10, 20, 50, 100]):
            print(f'{year} years:', sobol.analyze(problem, evaluated[i])['S1'])

        print('_________________________________________________')

    with open('min_max_population.csv', 'w', encoding='UTF-8') as f:
        f.writelines(result)


main()
