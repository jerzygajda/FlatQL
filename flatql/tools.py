from flatql.helpers import convert_pseudo_list, simple_rewrite

def get_in(input_data, path, default=None):
    """Get the value at the path in input_data.

    :param input_data: dict or list
    :param path: the path of the value to get, example: item.#1.name
    :param default: value returned if nothing was found
    :return: value
    """
    if '*' in path:
        raise ValueError('* in path is not supported')
    found = find(input_data, path.split('.'))
    if found:
        return found[0][1]
    return default

def set_in(input_data, path, value):
    """Set the value at the path in input_data.

    :param input_data: dict or list
    :param path: the path of the value to set, example: item.#1.name
    :param value: value to set
    :return: modified input_data
    """
    if '*' in path:
        raise ValueError('* in path is not supported')
    path_parts = path.split('.')
    current_path_part = path_parts[0] if path_parts else None
    if current_path_part:
        if not input_data:
            input_data = [] if current_path_part.startswith('#') else {}
        if isinstance(input_data, list):
            idx = int(current_path_part[1:])
            data = input_data[idx] if input_data and len(input_data) > idx else None
            result = set_in(data, '.'.join(path_parts[1:]), value)
            if data:
                input_data[idx] = result
            else:
                input_data.insert(idx, result)
        elif isinstance(input_data, dict):
            data = input_data.get(current_path_part)
            input_data[current_path_part] = set_in(data, '.'.join(path_parts[1:]), value)
    else:
        return value
    return input_data

def find_in_path(input_data, path):
    """Finds values at the path in input_data.

    :param input_data: dict or list
    :param path: the path of the values example: b.*.name
    :result: list of found data
    """
    result = find(input_data, path.split('.'))
    return [value for _, value in result if value]

def find_in_paths(input_data, paths):
    """Finds values at the paths in input_data.

    :param input_data: dict or list
    :param paths: the paths list, example: ['a.b.c', b.*.name]
    :result: list of found data
    """
    result = []
    for path in paths:
        references = find(input_data, path.split('.'))
        for _, refs in references:
            result.append(refs)
    return result

def find(input_data, path, current_path=None):
    """Finds all elements based on path

    :param input_data: dict or list
    :param path: the path list, example: b.*.name
    :param current_path: the current path, default=None
    :return: list elements of shape (path, value)
    """
    fields_found = []
    if isinstance(input_data, dict) and path:
        new_path = f'{current_path}.{path[0]}' if current_path else path[0]
        fields_found.extend(find(input_data.get(path[0]), path[1:], new_path))
    elif isinstance(input_data, list) and path:
        if path[0] == '*':
            for idx, item in enumerate(input_data):
                new_path = f'{current_path}.#{idx}' if current_path else f'#{idx}'
                fields_found.extend(find(item, path[1:], new_path))
        elif path[0].startswith('#'):
            idx = int(path[0][1:])
            if (0 <= idx < len(input_data)) or (-len(input_data) <= idx < 0):
                new_path = f'{current_path}.#{idx}' if current_path else f'#{idx}'
                fields_found.extend(find(input_data[idx], path[1:], new_path))
    elif not path:
        fields_found.append((current_path, input_data))
    return fields_found

def rewrite_path(path, template):
    """Converts source path to destination path based on template

    :param path: string, example: a.#0.name
    :param template: template string, example: b.*.name
    :return: string, example: b.#0.name
    """
    for p in path.split('.'):
        if p.startswith('#'):
            template = template.replace('*', p, 1)
    return template

def transform(input_data, transform_config):
    """Transforms input data to another shape based on config

    :param input_data: dict or list
    :param transform_config: dict where the keys are source paths
        and the values are destination paths
    :return: dict or list
    """
    flat_data = []
    for src, dst in transform_config.items():
        fields_found = find(input_data, src.split('.'), None)
        for field in fields_found:
            if isinstance(dst, str):
                target_path = rewrite_path(field[0], dst)
                result = simple_rewrite(field[0], target_path, field[1])
                flat_data.append(result)
            else:
                func = dst[0]
                args = dst[1:]
                target_path = rewrite_path(field[0], args[0])
                result = func(field[1], field[0], *args)
                flat_data.append(result)
    result = {}
    for path, value in flat_data:
        current_level = result
        path_parts = path.split('.')
        path_parts_length = len(path_parts)
        for idx, p in enumerate(path_parts):
            if idx == path_parts_length - 1: # last
                current_level[p] = value
            else:
                current_level.setdefault(p, {})
                current_level = current_level[p]
    return convert_pseudo_list(result)
