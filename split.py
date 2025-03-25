import random

def split_arff(input_file, train_file, test_file, train_ratio=0.8):
    with open(input_file, "r") as f:
        lines = f.readlines()

    header_end_index = lines.index("@DATA\n") + 1
    header = lines[:header_end_index]
    data = lines[header_end_index:]

    random.shuffle(data)
    split_point = int(len(data) * train_ratio)

    with open(train_file, "w") as train_f:
        train_f.writelines(header + data[:split_point])

    with open(test_file, "w") as test_f:
        test_f.writelines(header + data[split_point:])

split_arff("training_keyboard.arff", "training_keyboard.arff", "test_keyboard.arff")
