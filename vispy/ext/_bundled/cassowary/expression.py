from __future__ import print_function, unicode_literals, absolute_import, division

from .error import InternalError
from .utils import approx_equal, REQUIRED, STRONG, repr_strength

###########################################################################
# Variables
#
# Variables are the atomic unit of linear programming, describing the
# quantities that are to be solved and constrained.
###########################################################################

class AbstractVariable(object):
    def __init__(self, name):
        self.name = name
        self.is_dummy = False
        self.is_external = False
        self.is_pivotable = False
        self.is_restricted = False

    def __rmul__(self, x):
        return self.__mul__(x)

    def __mul__(self, x):
        if isinstance(x, (float, int)):
            return Expression(self, x)
        elif isinstance(x, Expression):
            if x.is_constant:
                return Expression(self, value=x.constant)
            else:
                raise TypeError('Cannot multiply variable by non-constant expression')
        else:
            raise TypeError('Cannot multiply variable by object of type %s' % type(x))

    def __truediv__(self, x):
        return self.__div__(x)

    def __div__(self, x):
        if isinstance(x, (float, int)):
            if approx_equal(x, 0):
                raise ZeroDivisionError()
            return Expression(self, 1.0 / x)
        elif isinstance(x, Expression):
            if x.is_constant:
                return Expression(self, value=1.0/x.constant)
            else:
                raise TypeError('Cannot add non-constant expression to variable')
        else:
            raise TypeError('Cannot divide variable by object of type %s' % type(x))

    def __radd__(self, x):
        return self.__add__(x)

    def __add__(self, x):
        if isinstance(x, (int, float)):
            return Expression(self, constant=x)
        elif isinstance(x, Expression):
            return Expression(self) + x
        elif isinstance(x, AbstractVariable):
            return Expression(self) + Expression(x)
        else:
            raise TypeError('Cannot add object of type %s to expression' % type(x))

    def __rsub__(self, x):
        if isinstance(x, (int, float)):
            return Expression(self, -1.0, constant=x)
        elif isinstance(x, Expression):
            return x - Expression(self)
        elif isinstance(x, AbstractVariable):
            return Expression(x) - Expression(self)
        else:
            raise TypeError('Cannot subtract variable from object of type %s' % type(x))

    def __sub__(self, x):
        if isinstance(x, (int, float)):
            return Expression(self, constant=-x)
        elif isinstance(x, Expression):
            return Expression(self) - x
        elif isinstance(x, AbstractVariable):
            return Expression(self) - Expression(x)
        else:
            raise TypeError('Cannot subtract object of type %s from variable' % type(x))


class Variable(AbstractVariable):
    def __init__(self, name, value=0.0):
        super(Variable, self).__init__(name)
        self.value = float(value)
        self.is_external = True

    def __repr__(self):
        return '%s[%s]' % (self.name, self.value)

    __hash__ = object.__hash__

    def __eq__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.EQ, other)
        else:
            raise TypeError('Cannot compare variable with object of type %s' % type(other))

    def __lt__(self, other):
        # < and <= are equivalent in the API; it's effectively true
        # due to float arithmetic, and it makes the API a little less hostile,
        # because all the comparison operators exist.
        return self.__le__(other)

    def __le__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.LEQ, other)
        else:
            raise TypeError('Cannot compare variable with object of type %s' % type(other))

    def __gt__(self, other):
        # > and >= are equivalent in the API; it's effectively true
        # due to float arithmetic, and it makes the API a little less hostile,
        # because all the comparison operators exist.
        return self.__ge__(other)

    def __ge__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.GEQ, other)
        else:
            raise TypeError('Cannot compare variable with object of type %s' % type(other))


class DummyVariable(AbstractVariable):
    def __init__(self, number):
        super(DummyVariable, self).__init__(name='d%s' % (number))
        self.is_dummy = True
        self.is_restricted = True

    def __repr__(self):
        return '%s:dummy' % self.name


class ObjectiveVariable(AbstractVariable):
    def __init__(self, name):
        super(ObjectiveVariable, self).__init__(name)

    def __repr__(self):
        return '%s:obj' % self.name


