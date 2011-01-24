# -*- coding: utf-8 -*-

#legal_one_filter = ("__doc__", "__name__", "__package__", "atan2", "copysign", "e", "fmod", "frexp", "fsum", "hypot", "isinf", "isnan", "ldexp", "modf", "pi", "pow")
#legal_one = tuple( [elem for elem in dir(math) if elem not in legal_one_filter] )

legal_one = ('acos', 'acosh', 'asin', 'asinh', 'atan', 'atanh', 'cos', 'cosh', 'exp', 'log', 'log10', 'sin', 'sinh', 'sqrt', 'tan', 'tanh')
legal_two = ('+', '-', '*', '/', '//', '**')
legal_op = legal_two + legal_one
legal_other = ("x", "e", "pi")
legal_all = legal_other + legal_op
