import socket
import os
import torch

SOCKET_PATH = "/tmp/bash_autocomplete.sock" 
MODEL_PATH = "inferenced/lstm_model_state.pth" 

def load_pytorch_model(model_path):
    """
    Загружает PyTorch модель из файла .pth.
    """
    print(f"Загрузка модели из: {model_path}")
    print("ЗАГЛУШКА: Модель типа загружена.")
    return "dummy_model_object"

def get_prediction_from_model(text_input, model):
    """
    Получает предсказание от загруженной модели.
    """
    if model is None:
        return "Ошибка: модель не загружена"
    
    print(f"Получен текст для предсказания: '{text_input}'")
    words = text_input.split(" ")
    if words:
        predicted_word = words[-1] + "_next" 
    else:
        predicted_word = "start_next"
    print(f"ЗАГЛУШКА: Предсказанное слово: '{predicted_word}'")
    return predicted_word

def start_server(model_path_param, socket_path_param):
    """
    UDS server
    """
    loaded_model = load_pytorch_model(model_path_param)
    if loaded_model is None:
        print("Не удалось загрузить модель. Сервер не будет запущен.")
        return

    if os.path.exists(socket_path_param):
        try:
            os.remove(socket_path_param)
            print(f"Удален старый сокет-файл: {socket_path_param}")
        except OSError as e:
            print(f"Ошибка при удалении сокет-файла {socket_path_param}: {e}")
            return


    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    try:
        server_socket.bind(socket_path_param)
        server_socket.listen(1)
        print(f"Сервер запущен и слушает на: {socket_path_param}")

        while True:
            print("Ожидание нового подключения...")
            connection, client_address = server_socket.accept()
            try:
                print("Клиент подключился.")
                while True:
                    data = connection.recv(1024) #todo add config param
                    if not data:
                        print("Клиент отключился (нет данных).")
                        break
                    
                    received_text = data.decode('utf-8').strip() 
                    if not received_text: 
                        print("Получена пустая строка от клиента.")
                        continue

                    print(f"Получено от клиента: '{received_text}'")
                    
                    prediction = get_prediction_from_model(received_text, loaded_model)
                    
                    connection.sendall(prediction.encode('utf-8'))
                    print(f"Отправлено клиенту: '{prediction}'")

            except ConnectionResetError:
                print("Клиент разорвал соединение.")
            except Exception as e:
                print(f"Ошибка при обработке клиента: {e}")
            finally:
                print("Закрытие соединения с клиентом.")
                connection.close()
    
    except Exception as e:
        print(f"Критическая ошибка сервера: {e}")
    finally:
        print("Остановка сервера.")
        if os.path.exists(socket_path_param):
            try:
                os.remove(socket_path_param) # Очистка сокет-файла при выходе
                print(f"Удален сокет-файл при остановке: {socket_path_param}")
            except OSError as e:
                 print(f"Ошибка при удалении сокет-файла {socket_path_param} при остановке: {e}")
        server_socket.close()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    actual_model_path = os.path.join(script_dir, "lstm_model_state.pth")

    if not os.path.exists(actual_model_path):
        print(f"ПРЕДУПРЕЖДЕНИЕ: Файл модели не найден по пути: {actual_model_path}")
        print("Пожалуйста, убедитесь, что файл lstm_model_state.pth находится в той же директории, что и server.py,")
        print("или исправьте путь в MODEL_PATH внутри скрипта.")

    print(f"Используемый путь к модели: {actual_model_path}")
    print(f"Используемый путь к сокету: {SOCKET_PATH}")
    
    start_server(actual_model_path, SOCKET_PATH)
