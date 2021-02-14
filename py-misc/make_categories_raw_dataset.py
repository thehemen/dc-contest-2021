import argparse
from sklearn.model_selection import train_test_split

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
            data[idx] = raw_data, category

    vals = [row for _, row in sorted(data.items(), key=lambda x: x[0], reverse=False)]
    return [x[0] for x in vals], [x[1] for x in vals]

def save_dataset(x, y, dataset_name, category_name):
	with open(dataset_name, 'w') as f:
		for x_row in x:
			f.write(f'{x_row}\n')

	with open(category_name, 'w') as f:
		for i, y_row in enumerate(y):
			f.write(f'{i} {y_row}\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in_dataset_name', default='../data/en-1k-input.txt')
    parser.add_argument('--in_log_name', default='../data/en-1k-ground-truth.txt')
    parser.add_argument('--out_dataset_name', default='../data/en-1k-test-input.txt')
    parser.add_argument('--out_log_name', default='../data/en-1k-test-ground-truth.txt')
    args = parser.parse_args()

    x, y = read_dataset_with_categories(args.in_dataset_name, args.in_log_name)
    _, x_test, __, y_test = train_test_split(x, y, test_size=0.15, random_state=42)
    assert len(x_test) == len(y_test)
    save_dataset(x_test, y_test, args.out_dataset_name, args.out_log_name)
    print(f'{len(x_test)} samples saved to {args.out_dataset_name} / {args.out_log_name}.')
