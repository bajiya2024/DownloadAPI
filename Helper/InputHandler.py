import sys


"""
getUrlInput handle url inputs if url
"""
fields = ["url"]
def getUrlInput(params):
    inputs = {}
    err_msg = ""
    for f in fields:
        if f in params and params.get(f):
            inputs[f] = params.get(f)
        else:
            return ("Please provide param : %s" % f, inputs)
    return (err_msg, inputs)



"""
getid function handle id input
"""
def getid(params):
    inputs = {}
    err_msg = ""
    for f in ["id"]:
        if f in params and params.get(f):
            inputs[f] = params.get(f)
        else:
            return ("Please provide param : %s" % f, inputs)
    return (err_msg, inputs)
