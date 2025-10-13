def make_repr(instance: object, *argv: property) -> str:
    def display_prop(p: property) -> str:
        if p.fget is not None:
            return f"{p.fget.__name__}={p.fget(instance)!r}"
        raise RuntimeError("Property has no fget")

    return "{}({})".format(type(instance).__qualname__, ", ".join(display_prop(p) for p in argv))


def make_repr_from_data(instance: object) -> str:
    kws = [f"{key}={value!r}" for key, value in instance.__dict__.items()]
    return "{}({})".format(type(instance).__qualname__, ", ".join(kws))
