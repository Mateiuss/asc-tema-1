"""
This is the module for the DataIngestor class.
The class is explained below.
"""

import csv

class DataIngestor:
    """
    This is the class that will be used to ingest the data from the CSV file and
    provide the necessary methods to get the required information.
    """
    def __init__(self, csv_path: str):
        with open(csv_path, 'r', encoding='utf-8')as file:
            csv_file = csv.DictReader(file)
            self.data = []

            for line in csv_file:
                self.data.append(line)

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity '\
            'aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic '\
            'activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity '\
            'aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic '\
            'physical activity and engage in muscle-strengthening activities on 2 '\
            'or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity '\
            'aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic '\
            'activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more '\
            'days a week',
        ]

    def state_mean(self, request_json):
        """
        Function that gets the state mean for a given state and question.
        """
        state = request_json['state']
        question = request_json['question']
        state_data = [row for row in self.data if row['LocationDesc'] == state and
                       row['Question'] == question]

        if len(state_data) == 0:
            return None

        return {state: sum((float(row['Data_Value']) for row in state_data)) / len(state_data)}

    def states_mean(self, request_json):
        """
        Function that gets the mean of all states for a given question.
        """
        question = request_json['question']
        states = {row['LocationDesc'] for row in self.data if row['Question'] == question}

        states_mean = {}

        for state in states:
            request = {'state': state, 'question': question}

            state_mean = self.state_mean(request)
            states_mean.update(state_mean)

        return states_mean

    def best5(self, request_json):
        """
        Function that gets the best 5 states for a given question.
        """
        question = request_json['question']
        best_is_max = question in self.questions_best_is_max

        states_mean = self.states_mean(request_json)
        sorted_states = sorted(states_mean.items(), key=lambda x: x[1], reverse=best_is_max)

        return dict(sorted_states[:5])

    def worst5(self, request_json):
        """
        Functions that gets the worst 5 states for a given question.
        """
        question = request_json['question']
        best_is_min = question in self.questions_best_is_min

        states_mean = self.states_mean(request_json)
        sorted_states = sorted(states_mean.items(), key=lambda x: x[1], reverse=best_is_min)

        return dict(sorted_states[:5])

    def global_mean(self, request_json):
        """
        Function that gets the global mean for a given question.
        """
        question = request_json['question']
        question_data = [row for row in self.data if row['Question'] == question]

        if len(question_data) == 0:
            return None

        return {'global_mean': sum((float(row['Data_Value'])
                                    for row in question_data)) / len(question_data)}

    def state_diff_from_mean(self, request_json):
        """
        Function that gets the difference between the global mean and the state mean for a given
        state and question.
        """
        question = request_json['question']
        state = request_json['state']

        global_mean = self.global_mean({'question': question})
        global_mean = global_mean['global_mean']

        state_mean = self.state_mean({'state': state, 'question': question})
        state_mean = state_mean[state]

        return {state: global_mean - state_mean}

    def diff_from_mean(self, request_json):
        """
        Function that gets the difference between the global mean and the state mean on a given
        question for all states.
        """
        question = request_json['question']
        global_mean = self.global_mean({'question': question})
        global_mean = global_mean['global_mean']

        states_mean = self.states_mean({'question': question})

        return {state: global_mean - state_mean for state, state_mean in states_mean.items()}

    def state_mean_by_category(self, request_json):
        """
        Function that gets the mean of state for a given question and state by category.
        """
        question = request_json['question']
        state = request_json['state']

        stratification_categories = {}

        for row in self.data:
            if row['Question'] == question and row['LocationDesc'] == state:
                category = row['StratificationCategory1']

                if category == '':
                    continue

                if category not in stratification_categories:
                    stratification_categories[category] = {}

                stratification = row['Stratification1']

                if stratification not in stratification_categories[category]:
                    stratification_categories[category][stratification] = [row['Data_Value']]
                else:
                    stratification_categories[category][stratification].append(row['Data_Value'])

        for (category, value) in stratification_categories.items():
            for stratification in value:
                value[stratification] =\
                sum((float(x) for x in value[stratification])) / len(value[stratification])

        ans = {}

        for (category, value) in stratification_categories.items():
            for stratification in value:
                ans[(category, stratification)] = value[stratification]

        return {state: ans}

    def mean_by_category(self, request_json):
        """
        Function that gets the mean of all states for a given question by category.
        """
        question = request_json['question']
        states = {row['LocationDesc'] for row in self.data if row['Question'] == question}

        ans = {}

        for state in states:
            request = {'state': state, 'question': question}
            state_mean_by_category = self.state_mean_by_category(request)

            for (category, stratification), value in state_mean_by_category[state].items():
                ans[(state, category, stratification)] = value

        return ans
