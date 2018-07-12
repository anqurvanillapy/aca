# Aca

> *Aca, a functional programming language, and shitty toy.*

Aca is a toy functional programming language initially inspired by ISWIM.  The
interpreter is currently written in Python.

## Install

```bash
$ pip install acalang
```

## Example

1. Command line usage

```bash
$ cat foo.aca
let main =
    dechurch 3

$ aca foo.aca
3

$ aca foo.aca -S    # `noeval' mode
(lambda x: dechurch(x))((lambda x: x)((lambda f: lambda x: (f(f(f(x)))))))

$ aca       # REPL
$ aca -S    # REPL with `noeval'
```

2. Lambda calculus

```
let main =
    (\x y f. f x y)
```

3. Sugar for Church numerals

```
let main = 0

-- This is identical to
{-
let main =
    (\x . x)
-}
```

4. Builtin function `dechurch` for trying to decode a natural number

```
-- Yields no lambdas but value `42` on the screen
let main =
    dechurch 42
```

5. Simple module import with `use`

```bash
$ foo.aca
let foo = 42

$ bar.aca
use foo

let main =
    dechurch foo

$ aca bar.aca
42
```

## Goals

- Before `v1.0.0`:
    + Untyped lambda calculus
    + Standard library for basic datatypes and operations
- `v1.0.0`:
    + Simply typed lambda calculus
- `v2.0.0`:
    + System F

## License

MIT
