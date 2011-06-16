 /*
 *   * testlibpq.c
 *   *   Test the C version of LIBPQ, the POSTGRES frontend library.
 *   *
 *   *
 * 
 * */


#include <stdio.h>
#include "libpq-fe.h"  /* internal include PG */

void exit_nicely(PGconn* conn) 
{ 
	PQfinish(conn); 
	exit(1); 
}

int main(int argc, char* argv) 
{ 
	char *pghost, *pgport, *pgoptions, *pgtty; char* dbName; int nFields; int i,j;

	/* FILE *debug; */

	PGconn* conn; 
	PGresult* res;

	/* begin, by setting the parameters for a backend connection if the parameters are null, 
 	* then the system will try to use reasonable defaults by looking up environment variables or, 
 	* failing that, using hardwired constants */ 
	
	pghost = NULL; 
	/* host name of the backend server */ 
	pgport = NULL; 
	/* port of the backend server */ 
	pgoptions = NULL; 
	/* special options to start up the backend server */ 
	
	pgtty = NULL; 
	/* debugging tty for the backend server */ 
	dbName = "template1";

	// http://developer.postgresql.org/pgdocs/postgres/libpq-connect.html

	/* make a connection to the database */ 
	//conn = PQsetdb(pghost, pgport, pgoptions, pgtty, dbName); // trying to connect with PGconnectdb

	// PGconn *PQconnectdb(const char *conninfo);
	// PGconn *PQconnectdbParams(const char **keywords, const char **values, int expand_dbname);

	char *conKeyParam[] = {"host","port","dbname","user",NULL};
	char *conKeyValues[] = {"localhost","5432","template1","postgresql",NULL};

	/*conKeyParam[0]="host";
	conKeyParam[1]="hostaddr";
	conKeyParam[2]="port";
	conKeyParam[3]="dbname";
	conKeyParam[4]="user";
	conKeyParam[5]="\0";

	conKeyValues[0]="localhost";
	conKeyValues[1]="127.0.0.1";
	conKeyValues[2]="5432";
	conKeyValues[3]="template1";
	conKeyValues[4]="postgresql";
	conKeyValues[5]="\0";
	*/
	
	conn = PQconnectdbParams(conKeyParam,conKeyValues,0);

	/* check to see that the backend connection was successfully made */ 
	if (PQstatus(conn) == CONNECTION_BAD) 
	{ 
		fprintf(stderr, "Connection to database '%s' failed.0\n", dbName); 
		fprintf(stderr,"%s",PQerrorMessage(conn)); 
		exit_nicely(conn); 

	}

	/* debug = fopen("/tmp/trace.out","w"); */ /* PQtrace(conn, debug); */

	/* start a transaction block */ 
	res = PQexec(conn,"BEGIN"); 
	if (PQresultStatus(res) != PGRES_COMMAND_OK) 
	{ 
		fprintf(stderr,"BEGIN command failed0"); 
		PQclear(res); exit_nicely(conn); 
	} /* should PQclear PGresult whenever it is no longer needed to avoid memory leaks */ 
	PQclear(res);

	/* fetch instances from the pg_database, the system catalog of databases*/ 
	res = PQexec(conn,"DECLARE myportal CURSOR FOR select * from pg_database"); 
	if (PQresultStatus(res) != PGRES_COMMAND_OK) 
	{ 
		fprintf(stderr,"DECLARE CURSOR command failed0"); 
		PQclear(res); 
		exit_nicely(conn); 
	} 
	PQclear(res);

	res = PQexec(conn,"FETCH ALL in myportal"); 
	if (PQresultStatus(res) != PGRES_TUPLES_OK) 
	{ 
		fprintf(stderr,"FETCH ALL command didn't return tuples properly"); 
		PQclear(res); 
		exit_nicely(conn); 
	}

	/* first, print out the attribute names */ 
	nFields = PQnfields(res); 
	for (i=0; i < nFields; i++) 
	{ 
		printf("%-15s",PQfname(res,i)); 
	} 
	printf("|");

	/* next, print out the instances */ 
	for (i=0; i < PQntuples(res); i++) 
	{ 
		for (j=0 ; j < nFields; j++) 
		{ 
			printf("%-15s", PQgetvalue(res,i,j)); 
		} 
		printf("|"); 
	}

	PQclear(res);

	/* close the portal */ 
	res = PQexec(conn, "CLOSE myportal"); 
	PQclear(res);

	/* end the transaction */ 
	res = PQexec(conn, "END"); 
	PQclear(res);

	/* close the connection to the database and cleanup */ 
	PQfinish(conn); 
	/* fclose(debug); */ 
} 
