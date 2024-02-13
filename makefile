# Compiler to use
CC=gcc

# Compiler flags
CFLAGS=-Wall -g

# Name of the output executable
TARGET=main

# Default target
all: $(TARGET)

$(TARGET): main.c
	$(CC) $(CFLAGS) main.c -o $(TARGET)

clean:
	rm -f $(TARGET)

.PHONY: all clean
