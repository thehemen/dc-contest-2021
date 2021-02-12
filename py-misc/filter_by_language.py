import json
import argparse

def read_file(filename):
    with open(filename, 'r') as f:
        return [x[:-1] for x in f.readlines()]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', default='../data/dc0202-input.txt')
    parser.add_argument('--prediction_name', default='../out.json')
    parser.add_argument('--language', default='en')
    parser.add_argument('--out_name', default='../out_filtered.txt')
    args = parser.parse_args()

    dataset_rows = read_file(args.dataset_name)
    prediction_rows = read_file(args.prediction_name)
    filtered_rows = []

    for dataset_row, prediction_row in zip(dataset_rows, prediction_rows):
        lang_code = json.loads(prediction_row)['lang_code']

        if lang_code == args.language:
            filtered_rows.append(dataset_row)

    with open(args.out_name, 'w') as f:
        for filtered_row in filtered_rows:
            f.write(f'{filtered_row}\n')

    print(f'{len(filtered_rows)} rows are saved to {args.out_name}.')
