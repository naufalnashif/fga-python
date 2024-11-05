def calculate(operation, x, y):
    '''operation = [add, sub, mul, div]'''
    if operation == "Addition":
        return x+y
    elif operation == "Subtraction":
        if x>y:
            return x-y
        else:
            return y-x
    elif operation == "Multiplication":
        return x*y
    elif operation == "Division":
        if y != 0:
            return x/y
        else:
            s = "Cannot Divided by Zero"
            return s