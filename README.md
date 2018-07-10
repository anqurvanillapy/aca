# Aca

> *Aca, a functional programming language, and shitty toy.*

Aca is a toy functional programming language initially inspired by ISWIM.  The
interpreter is currently written in Python.

## Install

Not on PyPI.  Install it manually with the setup script.

## Example

```bash
$ cat foo.aca
let main =
    dechurch (\x . x) 3
$ aca foo.aca
42
$ aca foo.aca -S
(lambda x: dechurch(x))((lambda x: x)((lambda f: lambda x: (f(f(f(x)))))))
```

## Already done

* Lambda calculus
* Encoding and decoding of Church numerals
* Local declarations

## Goals

- Before `v1.0.0`:
    + Untyped lambda calculus
    + Standard library for basic datatypes and operations
- `v1.0.0`:
    + Builtin binary operators
- `v2.0.0`:
    + System F

## License

MIT
