# FlatQL

**FlatQL** is a library to convert one dictionary to another. It's also very useful in searching values in nested dictionaries.

### Prerequisites

python version >= 3.0

### Installing

```python
pip3 install git+https://github.com/jerzygajda/FlatQL.git
```

## Quick usage

### Find values in the dictionary based on a path

Sometimes you need to find all values on a particular path.
In this case, we have config `items.*.name` in human language means: go to `items` key and for every item get the value of `name` key.

```python
from flatql import find_in_path 
data = {'items': [{'name': 'Item 1'},
                  {'name': 'Item 2'}]}
result = find_in_path(data, 'items.*.name'])
#['Item 1', 'Item 2']
```

### Transform one dictionary to another 

If you using various API very often you must convert data to your system.

In this example, we have `resource` it's our input data, and `config` its mapping configuration.

Config is a simple dictionary where keys were paths to find in input data and values is a destination path.

```python
from flatql import transform

resource = {'res_uuid': '00000000-0000-0000-0000-000000000001',
            'res_name': 'Test resource',
            'test': {'id': '00000000-0000-0000-0000-000000000002'},
            'list': [{'id': '00000000-0000-0000-0000-000000000003'},
                     {'id': '00000000-0000-0000-0000-000000000004'}]}

config = {'res_uuid': 'id', # map res_uuid to id
          'list.*.id': 'items.{1}', # '*' in path means every list item, {1} in target is index of key from path parts
          'res_name': 'name'}
result = transform(resource, config)
#{'id': '00000000-0000-0000-0000-000000000001',
# 'name': 'Test resource',
# 'items': ['00000000-0000-0000-0000-000000000003',
#           '00000000-0000-0000-0000-000000000004']}
```

### Transform one dictionary to another - with functions

This example is very similar to the previous one. One difference is in the configuration.
In this case we attach transform function `transform_item(item, path, template)` to configuration.

```python
from flatql import transform, rewrite_path

def transform_item(item, path, template):
    target_path = rewrite_path(path, template)
    return (target_path, {'test': 1}) # replace every item by {'test': 1}

resource = {'authors': [{'id': 1, 'res_name': 'Author 1'},
                        {'id': 2, 'res_name': 'Author 2'}]}

# for every item in authors call transform_item and save the result in creator
config = {'authors.*': (transform_item, 'creator.{1}')}

result = transform(resource, config)
#{'creator': [{'test': 1}, {'test': 1}]}
```

### Extract some data from dictionary/list

To extract only specified data you can use extract function

```python
from flatql import extract

resource = {'authors': [{'id': 1, 'res_name': 'Author 1'},
                        {'id': 2, 'res_name': 'Author 2'}]}

# for every item in authors get id field
paths = ['authors.*.id']

result = extract(resource, paths)
#{'authors': [{'id': 1}, {'id': 2}]}
```

### Get and Set values

You can also get or set values based on the path.

```python
from flatql import get_in, set_in

data = {}
data = set_in(data, 'items.#0.name', 'Test 1')
data = set_in(data, 'items.#1.name', 'Test 2')
# data = {'items': [{'name': 'Test 1'}, {'name': 'Test 2'}]}

value = get_in(data, 'items.#1.name')
# value = 'Test 2'

```

## Tests
python3 -m unittest discover
