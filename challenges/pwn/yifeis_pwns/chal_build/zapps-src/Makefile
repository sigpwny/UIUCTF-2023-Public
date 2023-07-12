CFLAGS := -g -Os -pipe

all: relative/exe

.PHONY: clean
.SECONDARY:
.DELETE_ON_ERROR:

clean:
	rm -rf tmp absolute relative

tmp:
	mkdir -p tmp
absolute:
	mkdir -p absolute
relative:
	mkdir -p relative

absolute/lib.so: lib.c | absolute
	$(CC) -o $@ $< -fPIC -shared $(CFLAGS)
absolute/exe: exe.c absolute/lib.so | absolute
	$(CC) -o $@ $< -L absolute -l:lib.so -Wl,-rpath=absolute $(CFLAGS)

relative/ld-linux-x86-64.so.2 relative/libc.so.6: | relative
	cp $$($(CC) --print-file-name=$(notdir $@)) $@

tmp/zapps-crt0.o: zapps-crt0.c | tmp
	$(CC) -o $@ $< -fPIC -ffreestanding -fno-merge-constants -c $(CFLAGS)
tmp/strip_interp: strip_interp.c | tmp
	$(CC) -o $@ $< $(CFLAGS)

relative/lib.so: lib.c | relative
	$(CC) -o $@ $< -fPIC -shared $(CFLAGS)
relative/exe: exe.c tmp/strip_interp tmp/zapps-crt0.o relative/lib.so relative/ld-linux-x86-64.so.2 relative/libc.so.6 | relative
	$(CC) -o $@ $< -L relative -l:lib.so -Wl,-rpath=XORIGIN -Wl,-e_zapps_start -Wl,--unique=.text.zapps tmp/zapps-crt0.o $(CFLAGS)
	sed -i '0,/XORIGIN/{s/XORIGIN/$$ORIGIN/}' $@
	tmp/strip_interp $@
