import unittest
from deepdiff import DeepDiff
import app

class TestWebserver(unittest.TestCase):
    def setUp(self):
        # create a data_ingestor on the test csv file
        self.data_ingestor = app.data_ingestor.DataIngestor("unittests/nutrition_unittest.csv")

        # Shutdown the thread pool so that we can test only the functionality
        app.webserver.tasks_runner.close()

    def test_states_mean(self):
        request_json = {'question': 'Percent of adults who engage in no leisure-time physical activity'}
        res = self.data_ingestor.states_mean(request_json)

        expected = {'Nebraska': 31.5, 'Wisconsin': 24.0, 'Kansas': 28.7, 'Ohio': 31.6, 'Maryland': 32.85}
        
        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_mean(self):
        request_json = {'question': 'Percent of adults who engage in no leisure-time physical activity', 'state': 'Maryland'}
        res = self.data_ingestor.state_mean(request_json)

        expected = {'Maryland': 32.85}
        
        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_best5(self):
        request_json = {'question': 'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week'}
        res = self.data_ingestor.best5(request_json)

        expected = {'Washington': 40.3, 'New Hampshire': 35.3, 'Massachusetts': 31.4, 'Kansas': 24.75, 'Rhode Island': 19.7}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_worst5(self):
        request_json = {'question': 'Percent of adults who engage in no leisure-time physical activity'}
        res = self.data_ingestor.worst5(request_json)

        expected = {'Maryland': 32.85, 'Ohio': 31.6, 'Nebraska': 31.5, 'Kansas': 28.7, 'Wisconsin': 24.0}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_global_mean(self):
        request_json = {'question': 'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week'}
        res = self.data_ingestor.global_mean(request_json)

        expected = {'global_mean': 30.28}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_diff_from_mean(self):
        request_json = {'question': 'Percent of adults aged 18 years and older who have obesity'}
        res = self.data_ingestor.diff_from_mean(request_json)

        expected = {'Ohio': -0.85, 'New Mexico': 0.84999999999999}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_diff_from_mean(self):
        request_json = {
            'question': 'Percent of adults aged 18 years and older who have obesity',
            'state': 'Ohio'
        }
        res = self.data_ingestor.state_diff_from_mean(request_json)

        expected = {'Ohio': -0.85}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_mean_by_category(self):
        request_json = {'question': 'Percent of adults who engage in muscle-strengthening activities on 2 or more days a week'}
        res = self.data_ingestor.mean_by_category(request_json)

        expected = {
            ('Kansas', 'Gender', 'Female'): 24.75,
            ('Massachusetts', 'Age (years)', '35 - 44'): 31.4,
            ('Rhode Island', 'Income', 'Less than $15,000'): 19.7,
            ('New Hampshire', 'Gender', 'Female'): 35.3,
            ('Washington', 'Income', '$75,000 or greater'): 40.3
        }

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))

    def test_state_mean_by_category(self):
        request_json = {
            'question': 'Percent of adults aged 18 years and older who have obesity',
            'state': 'Ohio'
        }
        res = self.data_ingestor.state_mean_by_category(request_json)

        expected = {'Ohio': {('Income', '$75,000 or greater'): 29.4}}

        d = DeepDiff(res, expected, math_epsilon=0.01)
        self.assertTrue(d == {}, str(d))


if __name__ == '__main__':
    unittest.main()
