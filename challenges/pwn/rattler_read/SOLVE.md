# Rattler Read


## Initial Investigation
A `RestrictedPython` pyjail. After looking at the code, you should notice that

+ `_` access is blocked (alongside `getattr` and others)
+ imports are blocked

Digging deeper, one can find that `RestrictedPython` itself imports `random`, `math` and `string`. See source [here](https://github.com/zopefoundation/RestrictedPython/blob/b82d5821d1669ff56b4264c39b01e658a62875e9/src/RestrictedPython/Utilities.py#L15). This means we can use these even without imports.

With extremely limited property access, I feel that the best solution is to investigate the modules we have available and see if there exists additional functionality we can rely on to do code execution.


## Digging into imports

Looking into the `random` [module](https://github.com/python/cpython/blob/3.11/Lib/random.py#L57), we find that it imports `os` as `_os`. Unfortunately, the `_` prefix prevents us from using it. If we had access to this, we could call `os.system`.

Looking into the `string` module, we find an [interesting method](https://docs.python.org/3/library/string.html#string.Formatter.get_field) on the `Formatter` class:

> `get_field(field_name, args, kwargs)`
> 
> Given field_name as returned by parse() (see above), convert it to an object to be formatted.

This is exciting because it allows us to access `_` properties!

## Final Payload

Now, we can chain these two facts together into our payload!

```py
print(string.Formatter().get_field("0._os", [random], kwargs={})[0].system("cat /flag.txt"))
```

The first part, `string.Formatter().get_field` allows us to access properties with an `_` prefix. The second part, `random._os.system(...)`, is our command execution.