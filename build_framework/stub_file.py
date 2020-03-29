# -*- coding: utf-8 -*-

import os
import imp
import inspect
from setuptools import Command


HEADER = '''\
# -*- coding: utf-8 -*-

"""
import sys


def __bootstrap__():
    """
    This function does not exist. It is a bootstrapper that loads the pyd file.
    :return: 
    """
    import imp
    
    mod_file = __file__ + 'd'
    mod = imp.load_dynamic(
        '',
        mod_file
    )
    
    sys.modules[__name__] = mod
    

__bootstrap__()

del __bootstrap__


# this is here to make an IDE happy.
if __name__ not in sys.modules:
    import logging

'''

CLASS_TEMPLATE = '''
{indent}class {class_name}({parent_classes}):
{indent}    """
{class_doc}
{indent}    """
{class_attributes}{class_methods}{class_properties}{class_classes}
'''

FUNC_TEMPLATE = '''
{indent}def {func_name}({func_args}):
{indent}    """
{func_doc}
{indent}    """
{indent}    pass
'''

METH_TEMPLATE = '''
{indent}    def {meth_name}({meth_args}):
{indent}        """
{meth_doc}
{indent}        """
{indent}        pass
'''

PROPGET_TEMPLATE = '''
{indent}@property
{indent}def {prop_name}(self):
{indent}    """
{prop_doc}
{indent}    """
{indent}    return None
'''


PROPSET_TEMPLATE = '''
{indent}@{prop_name}.setter
{indent}def {prop_name}(self, value):
{indent}    pass
'''


def _is_in_base(bases, item):
    for base in bases:
        if item in base.__dict__.values():
            return True
    return False


def _iter_bases(parent, bases):
    for parent_base in inspect.getmro(parent):
        if parent_base == parent:
            continue

        if parent_base in bases:
            bases.remove(parent_base)

        _iter_bases(parent_base, bases)


def _build_class(class_name, cls, indent):
    if not cls.__module__.startswith(''):
        return ''

    class_doc = inspect.getdoc(cls)

    if class_doc in (None, 'None'):
        class_doc = indent + '    NO DOC'
    else:
        class_doc = '\n'.join(
            indent + '    ' + line for line in class_doc.split('\n')
        )

    class_attributes = []
    class_methods = []
    class_properties = []
    class_classes = []
    bases = list(b for b in inspect.getmro(cls) if b != cls)

    for parent_class in bases[:]:
        if parent_class != cls:
            _iter_bases(parent_class, bases)

    parent_classes = list(p.__name__ for p in bases)

    if not parent_classes:
        parent_classes = ['object']

    bases = list(b for b in inspect.getmro(cls) if b != cls)

    for item_name, item in cls.__dict__.items():
        if isinstance(item, staticmethod):
            item = item.__func__

        if item_name in (
            '__dict__',
            '__weakref__',
            '__setstate__',
            '__reduce__'
        ):
            continue

        if _is_in_base(bases, item):
            continue

        if item_name.startswith('_') and not item_name.endswith('_'):
            continue

        if inspect.isclass(item):
            class_classes += [_build_class(item_name, item, indent + '    ')]
        elif inspect.isgetsetdescriptor(item) or isinstance(item, property):
            class_properties += [_build_prop(item_name, item, indent)]
        elif inspect.ismethod(item) or inspect.ismethoddescriptor(item):
            class_methods += [_build_meth(item_name, item, indent)]
        elif inspect.isfunction(item):
            class_methods += [_build_meth(item_name, item, indent)]
        elif not item_name.startswith('_'):
            item = str(type(item)).split("'")[1].split('.')[-1]
            if item in ('module', 'property', 'builtin_function_or_method'):
                continue

            class_attributes += [
                indent + '    ' + item_name + ' = {0}()\n'.format(item)
            ]

    output = CLASS_TEMPLATE.format(
        class_name=class_name,
        parent_classes=', '.join(parent_classes),
        class_doc=class_doc,
        class_attributes=''.join(class_attributes),
        class_methods=''.join(class_methods),
        class_properties=''.join(class_properties),
        class_classes=''.join(class_classes),
        indent=indent
    )
    output = ''.join(output)

    for item in (
        class_attributes,
        class_methods,
        class_properties,
        class_classes
    ):
        if item:
            break

    else:
        output += indent + '    pass'

    return output


