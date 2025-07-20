import base64
import pickle


class Binary:

    def str_to_binary(self, string):
        """Преобразование строки в бинарные данные"""
        try:
            encoded_string = base64.b64encode(string).decode("utf-8")
            return encoded_string
        except UnicodeEncodeError as error:
            raise ValueError(f"Error encode: {error}")

    def object_to_binary(self, obj):
        """
        Here, is used library pickle for a work with a binary and json data.
        Преобразование объекта в бинарные данные"""
        return pickle.dumps(obj)
