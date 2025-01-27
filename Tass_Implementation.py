import networkx as nx
import random
from typing import Dict
from typing import Any

from matplotlib import pyplot as plt


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

def generate_dag(n: int, density: float, regularity: float, fatness: float) -> nx.DiGraph:
    if n <= 1:
        raise ValueError("Number of tasks must be greater than 1")

    G = nx.DiGraph()

    max_width = int(n * fatness)
    num_levels = max(2, n // max_width)

    nodes_per_level = [[] for _ in range(num_levels)]
    current_node = 0

    for level in range(num_levels):
        if level == 0:
            width = min(max_width // 2, n)
        elif level == num_levels - 1:
            width = n - current_node
        else:
            width = min(max_width, n - current_node)

        for _ in range(width):
            exec_time_1 = random.uniform(1, 15)
            exec_time_2 = random.uniform(1, 15)
            WC_low = max(exec_time_1, exec_time_2)
            WC_high = min(exec_time_1, exec_time_2)
            deadline = 0

            G.add_node(current_node,
                       label=f"T{current_node}",
                       WC_low=round(WC_low, 2),
                       WC_high=round(WC_high, 2),
                       deadline=round(deadline, 2))

            nodes_per_level[level].append(current_node)
            if current_node < n-1:
                current_node += 1

    for level in range(num_levels - 1):
        current_level_nodes = nodes_per_level[level]
        next_level_nodes = nodes_per_level[level + 1]

        for source in current_level_nodes:
            num_edges = max(1, int(len(next_level_nodes) * density))

            if random.random() < regularity:
                num_edges = min(num_edges + 1, len(next_level_nodes))

            targets = random.sample(next_level_nodes, num_edges)
            for target in targets:
                G.add_edge(source, target)

    current_node = 0
    for node in G.nodes:
        slack_factor = random.uniform(1.5, 3)
        deadline = (G.nodes[node]['WC_low'] + G.nodes[node]['WC_high']) * slack_factor

        if list(G.predecessors(node)):
            parent_deadlines = [
                G.nodes[parent]['deadline'] for parent in G.predecessors(node) if G.has_node(parent)
            ]
            if parent_deadlines:
                parent_deadline = max(parent_deadlines)

                while deadline <= parent_deadline:
                    slack_factor = random.uniform(1.5, 3)
                    deadline = parent_deadline + (G.nodes[node]['WC_low'] + G.nodes[node]['WC_high']) * slack_factor

        G.nodes[node]['deadline'] = round(deadline, 2)
        print(f'node {node} :')
        print(G.nodes[node])
        print('parents: ')
        print([G.nodes[parent]['label'] for parent in G.predecessors(node)])
        print('\n')

    return G

def draw_dag(G: nx.DiGraph, title: str = "DAG") -> None:
    plt.figure(figsize=(12, 8))
    pos = nx.kamada_kawai_layout(G)

    nx.draw_networkx_nodes(G, pos, node_color='lightblue',
                          node_size=2000, alpha=0.7)

    nx.draw_networkx_edges(G, pos, edge_color='gray',
                          arrows=True, arrowsize=20)

    labels = {}
    for node in G.nodes():
        data = G.nodes[node]
        labels[node] = f"{data['label']}\nlow:{data['WC_low']:.1f}\nhigh:{data['WC_high']:.1f}\ndeadline:{data['deadline']:.1f}"

    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def print_dag_stats(G: nx.DiGraph) -> Dict[str, Any]:
    stats = {
        'num_nodes': G.number_of_nodes(),
        'num_edges': G.number_of_edges(),
        'avg_degree': float(G.number_of_edges()) / G.number_of_nodes(),
        'critical_path': nx.dag_longest_path_length(G),
        'levels': len(list(nx.topological_generations(G)))
    }

    print("\nDAG Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


n_tasks = 10
density = 0.4
regularity = 0.6
fatness = 0.4

dag = generate_dag(n_tasks, density, regularity, fatness)

draw_dag(dag, "Generated DAG")
stats = print_dag_stats(dag)

# Example usage:

# # Define tasks and cores here...
# tasks = [Task("Task1", deadline=10, power=5), Task("Task2", deadline=15, power=3)]
# core_pairs = [CorePair(primary_core=Core(), spare_core=Core())]
#
# scheduler = TaskScheduler(tasks, core_pairs)
# scheduler.schedule_tasks()
