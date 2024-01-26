import jsonschema

class SchemaValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate_schema(self, data):
        try:
            jsonschema.validate(instance=data, schema=self.schema)
            return True  
        except jsonschema.exceptions.ValidationError as e:
            print(f"Schema validation failed: {e}")
            return False