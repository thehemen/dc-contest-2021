import argparse

def read_dataset_with_logs(dataset_name, log_name):
    data = {}

    with open(dataset_name, 'r') as f:
        dataset_rows = f.readlines()

    with open(log_name, 'r') as f:
        for line in f.readlines():
            idx = int(line.split(' ')[0])
            category = ' '.join([x for x in line.split(' ')[1:]])[:-1]

            if category == 'Othe':
                category = 'Other'

            dataset_row = dataset_rows[idx][:-1]
            data[idx] = dataset_row, category

    return [row for _, row in sorted(data.items(), key=lambda x: x[0], reverse=False)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name_first', default='../data/dc0202-en-input.txt')
    parser.add_argument('--dataset_name_second', default='../data/dc0206-en-input.txt')
    parser.add_argument('--log_name_first', default='../data/dc0202-en-ground-truth.txt')
    parser.add_argument('--log_name_second', default='../data/dc0206-en-ground-truth.txt')
    parser.add_argument('--out_dataset_name', default='../data/en-1k-input.txt')
    parser.add_argument('--out_log_name', default='../data/en-1k-ground-truth.txt')
    args = parser.parse_args()

    data = read_dataset_with_logs(args.dataset_name_first, args.log_name_first)
    data.extend(read_dataset_with_logs(args.dataset_name_second, args.log_name_second))

    index = 0

    with open(args.out_dataset_name, 'w') as f_dataset:
        with open(args.out_log_name, 'w') as f_log:
            for dataset_row, category in data:
                f_dataset.write(f'{dataset_row}\n')
                f_log.write(f'{index} {category}\n')
                index += 1
