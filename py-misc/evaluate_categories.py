import json
import argparse
from sklearn.metrics import log_loss

class CategoryPrediction:
    def __init__(self, lang_code, category):
        self.lang_code = lang_code
        self.category = category

    def get_top_1(self):
        return max(self.category, key=self.category.get)

def read_category_predictions(filename):
    replace_categories = {'Foreign Language Learning': 'Foreign Languages',
                          'Motivation & Self-development': 'Motivation & Self-Development'}

    categoryPredictions = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            json_data = json.loads(line)
            lang_code = json_data['lang_code']
            category = json_data['category']

            # Replace tgcat-tester's broken categories.
            if len(category) > 0:
                for replace_from, replace_to in replace_categories.items():
                    category[replace_to] = category[replace_from]
                    del category[replace_from]

            categoryPrediction = CategoryPrediction(lang_code, category)
            categoryPredictions.append(categoryPrediction)

    return categoryPredictions

def read_category_ground_truth(filename):
    categoriesGroundTruth = []

    with open(filename, 'r') as f:
        for line in f.readlines():
            category = ' '.join(line.split(' ')[1:])[:-1]
            categoriesGroundTruth.append(category)

    return categoriesGroundTruth

def get_log_loss(prediction_dict, category_gt):
    category_gt_dict = {category: 0 for category in prediction_dict.keys()}
    category_gt_dict[category_gt] = 1.0

    if category_gt not in prediction_dict.keys():
        print(category_gt)
        print(prediction_dict.keys())

    y_pred = []
    y_true = []

    for category_name in prediction_dict.keys():
        y_pred.append(prediction_dict[category_name])
        y_true.append(category_gt_dict[category_name])

    return log_loss(y_true, y_pred)

def get_fake_log_loss(num):
    y_pred = [0.0 for i in range(num)]
    y_true = [0.0 for i in range(num)]
    y_true[0] = 1.0
    return log_loss(y_true, y_pred)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang_code', default='en')
    parser.add_argument('--predictions', default='../out/en-1k-test-out.json')
    parser.add_argument('--ground_truth', default='../data/en-1k-test-ground-truth.txt')
    args = parser.parse_args()

    categoryPredictions = read_category_predictions(args.predictions)
    categoriesGroundTruth = read_category_ground_truth(args.ground_truth)

    category_num = len(categoryPredictions[0].category)
    print(f'Categories: {category_num}')

    fake_loss = get_fake_log_loss(category_num)

    assert len(categoryPredictions) == len(categoriesGroundTruth)
    pred_num = len(categoryPredictions)
    print(f'Test Predictions: {pred_num}')

    unique_len = len(set(categoriesGroundTruth))
    print(f'Unique ground truth categories: {unique_len}')

    success_num = 0
    log_loss_mean = 0.0

    for categoryPredicted, categoryGroundTruth in zip(categoryPredictions, categoriesGroundTruth):
        if categoryPredicted.lang_code == args.lang_code:
            log_loss_value = get_log_loss(categoryPredicted.category, categoryGroundTruth)
            categoryPredictedName = categoryPredicted.get_top_1()
            is_equal = categoryPredictedName == categoryGroundTruth

            if is_equal:
                success_num += 1
        else:
            log_loss_value = fake_loss

        log_loss_mean += log_loss_value / pred_num

    precision_at_1 = success_num / pred_num
    print(f'Precision-at-1: {precision_at_1:.6f}')
    print(f'Log Loss Score: {log_loss_mean:.6f}')
