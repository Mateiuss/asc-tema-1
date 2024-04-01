import csv

class DataIngestor:
    def __init__(self, csv_path: str):
        # TODO: Read csv from csv_path
        with open(csv_path, 'r')as file:
            csvFile = csv.DictReader(file)
            self.data = []

            for line in csvFile:
                self.data.append(line)

        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity aerobic physical activity or 75 minutes a week of vigorous-intensity aerobic physical activity and engage in muscle-strengthening activities on 2 or more days a week',
            'Percent of adults who achieve at least 300 minutes a week of moderate-intensity aerobic physical activity or 150 minutes a week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week',
        ]

    def state_mean(self, request_json):
        state = request_json['state']
        question = request_json['question']
        state_data = [row for row in self.data if row['LocationDesc'] == state and row['Question'] == question]

        if len(state_data) == 0:
            return None
        
        return {state: sum([float(row['Data_Value']) for row in state_data]) / len(state_data)}
    
    def states_mean(self, request_json):
        question = request_json['question']
        states = set([row['LocationDesc'] for row in self.data if row['Question'] == question])

        states_mean = {}

        for state in states:
            request = {'state': state, 'question': question}

            state_mean = self.state_mean(request)
            states_mean.update(state_mean)

        return states_mean

    def best5(self, request_json):
        question = request_json['question']
        best_is_max = question in self.questions_best_is_max
        
        states_mean = self.states_mean(request_json)
        sorted_states = sorted(states_mean.items(), key=lambda x: x[1], reverse=best_is_max)

        return dict(sorted_states[:5])
    
    def worst5(self, request_json):
        question = request_json['question']
        best_is_min = question in self.questions_best_is_min
        
        states_mean = self.states_mean(request_json)
        sorted_states = sorted(states_mean.items(), key=lambda x: x[1], reverse=best_is_min)

        return dict(sorted_states[:5])
    
    def global_mean(self, request_json):
        question = request_json['question']
        question_data = [row for row in self.data if row['Question'] == question]

        if len(question_data) == 0:
            return None
        
        return {'global_mean': sum([float(row['Data_Value']) for row in question_data]) / len(question_data)}
    
    def state_diff_from_mean(self, request_json):
        question = request_json['question']
        state = request_json['state']

        global_mean = self.global_mean({'question': question})
        global_mean = global_mean['global_mean']

        state_mean = self.state_mean({'state': state, 'question': question})
        state_mean = state_mean[state]

        return {state: global_mean - state_mean}
    
    def diff_from_mean(self, request_json):
        question = request_json['question']
        global_mean = self.global_mean({'question': question})
        global_mean = global_mean['global_mean']

        states_mean = self.states_mean({'question': question})

        return {state: global_mean - state_mean for state, state_mean in states_mean.items()}

    def state_mean_by_category(self, request_json):
        question = request_json['question']
        state = request_json['state']

        stratification_categories = {}
        ans = {}

        for row in self.data:
            if row['Question'] == question and row['LocationDesc'] == state:
                category = row['StratificationCategory1']

                if category == '':
                    print('Category i   s empty')
                    ans[('', '')] = row['Data_Value']
                    continue

                if category not in stratification_categories:
                    stratification_categories[category] = {}

                stratification = row['Stratification1']

                if stratification not in stratification_categories[category]:
                    stratification_categories[category][stratification] = [row['Data_Value']]
                else:
                    stratification_categories[category][stratification].append(row['Data_Value'])

        for category in stratification_categories:
            for stratification in stratification_categories[category]:
                stratification_categories[category][stratification] = sum([float(x) for x in stratification_categories[category][stratification]]) / len(stratification_categories[category][stratification])

        for category in stratification_categories:
            for stratification in stratification_categories[category]:
                ans[(category, stratification)] = stratification_categories[category][stratification]

        return {state: ans}
    
    def mean_by_category(self, request_json):
        question = request_json['question']
        states = set([row['LocationDesc'] for row in self.data if row['Question'] == question])

        ans = {}

        for state in states:
            request = {'state': state, 'question': question}
            state_mean_by_category = self.state_mean_by_category(request)
            
            for (category, stratification), value in state_mean_by_category[state].items():
                ans[(state, category, stratification)] = value

        return ans
