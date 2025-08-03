import base64
import pickle


class Binary:

    def str_to_binary(self, string) -> bytes:
        """Преобразование строки в бинарные данные"""
        try:
            encoded_string = base64.b64encode(
                string.encode("utf-8")
            )  # .decode("utf-8")
            return encoded_string
        except UnicodeEncodeError as error:
            raise ValueError(f"Error encode: {error}")

    def binary_to_str(self, binary_str) -> str:
        """Преобразование base64 строки обратно в исходную строку"""
        try:
            # decoded_bytes = base64.b64decode(binary_str.encode("utf-8"))
            decoded_bytes = base64.b64decode(binary_str).decode("utf-8")
            return decoded_bytes
        except (UnicodeDecodeError, base64.binascii.Error) as error:
            raise ValueError(f"Error decode: {error}")

    def object_to_binary(self, obj) -> bytes:
        """
        Here, is used library pickle for a work with a binary and json data.
        Преобразование объекта в бинарные данные"""
        return pickle.dumps(obj)

    def binary_to_object(self, binary_data) -> object:
        """Преобразование бинарных данных обратно в объект (десериализация pickle)"""
        try:
            return pickle.loads(binary_data)
        except pickle.PickleError as error:
            raise ValueError(f"Error deserializing object: {error}")
