#ifndef JEFFAY_NP_H
#define JEFFAY_NP_H

#ifndef SWIG
#include <set>
#endif

class George_NPTest : public SchedulabilityTest
{
 public:
	George_NPTest(unsigned int num_processors);

	bool is_schedulable(const TaskSet &ts, bool check_preconditions = true);

 private:
	struct task_order_period {
		bool operator()(const Task& lhs, const Task& rhs) const
		{
			return lhs.get_deadline() < rhs.get_deadline();
		}
	};

	unsigned long sync_cpu_busy_period(const TaskSet &ts);
	unsigned long deadline_busy_period(
			std::multiset<Task, task_order_period> ts, Task task,
			integral_t a);
	unsigned long B1(const TaskSet &ts, fractional_t U);
	unsigned long B2(std::multiset<Task, task_order_period> ts,
			fractional_t U);
	std::set<unsigned long> S(const TaskSet &ts, std::multiset<Task,
			task_order_period> ordered_ts,fractional_t U);
	integral_t synchronous_deadline_busy_period(
			std::multiset<Task, task_order_period> ordered_ts,
			Task t, unsigned long L);
};

#endif
