"""bytecode manipulation"""


def replace_functions(co, repl):
    """replace the functions in the code object co with those from repl.
       repl can either be a code object or a source code string.
       returns a new code object.
    """
    import new
    if isinstance(repl, basestring):
        repl = compile(repl, co.co_name, "exec")

    name2repl = {}
    for c in repl.co_consts:
        if isinstance(c, type(repl)):
            name2repl[c.co_name] = c

    consts = list(co.co_consts)
    for i in range(len(consts)):
        c = consts[i]
        if isinstance(c, type(repl)):
            if c.co_name in name2repl:
                consts[i] = name2repl[c.co_name]
                print "codehack: replaced %s in %s" % (c.co_name, co.co_filename)

    return new.code(co.co_argcount, co.co_nlocals, co.co_stacksize,
                     co.co_flags, co.co_code, tuple(consts), co.co_names,
                     co.co_varnames, co.co_filename, co.co_name,
                     co.co_firstlineno, co.co_lnotab,
                     co.co_freevars, co.co_cellvars)
