from flask import Flask, make_response, request
from ValidateurGenerique.FormValidator import FormValidator
import json

app = Flask(__name__)

def load_schema(file_path):
    try:
        with open(file_path, 'r') as file:
            schema = json.load(file)
            return schema
    except FileNotFoundError:
        raise ValueError(f"Error loading schema: File not found - {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error loading schema: {str(e)} - {file_path}")

file_path = 'C:\\Users\\Acer\\Desktop\\ValidateurGeneric\\schema.json'

try:
    schema = load_schema(file_path)
    print("Schema loaded successfully:", schema)
except ValueError as e:
    print("Error:", str(e))
    exit()

form_validator = FormValidator(schema)

@app.route('/api/validate_form', methods=['POST'])
def api_validate_form():
    try:
        data = request.get_json()
        print("Received JSON data:", data)

        errors = form_validator.validate_schema(data, 'root')
        if errors:
            flat_errors = [{"error": str(error)} for error in errors]
            return make_response({'status': 'error', 'errors': flat_errors}), 400
        else:
            return make_response({'status': 'success', 'message': 'Form is valid'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return make_response({'status': 'error', 'error': str(e)}, 500)

if __name__ == '__main__':
    app.run(debug=True)
