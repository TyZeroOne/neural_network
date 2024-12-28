import numpy as np
import sys

def parse_arguments():
    args = sys.argv[1:]
    params = {
        "input1": "input1.txt", 
        "output1": "output1.txt", 
        "input2": "input2.txt", 
        "output2": "output2.txt", 
        "epoch": 10000
    }
    for arg in args:
        key, _, value = arg.partition("=")
        if key in params:
            params[key] = value.strip()
    return params

def write_error(message):
    with open("error.txt", 'w', encoding="utf-8") as file:
        file.write(message)

def read_matrix(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        processed_data = []
        for line in lines:
            line = line.strip()
            if line:
                arrays = line.strip("[]").split("] [")
                layer = []
                for array in arrays:
                    values = [float(value) for value in array.split()]
                    layer.append(values)
                processed_data.append(np.array(layer))
        return processed_data
    except FileNotFoundError:
        write_error(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit()
    except ValueError as e:
        write_error(f"Ошибка: Не удалось преобразовать данные в числа. Проверьте содержимое файла. {e}")
        sys.exit()
    except Exception as e:
        write_error(f"Ошибка при чтении файла: {e}")
        sys.exit()

def load_training_data(file_path):
    try:
        inputs, outputs = [], []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.strip("[]").split("] [")
                    input_values = [float(x) for x in parts[0].split()]
                    output_values = [int(x) for x in parts[1].split()]
                    inputs.append(input_values)
                    outputs.append(output_values)
        return np.array(inputs), np.array(outputs)
    except FileNotFoundError:
        write_error(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit()
    except ValueError as e:
        write_error(f"Ошибка: Не удалось преобразовать данные в числа. Проверьте содержимое файла. {e}")
        sys.exit()
    except Exception as e:
        write_error(f"Ошибка при чтении файла: {e}")
        sys.exit()

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    return sigmoid(x) * (1 - sigmoid(x))

def forward_pass(weights, inputs):

    activations = [inputs]
    for layer in weights:
        inputs = sigmoid(np.dot(inputs, layer.T))
        activations.append(inputs)
    return activations

def backward_pass(weights, activations, targets, learning_rate):

    errors = [activations[-1] - targets]
    deltas = [errors[-1] * sigmoid_derivative(activations[-1])]
    
    for i in range(len(weights) - 1, 0, -1):
        error = np.dot(deltas[-1], weights[i])
        delta = error * sigmoid_derivative(activations[i])
        deltas.append(delta)
    deltas.reverse()
    
    for i in range(len(weights)):
        gradient = np.dot(deltas[i].T, activations[i])
        weights[i] -= learning_rate * gradient
    
    return weights

def calculate(matrix, vector):

    output_by_layer = []

    for layer_weights in matrix:
        if layer_weights.shape[1] != vector.shape[0]:
            write_error(
                f"Ошибка: Несоответствие размерностей. "
                f"Ожидалось: {layer_weights.shape[1]}, получили: {vector.shape[0]}"
            )
            sys.exit()

        vector = sigmoid(np.dot(layer_weights, vector))
        output_by_layer.append(vector)

    return output_by_layer[-1] if output_by_layer else np.array([])

def train_network(
        input_path1, 
        input_path2, 
        history_file,
        results_file, 
        epochs,
        learning_rate=0.1, 
    ):

    weights = read_matrix(input_path1)
    inputs, targets = load_training_data(input_path2)
    
    initial_results = [calculate(weights, x) for x in inputs]

    try:
        with open(results_file, 'w', encoding='utf-8') as file:
            file.write("Начальные результаты:\n")
            for i, res in enumerate(initial_results):
                file.write(f"Пример {i + 1}: {res}\n")
        print(f"Начальные результаты записаны в файл: {results_file}")
    except Exception as e:
        print(f"Ошибка при записи начальных результатов: {e}")

    history = []

    for epoch in range(epochs):
        activations = forward_pass(weights, inputs)

        outputs = activations[-1]  

        error = np.mean((outputs - targets) ** 2)
        history.append(f"Эпоха {epoch + 1}: ошибка = {error}")

        weights = backward_pass(
            weights, 
            activations, 
            targets, 
            learning_rate
        )

    try:
        with open(history_file, 'w', encoding='utf-8') as file:
            file.write("\n".join(history))
        print(f"История обучения сохранена в файл: {history_file}")
    except Exception as e:
        print(f"Ошибка при записи истории обучения: {e}")

    final_results = [calculate(weights, x) for x in inputs]

    try:
        with open(results_file, 'a', encoding='utf-8') as file:
            file.write("\nФинальные результаты:\n")
            for i, res in enumerate(final_results):
                file.write(f"Пример {i + 1}: {res}\n")
        print(f"Финальные результаты записаны в файл: {results_file}")
    except Exception as e:
        print(f"Ошибка при записи конечных результатов: {e}")

    return weights

def main():
    params = parse_arguments()

    try:
        train_network(
            params["input1"], 
            params["input2"], 
            params["output1"], 
            params["output2"], 
            epochs=int(params["epoch"]),
            learning_rate=0.5
        )
    except Exception as e:
        write_error(f"Ошибка: {e}")

if __name__ == "__main__":
    main()