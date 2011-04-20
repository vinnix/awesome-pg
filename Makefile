## File: Makefile
## 
## 	Regras para criar uma aplicacao libpq de exemplo

CPPFLAGS += -I/usr/include/postgresql
CFLAGS	 += -g
LDFLAGS	 += -g
LDFLAGS	 += -g
LDLIBS 	 += -L/usr/lib -lpq 

testlibpq: testlibpq.o