class SlackVariable(AbstractVariable):
    def __init__(self, prefix, number):
        super(SlackVariable, self).__init__(name='%s%s' % (prefix, number))
        self.is_pivotable = True
        self.is_restricted = True

    def __repr__(self):
        return '%s:slack' % self.name

###########################################################################
# Expressions
#
# Expressions are combinations of variables with multipliers and constants
###########################################################################


class Expression(object):
    def __init__(self, variable=None, value=1.0, constant=0.0):
        assert isinstance(constant, (float, int))
        assert variable is None or isinstance(variable, AbstractVariable)

        self.constant = float(constant)
        self.terms = {}

        if variable:
            self.set_variable(variable, float(value))

    def __repr__(self):
        parts = []
        if not approx_equal(self.constant, 0.0) or self.is_constant:
            parts.append(repr(self.constant))
        for clv, coeff in sorted(self.terms.items(), key=lambda x:repr(x)):
            if approx_equal(coeff, 1.0):
                parts.append(repr(clv))
            else:
                parts.append(repr(coeff) + "*" + repr(clv))
        return ' + '.join(parts)

    @property
    def is_constant(self):
        return not self.terms

    def clone(self):
        expr = Expression(constant=self.constant)
        for clv, value in self.terms.items():
            expr.set_variable(clv, value)
        return expr

    ######################################################################
    # Mathematical operators
    ######################################################################

    def __rmul__(self, x):
        return self.__mul__(x)

    def __mul__(self, x):
        if isinstance(x, Expression):
            if self.is_constant:
                result = x * self.constant
            elif x.is_constant:
                result = self * x.constant
            else:
                raise TypeError('Cannot multiply expression by non-constant')
        elif isinstance(x, Variable):
            if self.is_constant:
                result = Expression(x, self.constant)
            else:
                raise TypeError('Cannot multiply a variable by a non-constant expression')
        elif isinstance(x, (float, int)):
            result = Expression(constant=self.constant * x)
            for clv, value in self.terms.items():
                result.set_variable(clv, value * x)
        else:
            raise TypeError('Cannot multiply expression by object of type %s' % type(x))
        return result

    def __truediv__(self, x):
        return self.__div__(x)

    def __div__(self, x):
        if isinstance(x, (float, int)):
            if approx_equal(x, 0):
                raise ZeroDivisionError()
            result = Expression(constant=self.constant / x)
            for clv, value in self.terms.items():
                result.set_variable(clv, value / x)
        else:
            if x.is_constant:
                result = self / x.constant
            else:
                raise TypeError('Cannot divide expression by non-constant')
        return result

    def __radd__(self, x):
        return self.__add__(x)

    def __add__(self, x):
        if isinstance(x, Expression):
            result = self.clone()
            result.add_expression(x, 1.0)
            return result
        elif isinstance(x, Variable):
            result = self.clone()
            result.add_variable(x, 1.0)
            return result
        elif isinstance(x, (int, float)):
            result = self.clone()
            result.add_expression(Expression(constant=x), 1.0)
            return result
        else:
            raise TypeError('Cannot add object of type %s to expression' % type(x))

    def __rsub__(self, x):
        if isinstance(x, Expression):
            result = self.clone()
            result.multiply(-1.0)
            result.add_expression(x, 1.0)
            return result
        elif isinstance(x, Variable):
            result = self.clone()
            result.multiply(-1.0)
            result.add_variable(x, 1.0)
            return result
        elif isinstance(x, (int, float)):
            result = self.clone()
            result.multiply(-1.0)
            result.add_expression(Expression(constant=x), 1.0)
            return result
        else:
            raise TypeError('Cannot subtract object of type %s from expression' % type(x))

    def __sub__(self, x):
        if isinstance(x, Expression):
            result = self.clone()
            result.add_expression(x, -1.0)
            return result
        elif isinstance(x, Variable):
            result = self.clone()
            result.add_variable(x, -1.0)
            return result
        elif isinstance(x, (int, float)):
            result = self.clone()
            result.add_expression(Expression(constant=x), -1.0)
            return result
        else:
            raise TypeError('Cannot subtract object of type %s from expression' % type(x))

    ######################################################################
    # Mathematical operators
    ######################################################################

    __hash__ = object.__hash__

    def __eq__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.EQ, other)
        else:
            raise TypeError('Cannot compare expression with object of type %s' % type(other))

    def __lt__(self, other):
        # < and <= are equivalent in the API; it's effectively true
        # due to float arithmetic, and it makes the API a little less hostile,
        # because all the comparison operators exist.
        return self.__le__(other)

    def __le__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.LEQ, other)
        else:
            raise TypeError('Cannot compare expression with object of type %s' % type(other))

    def __gt__(self, other):
        # > and >= are equivalent in the API; it's effectively true
        # due to float arithmetic, and it makes the API a little less hostile,
        # because all the comparison operators exist.
        return self.__ge__(other)

    def __ge__(self, other):
        if isinstance(other, (Expression, Variable, float, int)):
            return Constraint(self, Constraint.GEQ, other)
        else:
            raise TypeError('Cannot compare expression with object of type %s' % type(other))

    ######################################################################
    # Internal mechanisms
    ######################################################################

    def add_expression(self, expr, n=1.0, subject=None, solver=None):
        if isinstance(expr, AbstractVariable):
            expr = Expression(variable=expr)

        self.constant = self.constant + n * expr.constant
        for clv, coeff in expr.terms.items():
            self.add_variable(clv, coeff * n, subject, solver)

    def add_variable(self, v, cd=1.0, subject=None, solver=None):
        # print 'expression: add_variable', v, cd
        coeff = self.terms.get(v)
        if coeff:
            new_coefficient = coeff + cd
            if approx_equal(new_coefficient, 0.0):
                if solver:
                    solver.note_removed_variable(v, subject)
                self.remove_variable(v)
            else:
                self.set_variable(v, new_coefficient)
        else:
            if not approx_equal(cd, 0.0):
                self.set_variable(v, cd)
                if solver:
                    solver.note_added_variable(v, subject)

    def set_variable(self, v, c):
        self.terms[v] = float(c)

    def remove_variable(self, v):
        del self.terms[v]

    def any_pivotable_variable(self):
        if self.is_constant:
            raise InternalError('any_pivotable_variable called on a constant')

        retval = None
        for clv, c in self.terms.items():
            if clv.is_pivotable:
                retval = clv
                break

        return retval

    def substitute_out(self, outvar, expr, subject=None, solver=None):
        multiplier = self.terms.pop(outvar)
        self.constant = self.constant + multiplier  * expr.constant

        for clv, coeff in expr.terms.items():
            old_coefficient = self.terms.get(clv)
            if old_coefficient:
                new_coefficient = old_coefficient + multiplier * coeff
                if approx_equal(new_coefficient, 0):
                    solver.note_removed_variable(clv, subject)
                    del self.terms[clv]
                else:
                    self.set_variable(clv, new_coefficient)
            else:
                self.set_variable(clv, multiplier * coeff)
                if solver:
                    solver.note_added_variable(clv, subject)

    def change_subject(self, old_subject, new_subject):
        self.set_variable(old_subject, self.new_subject(new_subject))

    def multiply(self, x):
        self.constant = self.constant * float(x)
        for clv, value in self.terms.items():
            self.set_variable(clv, value * x)

    def new_subject(self, subject):
        # print "new_subject", subject
        value = self.terms.pop(subject)
        reciprocal = 1.0 / value
        self.multiply(-reciprocal)
        return reciprocal

    def coefficient_for(self, clv):
        return self.terms.get(clv, 0.0)


