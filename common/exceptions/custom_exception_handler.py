from rest_framework.views import exception_handler
from rest_framework.exceptions import ErrorDetail


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        error_field = "non_field_errors"
        first_error = "Unknown Error"

        data = response.data

        try:
            # if list
            if isinstance(data, list):
                first_item = next((item for item in data if item), None)

                if isinstance(first_item, dict):
                    field, errors = next(iter(first_item.items()))
                    error_field, first_error = _extract_error(errors, parent_field=field)
                elif first_item:
                    error_field = "non_field_errors"
                    first_error = str(first_item)

            # if dict
            elif isinstance(data, dict):
                if "non_field_errors" in data:
                    error_field = "non_field_errors"
                    errors = data["non_field_errors"]
                    _, first_error = _extract_error(errors)
                else:
                    field, errors = next(iter(data.items()))
                    error_field, first_error = _extract_error(errors, parent_field=field)

        except Exception as e:
            error_field = "non_field_errors"
            first_error = f"Error reading: {str(e)}"

        response.data = {
            "success": False,
            "status": status_code,
            "error_field": error_field,
            "error_message": str(first_error) if first_error else "Error occurred!",
        }

    return response


def _extract_error(errors, parent_field=None):

    if isinstance(errors, list) and errors:
        first_non_empty = next((e for e in errors if e), None)
        if isinstance(first_non_empty, dict):
            sub_field, sub_errors = next(iter(first_non_empty.items()))
            if isinstance(sub_errors, list) and sub_errors:
                return sub_field, sub_errors[0]
            return sub_field, sub_errors
        return parent_field, first_non_empty
    elif isinstance(errors, ErrorDetail):
        return parent_field, str(errors)
    return parent_field, errors
