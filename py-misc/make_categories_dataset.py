import re
import tqdm
import json
import argparse
import pymorphy2
from sklearn.model_selection import train_test_split

def is_cyrillic(c, with_cyrillic):
    return ((c >= 'а' and c <= 'я') or (c >= 'А' and c <= 'Я')) and with_cyrillic == 1

def is_latin(c):
    return ((c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z'))

def get_clean_text(text, with_cyrillic):
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = text.replace('\n', ' ')
    text = ''.join(x for x in text if x.isprintable())
    text = ''.join(x.lower() for x in text if is_cyrillic(x, with_cyrillic) or is_latin(x) or x == ' ')
    text = re.sub(' +', ' ', text)  # Remove repeating whitespaces
    return text

class TgChannel:
    def __init__(self, raw_data, json_data):
        self.raw_data = raw_data
        self.title = json_data['title']
        self.description = json_data['description']
        self.recent_posts = json_data['recent_posts']

        self.category = 'Other'

    def __repr__(self):
        representation = ''
        representation += self.title + ' '
        representation += self.description + ' '

        for recent_post in self.recent_posts:
            representation += recent_post

        return representation

def read_dataset_with_categories(dataset_name, category_name):
    data = {}

    with open(dataset_name, 'r') as f:
        dataset_rows = f.readlines()

    with open(category_name, 'r') as f:
        for line in f.readlines():
            idx = int(line.split(' ')[0])
            category = ' '.join([x for x in line.split(' ')[1:]])[:-1]

            if category == 'Othe':
                category = 'Other'

            raw_data = dataset_rows[idx][:-1]
            json_data = json.loads(raw_data)
            tgChannel = TgChannel(raw_data, json_data)

            # Add prefix to fit FastText format and replace spaces with underscores
            tgChannel.category = '__label__' + category.replace(' ', '_')
            data[idx] = tgChannel

    return [row for _, row in sorted(data.items(), key=lambda x: x[0], reverse=False)]

def get_texts_with_labels(dataset, with_cyrillic, morph_analyzer=None):
    x, y = [], []

    for i in tqdm.tqdm(range(len(dataset))):
        row = dataset[i]
        text = repr(row)
        text = get_clean_text(text, with_cyrillic)

        if morph_analyzer is not None:
            words = []

            for word in text.split(' '):
                word_normalized = morph.parse(word)[0].normal_form
                words.append(word_normalized)

            text = ' '.join(words)

        x.append(text)
        y.append(row.category)

    return x, y

def save_dataset(filename, x, y):
    with open(filename, 'w') as f:
        for x_sample, y_sample in zip(x, y):
            f.write(f'{y_sample} {x_sample}\n')

    print(f'{len(x)} samples saved to {filename}.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', default='../data/dc0202-ru-input.txt')
    parser.add_argument('--log_name', default='../data/dc0202-ru-ground-truth.txt')
    parser.add_argument('--with_cyrillic', type=int, default=1)
    parser.add_argument('--with_lemmatization', type=int, default=0)
    parser.add_argument('--out_train_name', default='../../fastText/data/ru-1k-train.txt')
    parser.add_argument('--out_test_name', default='../../fastText/data/ru-1k-test.txt')
    args = parser.parse_args()

    if args.with_cyrillic == 1 and args.with_lemmatization == 1:
        morph = pymorphy2.MorphAnalyzer()
    else:
        morph = None

    dataset = read_dataset_with_categories(args.dataset_name, args.log_name)
    x, y = get_texts_with_labels(dataset, args.with_cyrillic, morph)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15, random_state=42)
    save_dataset(args.out_train_name, x_train, y_train)
    save_dataset(args.out_test_name, x_test, y_test)
