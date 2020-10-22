from sympy import *
dummy = symbols("dummy")


def add_to(eq, sym):
    return Eq(eq.lhs + sym, eq.rhs + sym).simplify()


def multiply_to(eq, sym):
    return Eq(eq.lhs * sym, eq.rhs * sym).simplify()


l0, l1, l2, xs, ys, xf, yf, x0, y0, x2, y2 = symbols('l0 l1 l2 xs ys xf yf x0 y0 x2 y2')

eql0o = Eq(l0**2, (x0 - xs)**2 + (y0 - ys)**2).expand()
eql2o = Eq(l2**2, (x2 - xf)**2 + (y2 - yf)**2).expand()
eql1o = Eq(l1**2, (xf - xs)**2 + (yf - ys)**2).expand()
# eql1.radsimp()
# print()
# print(eql0)
# print(eql2)
# print(eql1)

eql0 = add_to(eql0o, -1*(x0**2 - 2*x0*xs + y0**2 - 2*y0*ys))
eql2 = add_to(eql2o, -1*(x2**2 - 2*x2*xf + y2**2 - 2*y2*yf))

# print()
# print(eql0)
# print(eql2)
# print(eql1o)

eql1 = eql1o.subs(eql0.lhs, eql0.rhs)
eql1 = eql1.subs(eql2.lhs, eql2.rhs)
eql1 = add_to(eql1, -1*(l0**2 + l2**2 - x0**2 - x2**2 - y0**2 - y2**2 ))
eql1 = multiply_to(eql1, 1/2)

# g = -0.5*l0**2 + 0.5*l1**2 - 0.5*l2**2 + 0.5*x0**2 + 0.5*x2**2 + 0.5*y0**2 + 0.5*y2**2
g = symbols("g")
fg = -0.5*l0**2 + 0.5*l1**2 - 0.5*l2**2 + 0.5*x0**2 + 0.5*x2**2 + 0.5*y0**2 + 0.5*y2**2
eql1 = eql1.subs(fg, g)
eql1 = eql1.subs(x0, 0)
eql1 = eql1.subs(y0, 0)
eql1 = add_to(eql1, -1*x2*xf)
eql1 = multiply_to(eql1, 1/y2)

intersection = eql2o.subs(yf, eql1.rhs)


print(intersection)
xf_solutions = solve(intersection, xf)
print(xf_solutions)
print(len(xf_solutions))

# print(solve(eql0, xf**2 + yf**2, set=True))
