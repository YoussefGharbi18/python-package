class Transformations:
    def transform_date(self, date_str, date_formats):
        try:
            result = self.validate_date(date_str, date_formats)
            print("Transformed Date:", result)
            return result
        except ValueError:
            raise ValueError('Invalid date format')