
def get_validation_error_code(error_type: str, field) -> str:
    # 独自のバリデーションエラーコードを返す
    # yearでバリデーションエラーが発生した場合、monthが指定されているがyearが指定されてない場合と
    # yearが2024~2099の範囲外の場合の2パターンがあるため、エラーコードを分けるため
    if error_type == "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED":
        return "YEAR_REQUIRED_WHEN_MONTH_SPECIFIED"

    if error_type == "empty_list":
        return "EMPTY_LIST"

    if error_type == "value_error":
        match field:
            case "year":
                return "INVALID_YEAR"
            case "month":
                return "INVALID_MONTH"
            case "date":
                return "INVALID_DATE"
            case "email":
                return "INVALID_EMAIL"
            case "category":
                return "INVALID_CATEGORY"
            case "username":
                return "INVALID_USERNAME"
            case "new_password" | "password":
                return "INVALID_PASSWORD"
            case _:
                return "INVALID_VALUE"

    match error_type:
        case "float_parsing" | "int_parsing":
            return "INVALID_NUMBER"
        case "string_type":
            return "INVALID_STRING"
        case "date_from_datetime_parsing":
            return "INVALID_DATE"
        case "list_type":
            return "INVALID_LIST"
        case "missing":
            return "REQUIRED"
        case "value_error":
            return "INVALID_VALUE"
        case _:
            return "INVALID_INPUT"