def _build_prop(prop_name, prop, indent):
    indent += '    '
    prop_doc = inspect.getdoc(prop)
    if prop_doc in (None, 'None'):
        prop_doc = indent + '    NO DOC'
    else:
        prop_doc = '\n'.join(
            indent + '     ' + line for line in prop_doc.split('\n')
        )

    output = PROPGET_TEMPLATE.format(
        prop_name=prop_name,
        prop_doc=prop_doc,
        indent=indent
    )

    try:
        if prop.fset:
            output += PROPSET_TEMPLATE.format(
                prop_name=prop_name,
                indent=indent
            )
    except AttributeError:
        output += PROPSET_TEMPLATE.format(
            prop_name=prop_name,
            indent=indent
        )

    return output


def _build_func(func_name, func, indent):
    func_doc = inspect.getdoc(func)

    if func_doc in (None, 'None'):
        func_doc = indent + '        NO DOC'
    else:
        func_doc = '\n'.join(
            indent + '        ' + line for line in func_doc.split('\n')
        )

    func_args = inspect.formatargspec(inspect.getargspec(func))
    output = FUNC_TEMPLATE.format(
        func_name=func_name,
        func_args=func_args,
        func_doc=func_doc,
        indent=indent
    )
    return output


def _build_meth(meth_name, meth, indent):
    meth_doc = inspect.getdoc(meth)

    if meth_doc in (None, 'None'):
        meth_doc = indent + '        NO DOC'
    else:
        meth_doc = '\n'.join(
            indent + '        ' + line for line in meth_doc.split('\n')
        )
    try:
        meth_args = inspect.formatargspec(inspect.getargspec(meth))
    except TypeError:
        meth_args = ['self']

        if meth_name in (
            '__rand__',
            '__ror__',
            '__or__',
            '__and__',
            '__rxor__',
            '__xor__',
            '__ne__',
            '__eq__'
        ):
            meth_args += ['other']

        elif meth_name == '__getattr__':
            meth_args += ['key']

        elif meth_name == '__getitem__':
            meth_args += ['item']
        elif meth_name in ('__setattr__', '__setitem__'):
            meth_args += ['key', 'value']

        else:
            for param_name in meth_doc.split(':'):
                if param_name.startswith('param '):
                    param_name = param_name.split(' ')[-1]
                    meth_args += [param_name]

        meth_args = ', '.join(arg.strip() for arg in meth_args if arg.strip())

    output = METH_TEMPLATE.format(
        meth_name=meth_name,
        meth_args=meth_args,
        meth_doc=meth_doc,
        indent=indent
    )
    return output


class build_bootstrap(Command):
    description = 'bootstrap builder'

    def finalize_options(self):
        pass

    def initialize_options(self):
        pass

    def run(self):
        builder = self.distribution.get_command_obj('build')
        build_path = builder.build_lib
        build_ext = self.distribution.get_command_obj('build_ext')
        extension = self.distribution.ext_modules[0]
        ext_path = build_ext.get_ext_fullpath(extension.name)

        mod = imp.load_dynamic(
            '',
            ext_path
        )

        output = []
        end_output = []

        for key, value in mod.__dict__.items():

            if key.startswith('__') or key in ('copyfile', 'get_distribution'):
                continue

            if inspect.isclass(value):
                output += [_build_class(key, value, '    ')]
            elif inspect.isfunction(value):
                output += [_build_func(key, value, '    ')]
            elif not key.startswith('_'):
                value = str(type(value)).split("'")[1]

                if '' in value:
                    value = value.split('.')[-1]

                if value in (
                    'module',
                    'property',
                    'builtin_function_or_method'
                ):
                    continue

                end_output += ['    ' + key + ' = {0}()\n'.format(value)]
        output = ''.join(output + end_output)

        bootstrap = os.path.join(build_path, '.py')

        with open(bootstrap, 'w') as f:
            f.write(HEADER)
            f.write(output)

