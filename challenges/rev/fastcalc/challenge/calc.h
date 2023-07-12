#ifndef CALCMATH_H
#define CALCMATH_H

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

typedef enum Operator {
  ADD = '+',
  SUB = '-',
  MUL = '*',
  DIV = '/',
  MOD = '%',
  POW = '^'
} operator_t;

typedef struct operation {
  operator_t oper;
  double operandA;
  double operandB;
} operation_t;

/* Wrappers around the math library calls to preserve function names */
bool isNegative(double value) { return signbit(value); }
bool isNotNumber(double value) { return isnan(value); }
bool isInfinity(double value) { return isinf(value); }

double calculate(operation_t);
bool gauntlet(double result);

#endif
