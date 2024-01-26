import datetime
import re
import jsonschema
import functools

class FormValidator:
    def __init__(self, schema):
        self.schema = schema

    @staticmethod
    def validate_entry(func):
        @functools.wraps(func)
        def wrapper(self, field_value, field_schema, field_path=''):
            if not isinstance(field_schema, dict):
                raise ValueError('Invalid field_schema. Expected a dictionary.')
            
            if not isinstance(field_path, str):
                raise ValueError('Invalid field_path. Expected a string.')

            print("Validating entry:", field_path)
            return func(self, field_value, field_schema, field_path)

        return wrapper

    @validate_entry
    def validate_field(self, field_value, field_schema, field_path=''):
        try:
            jsonschema.validate(instance=field_value, schema=field_schema)
        except jsonschema.exceptions.ValidationError as e:
            print(f'Validation error at {field_path}: {e.message}')
            return [f'Validation error at {field_path}: {e.message}']

        field_errors = []
        print("Validating entry:", field_path) 
        if 'type' in field_schema:
            field_errors.extend(self.validate_type(field_value, field_schema['type'], field_schema, field_path))

        if 'properties' in field_schema:
            field_errors.extend(self.validate_object(field_value, field_schema['properties'], field_path))

        if 'items' in field_schema:
            field_errors.extend(self.validate_array(field_value, field_schema['items'], field_path))

        if 'format' in field_schema:
            field_errors.extend(self.validate_format(field_value, field_schema['format'], field_path))

        return field_errors

    def validate_type(self, field_value, expected_type, field_schema, field_path=''):
        field_errors = []

        if expected_type == 'object':
            if not isinstance(field_value, dict):
                field_errors.append(f'Invalid type for {field_path}. Expected object.')
            else:
                for key, value in field_schema.get('properties', {}).items():
                    nested_path = f'{field_path}.{key}' if field_path else key
                    if key in field_value:
                        nested_errors = self.validate_field(field_value[key], value, nested_path)
                        if nested_errors:
                            field_errors.extend(nested_errors)
                    elif 'required' in value and value['required']:
                        field_errors.append(f"Field {nested_path} is required")

        elif expected_type == 'string':
            try:
                str(field_value)
            except ValueError:
                field_errors.append(f'Invalid type for {field_path}. Expected string.')

            try:
                if 'pattern' in field_schema and not re.match(field_schema['pattern'], str(field_value)):
                    field_errors.append(f'Invalid pattern for {field_path}')
            except ValueError as e:
                field_errors.append(str(e))

        elif expected_type == 'array':
            if not isinstance(field_value, list):
                field_errors.append(f'Invalid type for {field_path}. Expected array.')
            else:
                for index, item in enumerate(field_value):
                    nested_path = f'{field_path}.{index}' if field_path else str(index)
                    nested_errors = self.validate_field(item, field_schema.get('items', {}), nested_path)
                    if nested_errors:
                        field_errors.extend(nested_errors)

        elif expected_type == 'number':
            try:
                float(field_value)
            except ValueError:
                field_errors.append(f'Invalid type for {field_path}. Expected number.')

        elif expected_type == 'boolean':
            if not isinstance(field_value, bool):
                field_errors.append(f'Invalid type for {field_path}. Expected boolean.')

        elif expected_type == 'null':
            if field_value is not None:
                field_errors.append(f'Invalid type for {field_path}. Expected null.')

        return field_errors

    @validate_entry
    def validate_object(self, field_value, properties, field_path=''):
        print(f"Validating object at path {field_path}")
        field_errors = []

        if not isinstance(field_value, dict):
            field_errors.append(f'Invalid type for {field_path}. Expected object.')
        else:
            for key, value in properties.items():
                nested_path = f'{field_path}.{key}' if field_path else key
                if key in field_value:
                    nested_errors = self.validate_field(field_value[key], value, nested_path)
                    if nested_errors:
                        field_errors.extend(nested_errors)
                elif 'required' in value:
                    field_errors.append(f"Field {nested_path} is required")

        return field_errors

    @validate_entry
    def validate_array(self, field_value, items, field_path=''):
        field_errors = []

        if not isinstance(field_value, list):
            field_errors.append(f'Invalid type for {field_path}. Expected array.')
        else:
            for index, item in enumerate(field_value):
                nested_path = f'{field_path}.{index}' if field_path else str(index)
                nested_errors = self.validate_field(item, items, nested_path)
                if nested_errors:
                    field_errors.extend(nested_errors)

        return field_errors

    @validate_entry
    def validate_format(self, field_value, format_name, field_path=''):
        format_method = getattr(self, f"validate_{format_name}", None)
        if format_method:
            try:
                format_method(field_value)
            except ValueError as e:
                return [f'Invalid format for {field_path}. {str(e)}']

        return []

    def validate_date(self, date_str, date_formats):
        for date_format in date_formats:
            try:
                datetime.datetime.strptime(date_str, date_format)
                return
            except ValueError:
                continue
        raise ValueError(f'Invalid date format. Expected format(s): {", ".join(date_formats)}')

    def validate_email(self, email):
        if '@' not in email:
            raise ValueError('Invalid email format: Missing "@"')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError('Invalid email format')

    @validate_entry
    def validate_schema(self, form_data, field_path=''):
        try:
            jsonschema.validate(instance=form_data, schema=self.schema)
        except jsonschema.exceptions.ValidationError as e:
            return [f'Validation error at {field_path}: {e.message}']

        return self.validate_object(form_data, self.schema, field_path)
