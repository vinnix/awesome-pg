## File: Makefile
## 
## 	Regras para criar uma aplicacao libpq de exemplo

CPPFLAGS += -I/usr/local/pgsql/include
CFLAGS	 += -g
LDFLAGS	 += -g
LDFLAGS	 += -g
LDLIBS 	 += -L/usr/local/pgsql/lib -lpq 

all: testlibpq

testlibpq:  testlibpq.o

clean: 
	rm *.o testlibpq
