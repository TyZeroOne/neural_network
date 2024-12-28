import sys
import xml.etree.ElementTree as ET
import numpy as np
import math

def parse_arguments():
    args = sys.argv[1:]
    params = {"input1": "input1.txt", "output1": "output1.xml", "input2": "input2.txt", "output2": "output2.txt"}
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
                int_arrays = []
                for array in arrays:
                    int_values = [float(value) for value in array.split()]
                    int_arrays.append(int_values)
                processed_data.append(int_arrays)
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

def read_vector(file_path):
    try:
        with open(file_path, 'r') as file:
            line = file.readline().strip()
            numbers = [float(num) for num in line.split()]
        return numbers
    except FileNotFoundError:
        write_error(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit()
    except ValueError as e:
        write_error(f"Ошибка: Не удалось преобразовать данные в числа. Проверьте содержимое файла. {e}")
        sys.exit()
    except Exception as e:
        write_error(f"Ошибка при чтении файла: {e}")
        sys.exit()

def serialize_to_xml(data, output_path):
    try:
        root = ET.Element("NeuralNetwork")
        for layer_data in data:
            layer = ET.SubElement(root, "layer")
            for neuron_values in layer_data:
                neuron = ET.SubElement(layer, "neuron")
                neuron.text = str(neuron_values).replace(",", "")
        tree = ET.ElementTree(root)
        with open(output_path, "wb") as file:
            tree.write(file, encoding="utf-8", xml_declaration=True)
        print(f"Данные успешно записаны в {output_path}.")
    except FileNotFoundError:
        write_error(f"Ошибка: Файл '{output_path}' не найден.")
        sys.exit()
    except Exception as e:
        write_error(f"Ошибка при записи XML: {e}")
        sys.exit()

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def calculate(matrix, vector):
    output_by_layer = []
    
    for layer_weights in matrix:
        current_layer_output = []

        for neuron_weights in layer_weights:
            if len(neuron_weights) == len(vector): 
                weighted_sum = sum(weight * value for weight, 
                                   value in zip(neuron_weights, vector)
                                   )
                neuron_output = sigmoid(weighted_sum)
                current_layer_output.append(neuron_output)
            else:
                write_error(
                    f"Ошибка: Несоответствие размерностей. "
                )
                sys.exit()

        output_by_layer.append(current_layer_output)
        vector = current_layer_output

    return output_by_layer[-1] if output_by_layer else [] 


def main():
    params = parse_arguments()

    try:
        layers = read_matrix(params["input1"])
        
        input_vector = read_vector(params["input2"])

        serialize_to_xml(layers, params["output1"])

        output_vector = calculate(layers, input_vector)

        with open(params["output2"], "w", encoding="utf-8") as f:
            f.write(", ".join(map(str, output_vector)))

    except Exception as e:
        write_error(f"Ошибка: {e}")


if __name__ == "__main__":
    main()