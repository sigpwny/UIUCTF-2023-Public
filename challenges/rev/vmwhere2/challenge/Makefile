all: chal program

chal: chal.o
	$(CC) $(CFLAGS) -O2 -o chal chal.o
	strip chal

program_assembly: highlevel.py program.py
	python3 program.py > program_assembly

program: assembler.py program_assembly
	./assembler.py program_assembly program

clean:
	rm -f chal chal.o
	rm -f program program_assembly
