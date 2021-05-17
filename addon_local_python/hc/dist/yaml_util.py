import yaml
import os
import io


class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader)


Loader.add_constructor('!include', Loader.include)


def yaml2dict(filename):
    f = open(filename, 'r', encoding='utf8')
    res = yaml.load(f, Loader=yaml.FullLoader)
    f.close()
    return res


def dict2yaml(dict_, filename):
    with io.open(filename, 'w', encoding='utf-8') as outfile:
        yaml.dump(dict_, outfile, default_flow_style=False, allow_unicode=True)


def is_nocontent(lists):
    for item in lists:
        if len(lists[item]) != 0:
            return False
    return True
