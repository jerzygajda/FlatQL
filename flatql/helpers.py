def simple_rewrite(source_path, target_path, item):
    return (target_path, item)

def convert_pseudo_list(input_data):
    """Converts input data with pseudo lists to normal lists

    :param input_data: dict, example: {'test': {'#0': 'item 1' ,'#1': 'item 2'}}
    :return: dict or list, example: {'test': ['item 1', 'item 2']}
    """
    if isinstance(input_data, dict):
        if input_data:
            key = next(iter(input_data))
            if key.startswith('#'):
                result = []
                for idx in range(0, len(input_data.keys())):
                    value = input_data.get(f'#{idx}')
                    result.append(convert_pseudo_list(value))
            else:
                result = {}
                for key, value in input_data.items():
                    result[key] = convert_pseudo_list(value)
            return result
        return None
    return input_data