###########################################################################
# Constraint
#
# Constraints are the restrictions on linear programming; an equality or
# inequality between two expressions.
###########################################################################

class AbstractConstraint(object):
    def __init__(self, strength, weight=1.0):
        self.strength = strength
        self.weight = weight
        self.is_edit_constraint = False
        self.is_inequality = False
        self.is_stay_constraint = False

    @property
    def is_required(self):
        return self.strength == REQUIRED

    def __repr__(self):
        return '%s:{%s}(%s)' % (repr_strength(self.strength), self.weight, self.expression)

class EditConstraint(AbstractConstraint):
    def __init__(self, variable, strength=STRONG, weight=1.0):
        super(EditConstraint, self).__init__(strength, weight)
        self.variable = variable
        self.expression = Expression(variable, -1.0, variable.value)
        self.is_edit_constraint = True

    def __repr__(self):
        return 'edit:%s' % super(EditConstraint, self).__repr__()


class StayConstraint(AbstractConstraint):
    def __init__(self, variable, strength=STRONG, weight=1.0):
        super(StayConstraint, self).__init__(strength, weight)
        self.variable = variable
        self.expression = Expression(variable, -1.0, variable.value)
        self.is_stay_constraint=True

    def __repr__(self):
        return 'stay:%s' % super(StayConstraint, self).__repr__()


