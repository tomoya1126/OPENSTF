/*
post.c

post process
*/

#include "ost.h"
#include "ev.h"
#include "ost_prototype.h"

void post(void)
{
	ev2d_init(Width2d, Height2d);

	ev3d_init();

	if (Piter) {
		plotIter();
	}

	if (NL1d > 0) {
		plotL1d();
	}

	if (NP2d > 0) {
		plotP2d();
	}

	ev2d_file(!HTML, (!HTML ? FN_ev2d_1 : FN_ev2d_0));
	ev2d_output();

	ev3d_file(!HTML, (!HTML ? FN_ev3d_1 : FN_ev3d_0), 0);
	ev3d_output();
}
