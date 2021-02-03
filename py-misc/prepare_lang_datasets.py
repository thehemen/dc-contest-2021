import json
import tqdm
import argparse
import warnings
from polyglot.detect import Detector
from polyglot.detect.base import logger as polyglot_logger

polyglot_logger.setLevel('ERROR')

parser = argparse.ArgumentParser()
parser.add_argument('--input', default='../data/dc0202-input.txt')
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

with open(args.input, 'r') as f:
    lines = f.readlines()

tgChannels = []

for line in lines:
    json_data = json.loads(line)
    tgChannel = TgChannel(line, json_data)
    tgChannels.append(tgChannel)

outs = {'en': [], 'ru': []}

for i in tqdm.tqdm(range(len(tgChannels))):
    text = get_clean_text(repr(tgChannels[i]))
    top_language = Detector(text, quiet=True).languages[0]
    code = top_language.code
    confidence = top_language.confidence

    if code == 'en' and confidence > 90.0:
        outs[code].append(tgChannels[i].raw_data)

    elif code == 'ru' and confidence > 50.0:
        outs[code].append(tgChannels[i].raw_data)

for code, rawChannels in outs.items():
    args_input_split = args.input.split('-')
    args_input = args_input_split[0] + f'-{code}-' + args_input_split[-1]

    with open(args_input, 'a') as f:
        for rawChannel in rawChannels:
            f.write(f'{rawChannel}')
