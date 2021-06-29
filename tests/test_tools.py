import unittest
from flatql import get_in, set_in, find_in_path, find_in_paths, transform, rewrite_path, extract


class TestDocument(unittest.TestCase):
    def test_get_in_list_items(self):
        data = {'a': ['b', 'c']}
        self.assertEqual(get_in(data, 'a.#0'), 'b')
        self.assertEqual(get_in(data, 'a.#1'), 'c')
        self.assertEqual(get_in(data, 'a.#2'), None)
        self.assertEqual(get_in(data, 'a.#-1'), 'c')
        self.assertEqual(get_in(data, 'a.#-2'), 'b')
        self.assertEqual(get_in(data, 'a.#-3'), None)

    def test_get_with_dict(self):
        data = {'a': {'b': {'c': 'Value'}}}
        self.assertEqual(get_in(data, 'a.b.c'), 'Value')

    def test_get_in_without_data(self):
        self.assertEqual(get_in({}, 'a.b.c.d'), None)
        self.assertEqual(get_in({}, 'a.#0'), None)

    def test_set_in_with_dict(self):
        data = {'a': {'b': 'c'}}
        expected = {'a': {'b': 'item'}}
        result = set_in(data, 'a.b', 'item')
        self.assertEqual(result, expected)

    def test_set_in_with_list(self):
        data = {'item': ['a', 'b', 'c']}
        expected = {'item': ['d', 'e', 'f']}
        result = set_in(data, 'item.#0', 'd')
        result = set_in(result, 'item.#1', 'e')
        result = set_in(result, 'item.#2', 'f')
        self.assertEqual(result, expected)

    def test_set_in_without_data(self):
        data = {}
        expected = {'a': {'b': 'c'}, 'b': [{'name': 'Item 1'},
                                           {'name': 'Item 2'},
                                           {'name': 'Item 3'}],
                    'c': ['Item 1', 'Item 2']}
        result = set_in(data, 'a.b', 'c')
        result = set_in(result, 'b.#0.name', 'Item 1')
        result = set_in(result, 'b.#2.name', 'Item 2')
        result = set_in(result, 'b.#3.name', 'Item 3')
        result = set_in(result, 'c.#0', 'Item 1')
        result = set_in(result, 'c.#1', 'Item 2')
        self.assertEqual(result, expected)

    def test_find_in_path(self):
        data = {'res_uuid': '00000000-0000-0000-0000-000000000001',
                'test': {'id': '00000000-0000-0000-0000-000000000002'},
                'list': [{'id': '00000000-0000-0000-0000-000000000003'},
                         {'id': '00000000-0000-0000-0000-000000000004'}],
                'deep_list': [
                    {'items': [{'item': {'id': '00000000-0000-0000-0000-000000000005'}}]}]}
        self.assertEqual(find_in_path(data, 'res_uuid'),
                         ['00000000-0000-0000-0000-000000000001'])
        self.assertEqual(find_in_path(data, 'list.#0.id'),
                         ['00000000-0000-0000-0000-000000000003'])
        self.assertEqual(find_in_path(data, 'deep_list.*.items.*.item.id'),
                         ['00000000-0000-0000-0000-000000000005'])

    def test_find_in_paths(self):
        data = {'res_uuid': '00000000-0000-0000-0000-000000000001',
                'test': {'id': '00000000-0000-0000-0000-000000000002'},
                'list': [{'id': '00000000-0000-0000-0000-000000000003'},
                         {'id': '00000000-0000-0000-0000-000000000004'}],
                'deep_list': [
                    {'items': [{'item': {'id': '00000000-0000-0000-0000-000000000005'}}]}]}
        expected = ['00000000-0000-0000-0000-000000000005',
                    '00000000-0000-0000-0000-000000000003',
                    '00000000-0000-0000-0000-000000000004']
        result = find_in_paths(data, ['deep_list.*.items.*.item.id', 'list.*.id'])
        self.assertEqual(result, expected)

    def test_transform_result(self):
        resource = {'res_uuid': '00000000-0000-0000-0000-000000000001',
                    'res_name': 'Test resource',
                    'test': {'id': '00000000-0000-0000-0000-000000000002'},
                    'list': [{'id': '00000000-0000-0000-0000-000000000003'},
                             {'id': '00000000-0000-0000-0000-000000000004'}]}
        config = {'res_uuid': 'id', 'list.*.id': 'list.{1}', 'res_name': 'name'}
        result = transform(resource, config)
        expected = {'id': '00000000-0000-0000-0000-000000000001',
                    'name': 'Test resource',
                    'list': ['00000000-0000-0000-0000-000000000003',
                             '00000000-0000-0000-0000-000000000004']}
        self.assertEqual(result, expected)


    def test_transform_with_manifest(self):
        def transform_item(item, source_path, target_path, manifest):
            target_path = rewrite_path(source_path, target_path)
            res_id = item.get('id')
            item_from_manifest = manifest.get(res_id)
            result = {'name': item_from_manifest.get('res_name'),
                      'id': item_from_manifest.get('res_uuid')}
            return (target_path, result)

        resource = {'res_uuid': '00000000-0000-0000-0000-000000000001',
                    'test': {'id': '00000000-0000-0000-0000-000000000002'},
                    'list': [{'id': '00000000-0000-0000-0000-000000000003'},
                             {'id': '00000000-0000-0000-0000-000000000004'}]}
        manifest = {'00000000-0000-0000-0000-000000000003':
                        {'res_name': 'test 1', 'res_uuid': '00000000-0000-0000-0000-000000000003'},
                    '00000000-0000-0000-0000-000000000004':
                        {'res_name': 'test 2', 'res_uuid': '00000000-0000-0000-0000-000000000004'}}
        config = {'res_uuid': 'id',
                  'list.*': (transform_item, 'list.{1}', manifest)}
        result = transform(resource, config)
        expected = {'id': '00000000-0000-0000-0000-000000000001',
                    'list': [
                        {'name': 'test 1', 'id': '00000000-0000-0000-0000-000000000003'},
                        {'name': 'test 2', 'id': '00000000-0000-0000-0000-000000000004'}]}
        self.assertEqual(result, expected)

    def test_simple_transform(self):
        resource = {'a': {'aa': {'aaa': 'value'}}}
        config = {'a.aa.aaa': 'b.bb.bbb'}
        result = transform(resource, config)
        expected = {'b': {'bb': {'bbb': 'value'}}}
        self.assertEqual(result, expected)

    def test_simple_transform_without_full_path(self):
        resource = {'a': {'aa': {'aaa': 'value'}}}
        config = {'a.aa': 'b.bb'}
        result = transform(resource, config)
        expected = {'b': {'bb': {'aaa': 'value'}}}
        self.assertEqual(result, expected)

    def test_simple_transform_list(self):
        resource = {'a': {'aa': [{'item': 1}, {'item': 2}]}}
        config = {'a.aa.*.item': 'b.bb.{2}.element'}
        result = transform(resource, config)
        expected = {'b': {'bb': [{'element': 1}, {'element': 2}]}}
        self.assertEqual(result, expected)

    def test_transform_with_list_index(self):
        resource = {'a': {'aa': [{'item': 1}, {'item': 2}]}}
        config = {'a.aa.#1.item': 'item'}
        result = transform(resource, config)
        expected = {'item': 2}
        self.assertEqual(result, expected)

    def test_transform_key_rename(self):
        resource = {'test': {'a': 'aa', 'b': 'bb'}}
        config = {'test': 'x'}
        result = transform(resource, config)
        expected = {'x': {'a': 'aa', 'b': 'bb'}}
        self.assertEqual(result, expected)

    def test_transform_with_path_parts_reorder(self):
        resource = {
            'a': {'aa': 'aaa'},
            'b': {'bb': 'bbb'},
            'c': {'cc': 'ccc'}
        }
        config = {'*.*': '{1}.{0}'}
        result = transform(resource, config)
        expected = {
            'aa': {'a': 'aaa'},
            'bb': {'b': 'bbb'},
            'cc': {'c': 'ccc'}
        }
        self.assertEqual(result, expected)

    def test_complex_transform(self):
        resource = {'count': 2, 'entries': [
            {'res_name': 'A', 'authors': [{'id': 1, 'res_name': 'Author 1'},
                                          {'id': 2, 'res_name': 'Author 2'}]},
            {'res_name': 'B', 'authors': [{'id': 4, 'res_name': 'Author 4'},
                                          {'id': 1, 'res_name': 'Author 1'}]}]}
        config = {'count': 'elements',
                  'entries.*.res_name': 'items.{1}.name',
                  'entries.*.authors.*.id': 'items.{1}.authors.{3}.ref'}
        result = transform(resource, config)
        expected = {'elements': 2, 'items': [
            {'name': 'A', 'authors': [{'ref': 1}, {'ref': 2}]},
            {'name': 'B', 'authors': [{'ref': 4}, {'ref': 1}]}]}
        self.assertEqual(result, expected)
    
    def test_transform_lists_with_index(self):
        resource = {'count': 2, 'entries': [
            {'res_name': 'A', 'authors': [{'id': 1, 'res_name': 'Author 1'},
                                          {'id': 2, 'res_name': 'Author 2'}]},
            {'res_name': 'B', 'authors': [{'id': 4, 'res_name': 'Author 4'},
                                          {'id': 1, 'res_name': 'Author 1'}]}]}
        config = {
            'entries.#0.authors.#0.res_name': 'name',
            'entries.#0.authors.#0.id': 'id'
            }
        result = transform(resource, config)
        expected = {'name': 'Author 1', 'id': 1}
        self.assertEqual(result, expected)

    def test_transform_with_function(self):
        def transform_item(item, path, template):
            target_path = rewrite_path(path, template)
            return (target_path, {'test': 1})

        resource = {'authors': [{'id': 1, 'res_name': 'Author 1'},
                                {'id': 2, 'res_name': 'Author 2'}]}

        config = {'authors.*': (transform_item, 'creator.{1}')}

        result = transform(resource, config)
        expected = {'creator': [{'test': 1}, {'test': 1}]}
        self.assertEqual(result, expected)

    def test_transform_with_deep_lists(self):
        resource = {'list': [{'id': 1}, {'id': 2}],
                    'deep_list': [{'name': 'Item 1',
                                   'authors': [{'name': 'Author 1'}, {'name': 'Author 2'}]},
                                  {'name': 'Item 2',
                                   'authors': [{'name': 'Author 3'}, {'name': 'Author 4'}]}]}
        config = {'list.*.id': 'list.{1}.uuid',
                  'deep_list.*.name': 'deep_list.{1}.display_name',
                  'deep_list.*.authors.*.name': 'deep_list.{1}.authors.{3}.n'}
        result = transform(resource, config)
        expected = {'deep_list':
                        [{'authors': [{'n': 'Author 1'}, {'n': 'Author 2'}],
                          'display_name': 'Item 1'},
                         {'authors': [{'n': 'Author 3'}, {'n': 'Author 4'}],
                          'display_name': 'Item 2'}],
                    'list': [{'uuid': 1}, {'uuid': 2}]}
        self.assertEqual(result, expected)

    def test_transform_dict_with_list_to_list(self):
        resource = {'list': [{'id': 1, 'name': 'Item 1'}, {'id': 2, 'name': 'Item 2'}]}
        config = {'list.*.id': '{1}.id',
                  'list.*.name': '{1}.title'}
        result = transform(resource, config)
        expected = [{'id': 1, 'title': 'Item 1'}, {'id': 2, 'title': 'Item 2'}]
        self.assertEqual(result, expected)

    def test_rewrite_path(self):
        self.assertEqual('item.#0.id', rewrite_path('list.#0.id', 'item.{1}.id'))
        self.assertEqual('item.#0.#1.id', rewrite_path('list.#0.#1.id', 'item.{1}.{2}.id'))
        self.assertEqual('#0.id', rewrite_path('list.#0.id', '{1}.id'))
        self.assertEqual('#100.id', rewrite_path('list.#100.id', '{1}.id'))
        self.assertEqual('items.item_1.uuid', rewrite_path('items.item_1.id', 'items.{1}.uuid'))
        self.assertEqual('d.c.b.a', rewrite_path('a.b.c.d', '{3}.{2}.{1}.{0}'))

    def test_transform_list_first_and_last_element(self):
        resource = [{'id': 1, 'name': 'First'},
                    {'id': 2, 'name': 'Second'},
                    {'id': 3, 'name': 'Last'}]
        config = {'#0.id': 'first.id',
                  '#0.name': 'first.title',
                  '#-1.id': 'last.id',
                  '#-1.name': 'last.title'}
        result = transform(resource, config)
        expected = {'first': {'id': 1, 'title': 'First'}, 'last': {'id': 3, 'title': 'Last'}}
        self.assertEqual(result, expected)

    def test_transform_with_dict_keys_wildcard(self):
        resource = {
            'items': {
                'item_1': {'id': 1, 'name': 'Item 1'},
                'item_2': {'id': 2, 'name': 'Item 2'},
                'item_3': {'id': 3, 'name': 'Item 3'}
            }
        }
        config = {'items.*.name': 'elements.{1}.title'}
        result = transform(resource, config)
        expected = {
            'elements': {
                'item_1': {'title': 'Item 1'},
                'item_2': {'title': 'Item 2'},
                'item_3': {'title': 'Item 3'}
            }
        }
        self.assertEqual(result, expected)

    def test_extract(self):
        resource = {
            'items': [
                {'id': 1, 'name': 'Item 1', 'description': 'Item 1 description'},
                {'id': 2, 'name': 'Item 2', 'description': 'Item 2 description'},
                {'id': 3, 'name': 'Item 3', 'description': 'Item 3 description'}
            ]
        }
        paths = ['items.*.name', 'items.*.id']
        result = extract(resource, paths)
        expected = {
            'items': [
                {'id': 1, 'name': 'Item 1'},
                {'id': 2, 'name': 'Item 2'},
                {'id': 3, 'name': 'Item 3'}
            ]
        }
        self.assertEqual(result, expected)

    def test_extract_with_dict_keys_wildcard(self):
        resource = {
            'items': {
                'item_1': {'id': 1, 'name': 'Item 1'},
                'item_2': {'id': 2, 'name': 'Item 2'},
                'item_3': {'id': 3, 'name': 'Item 3'}
            }
        }
        paths = ['items.*.name']
        result = extract(resource, paths)
        expected = {
            'items': {
                'item_1': {'name': 'Item 1'},
                'item_2': {'name': 'Item 2'},
                'item_3': {'name': 'Item 3'}
            }
        }
        self.assertEqual(result, expected)
