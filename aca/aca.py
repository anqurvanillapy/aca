#!/usr/bin/env python3
# pylint: disable=W0123, C0103, C0330

"""
Aca, a functional programming language, and shitty toy.

Full grammar:
TOP     : decl | use
decl    : "let" IDENT "=" expr
expr    : (factor)+
factor  : lambda | IDENT | INT | "(" expr ")"
lambda  : "(" "\\" (IDENT)+ "." (factor)+ ")"
use     : "use" IDENT
"""

import sys
from enum import Enum, auto
from collections import deque
from pkgutil import get_data

__VERSION__ = "0.3.0"

# TODO (before v1.0.0):
# 1. Argument issues
# 2. Standard library


class TkType(Enum):
    """Token type"""

    EOF = auto()
    CMT = auto()
    LMULCMT = auto()
    RMULCMT = auto()
    INT = auto()
    IDENT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LAMBDA = auto()
    FNDOT = auto()
    LET = auto()
    LETREC = auto()
    ASSIGN = auto()
    USE = auto()


RESERVED = {
    "--": TkType.CMT,
    "{-": TkType.LMULCMT,
    "-}": TkType.RMULCMT,
    "\\": TkType.LAMBDA,
    ".": TkType.FNDOT,
    "(": TkType.LPAREN,
    ")": TkType.RPAREN,
    "let": TkType.LET,
    "letrec": TkType.LETREC,
    "=": TkType.ASSIGN,
    "use": TkType.USE,
}


class Token:
    """Token object"""

    def __init__(self, ty, val):
        self.type = ty
        self.val = val

    def __str__(self):
        return "Token({}, {})".format(self.type, repr(self.val))

    def __repr__(self):
        return self.__str__()


class Lexer:
    """Aca lexical analyzer"""

    def __init__(self, fname="", src=""):
        self.src = src
        self.pos = 0
        self.cur_char = self.src[self.pos] if src else None
        self.len = len(self.src)
        self.fname = fname

    def fromstdin(self):
        """Read source from stdin once"""
        self.src = input()
        self.pos = 0
        self.cur_char = self.src[self.pos] if self.src else None
        self.len = len(self.src)

    def error(self):
        """Tokenize error"""
        raise ValueError(
            "invalid character `{}' at {} in file `{}'".format(
                self.pos, self.cur_char, self.fname
            )
        )

    def forward(self):
        """Increment pos and current char"""
        self.pos += 1
        if self.pos < self.len:
            self.cur_char = self.src[self.pos]
        else:
            self.cur_char = None

    def whitespace(self):
        """Skip whitespaces"""
        while self.cur_char and self.cur_char.isspace():
            self.forward()

    def number(self):
        """Get a multidigit number"""
        ret = ""
        while self.cur_char and self.cur_char.isdigit():
            ret += self.cur_char
            self.forward()
        return Token(TkType.INT, int(ret))

    def word(self):
        """Get a word token (a reserved word or identifier)"""
        ret = ""
        while self.cur_char and (
            self.cur_char.isalnum() or self.cur_char in ("_", "'")
        ):
            ret += self.cur_char
            self.forward()
        if ret in RESERVED:
            return Token(RESERVED[ret], ret)
        return Token(TkType.IDENT, ret)

    def cmt(self):
        """Single-line and multiline comment"""
        if self.cur_char == "-":
            self.forward()
            if self.cur_char and self.cur_char == "-":
                while self.cur_char and self.cur_char != "\n":
                    self.forward()
                return
        elif self.cur_char == "{":
            if self.tryeats("-"):
                while not self.tryeats("-}"):
                    pass
                return
        self.error()

    def tryeats(self, s):
        """Try to match a sequence of characters, namely a string"""
        for c in s:
            self.forward()
            if self.cur_char and self.cur_char == c:
                continue
            return False
        self.forward()
        return True

    def next_tk(self):
        """Tokenizer"""
        while self.cur_char:
            c = self.cur_char

            if c.isspace():
                self.whitespace()
                continue

            if c in ("-", "{"):
                self.cmt()
                continue

            if c.isdigit():
                return self.number()

            if c.isalpha() or c in "_":
                return self.word()

            if c in RESERVED:
                tk = Token(RESERVED[c], c)
                self.forward()
                return tk

            self.error()

        return Token(TkType.EOF, None)


