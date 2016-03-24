/*
 * Implementation of the minimum and sufficient tests for non-preemptible
 * single-processor EDF, presented in Theorem 14 of "Preemptive and
 * Non-Preemptive Real-Time UniProcessor Scheduling " by George et al. (1996)
 */

#include <algorithm>
#include <set>
#include <utility>
#include <iostream>

#include <stdlib.h>
#include <limits.h>

#include "tasks.h"
#include "math-helper.h"
#include "stl-helper.h"
#include "schedulability.h"

#include "edf/george_np.h"

George_NPTest::George_NPTest(unsigned int num_processors)
{
	if (num_processors != 1) {
		/* This is a uniprocessor test---complain even in non-debug
		 * builds. */
		abort();
	}
}

unsigned long George_NPTest::sync_cpu_busy_period(const TaskSet &ts)
{
	unsigned long t = 0, t_prev, w;

	for (unsigned int i = 0; i < ts.get_task_count(); i++)
		t += ts[i].get_wcet();

	do {
		t_prev = t;

		w = 0;
		for (unsigned int i = 0; i < ts.get_task_count(); i++)
			w += divide_with_ceil(t, ts[i].get_period()) *
					ts[i].get_wcet();

		t = w;
	} while (t != t_prev);

	return t;
}


unsigned long George_NPTest::deadline_busy_period(
		std::multiset<Task, task_order_period> ts, Task task,
		integral_t a)
{
	unsigned long t = 0, t_prev;
	unsigned long B = 0;
	integral_t Di = task.get_deadline() + a;
	long Ci;
	unsigned long left, right;
	std::multiset<Task>::iterator tj;

	for (tj = ts.begin(); tj != ts.end(); tj++) {
		if (tj->get_deadline() > Di)
			B = std::max(tj->get_wcet(), B);
	}

	Ci = a.get_si() / task.get_period(); /* Implicit floor */
	Ci += 1;
	Ci *= task.get_wcet();

	do {
		t_prev = t;

		t = B + Ci;
		for (tj = ts.begin(); tj != ts.end(); tj++) {
			left = divide_with_ceil(t_prev, tj->get_period());
			right = a.get_si() + task.get_deadline() -
					tj->get_deadline();
			right /= tj->get_period(); /* Implicit floor */

			t += std::min(left, right) * tj->get_wcet();
		}
	} while (t < t_prev);

	return t;
}

/* Annex A, page 46 */
integral_t George_NPTest::synchronous_deadline_busy_period(
		std::multiset<Task, task_order_period>ordered_ts, Task t,
		unsigned long L)
{
	integral_t a, Li;

	a = (long)(L - t.get_deadline());
	a = divide_with_ceil(a, mpz_class(t.get_period()));
	a *= t.get_period();

	do {
		Li = deadline_busy_period(ordered_ts, t, a);
		a = divide_with_ceil(Li - t.get_deadline(),
				mpz_class(t.get_period()));
		a *= t.get_period();
	} while (Li <= a);

	return Li;
}

unsigned long George_NPTest::B1(const TaskSet &ts, fractional_t U)
{
	unsigned long max_C = 0;
	fractional_t tmp, ret, b1 = 0;

	for (unsigned int i = 0; i < ts.get_task_count(); i++) {
		/* Assume Di <= Ti */
		tmp = ts[i].get_deadline() / ts[i].get_period();
		b1 = b1 + ((1 - tmp) * ts[i].get_wcet());

		max_C = std::max(ts[i].get_wcet(), max_C);
	}
	b1 += max_C - 1;

	ret = b1 / (mpq_class(1) - U);

	return ceil(ret.get_d());
}

unsigned long George_NPTest::B2(std::multiset<Task, task_order_period> ts,
		fractional_t U)
{
	fractional_t b2 = 0;
	unsigned long max_D;
	std::multiset<Task>::iterator it;

	max_D = (ts.rbegin()++)->get_deadline();

	for (it = ts.begin(); it != ts.end(); it++)
		b2 += (1 - (it->get_deadline() / it->get_period()));

	b2 /= (mpq_class(1) - U);

	return std::max(max_D, static_cast<unsigned long>(ceil(b2.get_d())));
}

std::set<unsigned long> George_NPTest::S(const TaskSet &ts, std::multiset<Task,
		task_order_period> ordered_ts,fractional_t U)
{
	unsigned long b1, b2, L, max_S, t;
	integral_t Li, max_k;
	std::set<unsigned long> S;

	b1 = B1(ts, U);
	b2 = B2(ordered_ts, U);
	L = sync_cpu_busy_period(ts);

	max_S = std::min(L, std::min(b1, b2));

	for (unsigned long i = 0; i < ts.get_task_count(); i++) {
		Li = synchronous_deadline_busy_period(ordered_ts, ts[i], L);

		max_k = Li - ts[i].get_deadline();
		max_k /= ts[i].get_period(); /* Implicit floor */

		for (long k = 0; k <= max_k.get_si(); k++) {
			t = (k * ts[i].get_period()) + ts[i].get_deadline();
			if (t >= max_S)
				break;

			S.insert(t);
		}
	}

	return S;
}

bool George_NPTest::is_schedulable(const TaskSet &ts, bool check_preconditions)
{
	fractional_t util = 0;
	unsigned long max_C;
	integral_t demand;

	std::multiset<Task, task_order_period> ordered_ts;
	std::set<unsigned long> s;
	std::set<unsigned long>::iterator t;
	std::multiset<Task>::reverse_iterator it;

	if (check_preconditions) {
		if (!(ts.has_no_self_suspending_tasks()
				&& ts.has_only_feasible_tasks()))
			return false;
	}

	ts.get_utilization(util);
	if (util >= 1)
		return false;

	for (unsigned int i = 0; i < ts.get_task_count(); i++)
		ordered_ts.insert(ts[i]);

	s = S(ts, ordered_ts, util);

	for (t = s.begin(); t != s.end(); t++)
	{
		max_C = 0;
		for (it = ordered_ts.rbegin(); it != ordered_ts.rend(); it++) {
			if (it->get_deadline() > *t) {
				max_C = std::max(it->get_wcet() - 1, max_C);
				break;
			}
		}

		ts.bound_demand(mpz_class(*t), demand);

		if (demand + max_C > *t)
			return false;
	}

	return true;
}
