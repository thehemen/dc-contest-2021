import json
import tqdm
import random
import argparse
import warnings
from polyglot.detect import Detector
from polyglot.detect.base import logger as polyglot_logger

polyglot_logger.setLevel('ERROR')

parser = argparse.ArgumentParser()
parser.add_argument('--input', default='../data/dc0202-input.txt')
parser.add_argument('--output', default='../ground_truth.json')
args = parser.parse_args()

class TgChannel:
    def __init__(self, raw_data, json_data):
        self.raw_data = raw_data
        self.title = json_data['title']
        self.description = json_data['description']
        self.recent_posts = json_data['recent_posts']

    def __repr__(self):
        representation = ''
        representation += self.title + '\n'
        representation += self.description + '\n'

        for recent_post in self.recent_posts:
            representation += recent_post

        return representation

def get_clean_text(text):
    return ''.join(x for x in text if x.isprintable())

if __name__ == '__main__':
    random.seed(42)

    with open(args.input, 'r') as f:
        lines = f.readlines()

    tgChannels = []

    for line in lines:
        json_data = json.loads(line)
        tgChannel = TgChannel(line, json_data)
        tgChannels.append(tgChannel)

    # Rewrite the file content
    with open(args.output, 'w') as f:
        pass

    for i in tqdm.tqdm(range(len(tgChannels))):
        text = get_clean_text(repr(tgChannels[i]))
        languages = Detector(text, quiet=True).languages
        code = languages[0].code
        confidence = languages[0].confidence

        # If the English score is not so high, choose another language.
        if len(languages) > 1:
            if code == 'en' and confidence < 90.0:
                code = languages[1].code

        if len(code) != 2:
            code = "other"

        with open(args.output, 'a') as f:
            json_row = json.dumps({'lang_code': code})
            f.write(f'{json_row}\n')
