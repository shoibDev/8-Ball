CC = clang
CFLAGS = -std=c99 -g -Wall -pedantic
PYTHON_INCLUDE = /usr/include/python3.11
PYTHON_LIB = /usr/lib/python3.11
SWIG = swig

all: _phylib.so

clean:
	rm -f *.o *.so

phylib.o: phylib.c
	$(CC) $(CFLAGS) -fPIC -c phylib.c -o phylib.o

libphylib.so: phylib.o
	$(CC) -shared -o libphylib.so phylib.o -L$(PYTHON_LIB) -lm

phylib_wrap.c:
	$(SWIG) -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -fPIC -c phylib_wrap.c -I$(PYTHON_INCLUDE) -o phylib_wrap.o

_phylib.so: libphylib.so phylib_wrap.o
	$(CC) -shared phylib_wrap.o -L. -L$(PYTHON_LIB) -lpython3.11 -lphylib -o _phylib.so
