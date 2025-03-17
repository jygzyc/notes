class BiMap:
    """
    BiMap class for bidirectional mapping between keys and values.
    """
    def __init__(self):
        self.key_to_value = {}
        self.value_to_key = {}

    def put(self, key, value):
        if key in self.key_to_value or value in self.value_to_key:
            return 
        
        self.key_to_value[key] = value
        self.value_to_key[value] = key

    def get_by_key(self, key):
        return self.key_to_value.get(key)

    def get_by_value(self, value):
        return self.value_to_key.get(value)

    def remove_by_key(self, key):
        if key in self.key_to_value:
            value = self.key_to_value.pop(key)
            del self.value_to_key[value]

    def remove_by_value(self, value):
        if value in self.value_to_key:
            key = self.value_to_key.pop(value)
            del self.key_to_value[key]

    def iterate(self):
        for key, value in self.key_to_value.items():
            yield key, value