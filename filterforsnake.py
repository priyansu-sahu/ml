
def filter_arff(input_file, output_file, selected_indices, selected_header):
    with open(input_file, "r") as f_in:
        lines = f_in.readlines()

    data_index = 0
    for i, line in enumerate(lines):
        if line.strip().upper() == "@DATA":
            data_index = i + 1
            break

    data_lines = lines[data_index:]

    with open(output_file, "w") as f_out:
        f_out.write(selected_header + "\n")
        for line in data_lines:
            if line.strip() == "":
                continue
            parts = [part.strip() for part in line.split(",")]
            filtered_parts = [parts[i] for i in selected_indices]
            f_out.write(", ".join(filtered_parts) + "\n")

# Header without STRING attributes for broad classifier compatibility
FILTER_HEADER_CLASSIFICATION = """@RELATION snake_game_classification

@ATTRIBUTE snake_head_x NUMERIC
@ATTRIBUTE snake_head_y NUMERIC
@ATTRIBUTE food_x NUMERIC
@ATTRIBUTE food_y NUMERIC
@ATTRIBUTE snake_len NUMERIC
@ATTRIBUTE current_score NUMERIC
@ATTRIBUTE action {UP,DOWN,LEFT,RIGHT}

@DATA
"""

# Generate filtered training file
filter_arff("training_keyboard.arff", "training_keyboard_filtered.arff",
            [0, 1, 2, 3, 4, 7, 8], FILTER_HEADER_CLASSIFICATION)

# Generate filtered test file
filter_arff("test_keyboard.arff", "test_keyboard_filtered.arff",
            [0, 1, 2, 3, 4, 7, 8], FILTER_HEADER_CLASSIFICATION)

