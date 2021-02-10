import json
import argparse
import matplotlib.pyplot as plt

if __name__ == '__main__':
    with open('categories.json', 'r') as f:
        category_dict = json.load(f)

    parser = argparse.ArgumentParser()
    parser.add_argument('--log_name', default='../data/en-1k-ground-truth.txt')
    args = parser.parse_args()

    category_by_idx = {}

    with open(args.log_name, 'r') as f:
        for line in f.readlines():
            idx = int(line.split(' ')[0])
            category = ' '.join([x for x in line.split(' ')[1:]])[:-1]

            if category == 'Othe':
                category = 'Other'

            category_by_idx[idx] = category

    category_count = {}

    for meta_category, categories in category_dict.items():
        for category in categories:
            category_count[category] = 0

    for idx, category in category_by_idx.items():
        category_count[category] += 1

    x = []
    y = []

    for category, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        print(f'{count} ({(count / len(category_by_idx)) * 100.0:.2f} %) {category}')
        x.append(category)
        y.append(count)

    fig, ax = plt.subplots()
    ax.barh(x, y)
    ax.set_title(args.log_name.split('/')[-1])
    ax.set_xlim([0, 200])
    plt.show()
