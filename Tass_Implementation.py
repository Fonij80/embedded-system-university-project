class Core:
    def __init__(self):
        self.schedule = []

    def find_first_free_time_slot_after(self, k):
        # Logic to find the first free time slot after k
        # This is just a placeholder; implement your logic accordingly
        return k + 1  # Example: returns next time slot

    def get_tsp(self, active_cores_at):
        # Logic to return TSP based on active cores
        return 100  # Example: returns a static value for TSP

    def schedule(self, task, time):
        # Logic to schedule a task at a given time
        self.schedule.append((task.name, time))
        print(f"Scheduled {task.name} at time {time} on core.")


class Task:
    def __init__(self, name, deadline, power):
        self.name = name
        self.deadline = deadline
        self.power = power


class CorePair:
    def __init__(self, primary_core, spare_core):
        self.primary_core = primary_core
        self.spare_core = spare_core


class TaskScheduler:
    def __init__(self, tasks, core_pairs):
        self.tasks = tasks  # Set of tasks in graph Φ
        self.core_pairs = core_pairs  # Set of core pairs CP
        self.temp_queue = []  # TQ
        self.priority_queue = []  # PQ

    def return_leaves(self):
        # Assuming this method returns the leaves of the graph (tasks with no dependencies)
        return [task for task in self.tasks if not task.has_dependencies()]

    def select_latest_deadline(self):
        # Select the task with the latest deadline from priority queue
        if not self.priority_queue:
            return None
        return max(self.priority_queue, key=lambda t: t.deadline)

    def min_utilization(self):
        # Placeholder for finding the minimum utilization core pair
        # This should return a core pair based on some criteria
        return self.core_pairs[0]  # Example: Return the first core pair

    def schedule_tasks(self):
        while self.tasks:
            # Step 3: Return leaves of graph
            self.temp_queue = self.return_leaves()

            # Step 4: Select a task with the latest deadline
            if not self.temp_queue:
                break

            selected_task = max(self.temp_queue, key=lambda t: t.deadline)
            self.priority_queue.append(selected_task)  # Step 5: Put Ti to PQ
            self.tasks.remove(selected_task)  # Step 6: Remove Ti from the graph

        while self.priority_queue:
            selected_task = self.select_latest_deadline()  # Step 9

            if not selected_task:
                break

            core_pair = self.min_utilization()  # Step 10
            k = max(selected_task.get_finish_time_of_predecessors())  # Step 11

            while k <= selected_task.deadline - selected_task.get_w():  # Step 12
                t = core_pair.primary_core.find_first_free_time_slot_after(k)  # Step 13

                TSP_primary = core_pair.primary_core.get_tsp(active_cores_at=t)  # Step 14

                if selected_task.power <= TSP_primary:  # Step 15
                    core_pair.primary_core.schedule(selected_task, t)  # Step 16
                    self.priority_queue.remove(selected_task)  # Step 17
                    break

                k = t + 1

            k = selected_task.get_finish_time_on_primary()  # Step 21

            while not selected_task.is_bi_scheduled():  # Step 22
                t = core_pair.primary_core.find_first_free_time_slot_after(k)  # Step 23

                TSP_spare = core_pair.spare_core.get_tsp(active_cores_at=t)  # Step 24

                if selected_task.get_bi_power() <= TSP_spare:  # Step 25
                    core_pair.spare_core.schedule(selected_task.get_bi(), t)  # Step 26
                    break


# Example usage:

# Define tasks and cores here...
tasks = [Task("Task1", deadline=10, power=5), Task("Task2", deadline=15, power=3)]
core_pairs = [CorePair(primary_core=Core(), spare_core=Core())]

scheduler = TaskScheduler(tasks, core_pairs)
scheduler.schedule_tasks()
