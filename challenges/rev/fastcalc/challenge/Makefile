COMPILER = gcc
FLAGS = -frecord-gcc-switches -static -O0 -lm

fast:
	$(COMPILER) calc.c -o calc -ffast-math $(FLAGS)

solve:
	$(COMPILER) calc.c -o calc-SOLUTION $(FLAGS)

output:
	python generate_operations.py > output.txt