class Interpreter:
    """Aca parser and interpreter"""

    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_tk = self.lexer.next_tk()
        self.args = set()
        self.ctx = {}

    def error(self):
        """Parse error"""
        raise SyntaxError(
            "invalid syntax at {} in file `{}'".format(
                self.lexer.pos, self.lexer.fname
            )
        )

    def eat(self, tktype):
        """Match a token with a specific type"""
        if self.cur_tk.type == tktype:
            self.cur_tk = self.lexer.next_tk()
        else:
            self.error()

    def eatin(self, types):
        """Match a token with one of some specific types"""
        if self.cur_tk.type in types:
            self.cur_tk = self.lexer.next_tk()
        else:
            self.error()

    def eatseq(self, types):
        """Match some tokens sequentially with specific types"""
        for t in types:
            self.eat(t)

    def decl(self):
        """Local declaration"""
        self.eat(TkType.LET)
        var = self.cur_tk.val
        self.eat(TkType.IDENT)
        if var in self.ctx:
            self.error()
        self.eat(TkType.ASSIGN)
        val = self.expr()
        self.ctx[var] = val
        self.args.clear()

    def expr(self):
        """Expression"""
        fg = self.factor()
        val = None
        factors = []
        try:
            val = next(fg)
        except StopIteration:
            self.error()
        for f in fg:
            factors.append(f)
        if factors:
            fs = factors.pop()
            while factors:
                fs = "{}({})".format(factors.pop(), fs)
            val = "{}({})".format(val, fs)
        return val

    def factor(self):
        """Factor"""
        while True:
            tk = self.cur_tk
            if tk.type in (TkType.RPAREN, TkType.LET, TkType.EOF):
                break
            if tk.type == TkType.INT:
                self.eat(TkType.INT)
                yield enchurch(int(tk.val))
            elif tk.type == TkType.IDENT:
                self.eat(TkType.IDENT)
                if tk.val in self.ctx:
                    yield self.ctx[tk.val]
                elif tk.val in self.args:
                    yield "({})".format(tk.val)
            elif tk.type == TkType.LPAREN:
                self.eat(TkType.LPAREN)
                if self.cur_tk.type == TkType.LAMBDA:
                    yield self.lamb()
                else:
                    val = self.expr()
                    self.eat(TkType.RPAREN)
                    yield val
            else:
                self.error()

    def lamb(self):
        """Lambda calculus"""
        a = deque()
        depth = 0
        self.eat(TkType.LAMBDA)
        while True:
            tk = self.cur_tk
            if tk.type == TkType.IDENT and tk.val not in self.args:
                self.eat(TkType.IDENT)
                self.args.add(tk.val)
                a.appendleft("(lambda {}:".format(tk.val))
                depth += 1
                continue
            elif tk.type == TkType.FNDOT:
                self.eat(TkType.FNDOT)
                break
            else:
                self.error()
        for t in self.factor():
            a.append(t)
        for _ in range(depth):
            a.append(")" * depth)
        self.eat(TkType.RPAREN)
        return " ".join(a)

    def include(self, fname, src):
        """Interruptedly include and parse a file"""
        old = self.funwind()
        self.lexer = Lexer(fname, src)
        self.cur_tk = self.lexer.next_tk()
        self.parse()
        self.lexer, self.cur_tk = old

    def use(self):
        """Use declarations from other source files"""
        self.eat(TkType.USE)
        fname = "{}.aca".format(self.cur_tk.val)
        self.eat(TkType.IDENT)
        with open(fname, "r") as f:
            self.include(fname, f.read())

    def funwind(self):
        """Get a backup for source file unwinding"""
        return self.lexer, self.cur_tk

    def parse(self):
        """Start parsing"""
        while self.cur_tk.type != TkType.EOF:
            if self.cur_tk.type == TkType.LET:
                self.decl()
            elif self.cur_tk.type == TkType.USE:
                self.use()
            else:
                self.error()

    def stdlib(self):
        """Init stdlib"""
        self.ctx["dechurch"] = "(lambda x: dechurch(x))"
        lib = "stdlib.aca"
        self.include(lib, get_data(__name__, lib).decode("utf-8"))

    def run(self, noeval=False):
        """Start the interpreter"""
        self.stdlib()
        self.parse()
        val = self.ctx["main"]
        print(val if noeval else eval(val))

    def repl(self, noeval=False):
        """Start the REPL"""
        version()
        if noeval:
            print("(`noeval' mode is on)")
        self.stdlib()
        n = 1
        while True:
            try:
                self.lexer.fname = "<stdin> #{}".format(n)
                print("> ", end="")
                self.lexer.fromstdin()
                self.cur_tk = self.lexer.next_tk()
                if self.cur_tk.type == TkType.IDENT:
                    val = self.ctx[self.cur_tk.val]
                    self.cur_tk = self.lexer.next_tk()
                    self.eat(TkType.EOF)
                    print(val if noeval else eval(val))
                else:
                    self.parse()
                n += 1
            except SyntaxError as e:
                print("SyntaxError: {}".format(e))
            except ValueError as e:
                print("SyntaxError: {}".format(e))
            except KeyError as e:
                print(
                    "KeyError: cannot find declaration of `{}'".format(
                        str(e)[1:-1]
                    )
                )
            except EOFError:
                break


def enchurch(n):
    """Encode Church numerals"""
    assert n >= 0
    if n:
        return "(lambda f: lambda x: {}(x){})".format("(f" * n, ")" * n)
    return "(lambda x: x)"


def dechurch(a):
    """Decode Church numerals"""
    if a(0) == 0:
        return 0
    return a(lambda x: x + 1)(0)


def usage():
    """Usage of aca command"""
    error("Usage: aca FILENAME [-S] [-h|--help] [-v|--version]")


def error(msg):
    """Top-level error"""
    print(msg, file=sys.stderr)
    sys.exit(1)


def version():
    """Print version"""
    print("Aca {}".format(__VERSION__))


def main():
    """Start REPL or run the script"""
    noeval = False
    fname = None
    try:
        for arg in sys.argv[1:]:
            if arg == "-S":
                assert not noeval
                noeval = True
            elif arg in ("-v", "--version"):
                version()
                return
            elif arg in ("-h", "--help"):
                assert False
            else:
                assert not fname
                fname = arg
        if fname:
            with open(fname, "r") as f:
                lexer = Lexer(fname, f.read())
                interp = Interpreter(lexer)
                interp.run(noeval)
        else:
            lexer = Lexer("<stdin>")
            interp = Interpreter(lexer)
            interp.repl(noeval)
    except AssertionError:
        usage()
    except SyntaxError as e:
        error("SyntaxError: {}".format(e))
    except ValueError as e:
        error("SyntaxError: {}".format(e))
    except KeyError as e:
        error("KeyError: cannot find declaration of `{}'".format(str(e)[1:-1]))


if __name__ == "__main__":
    main()
