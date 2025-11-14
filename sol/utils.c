/*
utils.c

utilities
*/

#include <stdio.h>
#include <string.h>
#include <math.h>

// tokenize a string
int tokenize(char *str, const char *tokensep, char *token[], int maxtoken)
{
	if ((str == NULL) || !maxtoken) return 0;

	char *thistoken = strtok(str, tokensep);

	int   count;
	for (count = 0; (count < maxtoken) && (thistoken != NULL); ) {
		token[count++] = thistoken;
		thistoken = strtok(NULL, tokensep);
	}

	token[count] = NULL;

	return count;
}

// nearest id : p[n1]...p[n2]
int nearest(double x, int n1, int n2, const double p[])
{
	int    imin = n1;
	double dmin = fabs(x - p[n1]);
	for (int i = n1 + 1; i <= n2; i++) {
		double d = fabs(x - p[i]);
		if (d < dmin) {
			dmin = d;
			imin = i;
		}
	}

	return imin;
}


// p1 <= p[n1] <= p[n2] <= p2
// p : p[i1] ... p[i2]
// input : p, i1, i2, p1, p2, eps
// output : n1, n2
void get_span(double *p, int i1, int i2, double p1, double p2, int *n1, int *n2, double eps)
{
	*n1 = i1;
	*n2 = i2;

	if (i2 - i1 < 1) return;

	// q1 <= q2
	const double q1 = (p1 < p2) ? p1 : p2;
	const double q2 = (p1 > p2) ? p1 : p2;

	if      ((q1 < p[i1] - eps) && (q2 < p[i1] - eps)) {
		// p1, p2 < p[i1] -> n1 = n2 = i1
		*n1 = i1;
		*n2 = i1 - 1;  // zero area
	}
	else if ((q1 > p[i2] + eps) && (q2 > p[i2] + eps)) {
		// p1, p2 > p[i2] -> n1 = n2 = i2
		*n1 = i2 + 1;  // zero area
		*n2 = i2;
	}
	else {
		// p1 <= p[n1]
		for (int i = i1; i <= i2; i++) {
			if (p[i] > q1 - eps) {
				*n1 = i;
				break;
			}
		}
		// p[n2] <= p2
		for (int i = i2; i >= i1; i--) {
			if (p[i] < q2 + eps) {
				*n2 = i;
				break;
			}
		}
	}
}

/*
//
//$ cl.exe utils.c -Fea.exe; a.exe
int main(void)
{
	double p[] = {0, 1, 2, 3, 4, 5, 6};
	int n1, n2;
	get_span(p, 0, 6, 1.1, 4.9, &n1, &n2, 1e-6);
	printf("%d %d\n", n1, n2);
	return 0;
}
*/
/*
//$ clang-cl.exe -o a.exe utils.c; a.exe
int main(void)
{
	char str[] = " aaa  bbb  ccc  ddd ";
	char seps[] = " \t\n";
	char *token[100];

	int count = tokenize(str, seps, token, 3);

	for (int n = 0; n < count; n++) {
		printf("%d: %s\n", n, token[n]);
	}
}
*/
