def build_tree_dict(tree_dict, specifiers):
    identifier, specifier = specifiers[0]

    if identifier == 'vert':
        print(identifier, specifier)

    if specifier not in tree_dict:
        tree_dict[specifier] = {
            'identifier': identifier,
            'specifier': specifier,
            'items': {}
        }

    if len(specifiers) > 1:
        build_tree_dict(tree_dict[specifier]['items'], specifiers[1:])


def build_tree_list(tree_dict):
    tree_list = []
    for specifier, item in tree_dict.items():
        tree_list.append({
            'identifier': item.get('identifier'),
            'specifier': item.get('specifier'),
            'items': build_tree_list(item.get('items'))
        })

    return tree_list
