# -*- coding: utf-8 -*-
import ast
import imp
import os
import sys

class Macroator(ast.NodeTransformer):
    def __init__(self, macros=None):
        super(Macroator, self).__init__()
        self.macros = macros or {}

    def visit_FunctionDef(self, func):
        decorators = list(reversed(func.decorator_list))
        decorators = [x.id if isinstance(x, ast.Name) else x.func.id for x in decorators]
        for d in decorators:
            if d in self.macros:
                func.decorator_list.pop(-1)
                func = self.macros[d](func)
            else:
                break
        return func

class Trampoline(ast.NodeTransformer):
    def visit_Return(self, node):
        if isinstance(node.value, ast.Call):
            node.value = ast.Dict(
                keys=[ast.Str(n) for n in ('func', 'args', 'keywords', '*args', '**kwargs')],
                values=[node.value.func,
                ast.Tuple(node.value.args, ast.Load()),
                ast.Tuple([ast.Tuple([ast.Str(kw.arg), kw.value], ast.Load()) for kw in node.value.keywords], ast.Load()),
                node.value.starargs or ast.Name('None', ast.Load()),
                node.value.kwargs or ast.Name('None', ast.Load()),],
                )
            node = ast.fix_missing_locations(node)
            self.did_alter = True
        else:
            self.did_alter = False
        return node

path = os.path.dirname(sys.modules[__name__].__dict__.get('__file__', ''))
fname = os.path.join(path, 'macro_trampoline_decorator.py')
trampoline_decorator = ast.parse(open(fname, 'rb').read(), 'macro_trampoline_decorator.py')
trampoline_decorator = trampoline_decorator.body[0]
# this is an impossible name in python, guaranteeing no name collisions
trampoline_decorator.name = '★trampoline_decorator'

class TrampolineMacro(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        t = Trampoline()
        node = t.visit(node)
        if t.did_alter:
            node.decorator_list.append(ast.Name(trampoline_decorator.name, ast.Load()))
            node = ast.fix_missing_locations(node)
            return [trampoline_decorator, node]
        else:
            return node


class MacroImporter(object):

    @staticmethod
    def find_module(name, path=None):
        file, path, description = imp.find_module(name, path)
        return MacroLoader(name, file, path, description)

class MacroLoader(object):

    def __init__(self, name, file, path, description):
        self.name = name
        self.file = file
        self.path = path
        self.description = description

    def load_module(self, path):
        if self.description[2] != imp.PY_SOURCE:
            return imp.load_module(self.name, self.file, self.path, self.description)
        tree = ast.parse(self.file.read(), self.path)
        m = Macroator(macros={'magic_trampoline':TrampolineMacro().visit})
        tree = m.visit(tree)
        mod = imp.new_module(self.name)
        code = compile(tree, self.path, 'exec', dont_inherit=True)
        exec (code) in mod.__dict__
        sys.modules[self.name] = mod
        return mod

def install_import_hook():
    if MacroImporter not in sys.meta_path:
        sys.meta_path.append(MacroImporter)

install_import_hook()
