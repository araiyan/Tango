CC = gcc
CFLAGS = -W -Wall -Wextra

OBJS = autodriver.o

all: autodriver

autodriver: $(OBJS)
	$(CC) $(LDFLAGS) -o autodriver $(OBJS)
	sudo chown ubuntu autodriver
	sudo chmod +s autodriver

autodriver.o: autodriver.c

clean:
	rm -f *.o autodriver

.PHONY: clean