class Constraint(AbstractConstraint):
    LEQ = -1
    EQ = 0
    GEQ = 1

    def __init__(self, param1, operator=EQ, param2=None, strength=REQUIRED, weight=1.0):
        """Define a new linear constraint.

        param1 may be an expression or variable
        param2 may be an expression, variable, or constant, or may be ommitted entirely.
        If param2 is specified, the operator must be either LEQ, EQ, or GEQ
        """
        if isinstance(param1, Expression):
            if param2 is None:
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param1
            elif isinstance(param2, Expression):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param1.clone()
                if operator == self.LEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_expression(param2, 1.0)
                elif operator == self.EQ:
                    self.expression.add_expression(param2, -1.0)
                elif operator == self.GEQ:
                    self.expression.add_expression(param2, -1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")
            elif isinstance(param2, Variable):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param1.clone()
                if operator == self.LEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_variable(param2, 1.0)
                elif operator == self.EQ:
                    self.expression.add_variable(param2, -1.0)
                elif operator == self.GEQ:
                    self.expression.add_variable(param2, -1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")

            elif isinstance(param2, (float, int)):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param1.clone()
                if operator == self.LEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_expression(Expression(constant=param2), 1.0)
                elif operator == self.EQ:
                    self.expression.add_expression(Expression(constant=param2), -1.0)
                elif operator == self.GEQ:
                    self.expression.add_expression(Expression(constant=param2), -1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")
            else:
                raise InternalError("Invalid parameters to Constraint constructor")

        elif isinstance(param1, Variable):
            if param2 is None:
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = Expression(param1)
            elif isinstance(param2, Expression):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param2.clone()
                if operator == self.LEQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.EQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.GEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_variable(param1, 1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")

            elif isinstance(param2, Variable):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = Expression(param2)
                if operator == self.LEQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.EQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.GEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_variable(param1, 1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")

            elif isinstance(param2, (float, int)):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = Expression(constant=param2)
                if operator == self.LEQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.EQ:
                    self.expression.add_variable(param1, -1.0)
                elif operator == self.GEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_variable(param1, 1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")
            else:
                raise InternalError("Invalid parameters to Constraint constructor")

        elif isinstance(param1, (float, int)):
            if param2 is None:
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = Expression(constant=param1)

            elif isinstance(param2, Expression):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = param2.clone()
                if operator == self.LEQ:
                    self.expression.add_expression(Expression(constant=param1), -1.0)
                elif operator == self.EQ:
                    self.expression.add_expression(Expression(constant=param1), -1.0)
                elif operator == self.GEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_expression(Expression(constant=param1), 1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")

            elif isinstance(param2, Variable):
                super(Constraint, self).__init__(strength=strength, weight=weight)
                self.expression = Expression(constant=param1)
                if operator == self.LEQ:
                    self.expression.add_variable(param2, -1.0)
                elif operator == self.EQ:
                    self.expression.add_variable(param2, -1.0)
                elif operator == self.GEQ:
                    self.expression.multiply(-1.0)
                    self.expression.add_variable(param2, 1.0)
                else:
                    raise InternalError("Invalid operator in Constraint constructor")

            elif isinstance(param2, (float, int)):
                raise InternalError("Cannot create an inequality between constants")

            else:
                raise InternalError("Invalid parameters to Constraint constructor")
        else:
            raise InternalError("Invalid parameters to Constraint constructor")

        self.is_inequality = operator != self.EQ

    def clone(self):
        c = Constraint(self.expression, strength=self.strength, weight=self.weight)
        c.is_inequality = self.is_inequality
        return c
