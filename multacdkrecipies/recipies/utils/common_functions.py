def enum_parsing(source_list:list, target_enum) -> list:
    enums = list(target_enum)
    return [enum for enum in enums if enum.value in source_list]