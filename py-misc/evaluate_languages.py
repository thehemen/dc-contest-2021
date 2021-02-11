import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--predictions', default='../out.json')
parser.add_argument('--ground_truth', default='../ground_truth.json')
args = parser.parse_args()

def read_lang_data(filename):
    lang_codes = []

    with open(filename) as f:
        for line in f.readlines():
            json_data = json.loads(line)
            lang_codes.append(json_data['lang_code'])

    return lang_codes

class LangMetrics:
    def __init__(self, lang_code, weight):
        self.lang_code = lang_code
        self.weight = weight

        self.TP = 0
        self.FP = 0
        self.FN = 0

        self.precision = 0
        self.recall = 0
        self.F1 = 0

    def calc(self):
        self.precision = self.TP / (self.TP + self.FP + 1e-9)
        self.recall = self.TP / (self.TP + self.FN + 1e-9)
        self.F1 = 2 * self.precision * self.recall / (self.precision + self.recall + 1e-9)

if __name__ == '__main__':
    predictions = read_lang_data(args.predictions)
    ground_truth = read_lang_data(args.ground_truth)
    lang_metrics = {}

    for lang_code in set(ground_truth):
        weight = ground_truth.count(lang_code) / len(ground_truth)
        lang_metrics[lang_code] = LangMetrics(lang_code, weight)

    for gt_lang_code, pred_lang_code in zip(ground_truth, predictions):
        if gt_lang_code == pred_lang_code:
            lang_metrics[gt_lang_code].TP += 1
        else:
            lang_metrics[gt_lang_code].FN += 1

            if pred_lang_code in lang_metrics.keys():
                lang_metrics[pred_lang_code].FP += 1

    for lang_code in lang_metrics.keys():
        lang_metrics[lang_code].calc()

    micro_F1 = 0.0

    for lang_code in lang_metrics.keys():
        micro_F1 += lang_metrics[lang_code].weight * lang_metrics[lang_code].F1

    en_F1 = lang_metrics['en'].F1
    ru_F1 = lang_metrics['ru'].F1

    print(f'en-F1: {en_F1:.6f}'.replace('.', ','))
    print(f'ru-F1: {ru_F1:.6f}'.replace('.', ','))
    print(f'micro-F1: {micro_F1:.6f}'.replace('.', ','))
