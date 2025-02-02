import networkx as nx
import random
from typing import Dict
from typing import Any

from matplotlib import pyplot as plt


class CorePair:
    t = 0

    def __init__(self, high_power, low_power):
        self.pair_id = self.t
        self.high_power_core = high_power
        self.low_power_core = low_power
        self.is_high_active = False
        self.is_low_active = False
        self.t += 1

    def find_first_free_time_slot_after(self, k):
        # Logic to find the first free time slot after k
        # This is just a placeholder; implement your logic accordingly
        return k + 1  # Example: returns next time slot

    def get_tsp(self,number_of_active_cores, time):
        # gets thermal limits from Hotspot and calculates TSP based on active cores
        return 100, 80  # Example: returns a tuple of static value for high_power and low_power core

    def schedule(self, task, time):
        # Logic to schedule a task at a given time
        self.schedule.append((task.name, time))
        print(f"Scheduled {task.name} at time {time} on core.")


class System:
    def __init__(self):
        self.islands = []
        self.total_time = 200

    def add_core_pair(self, core_pair):
        self.islands.append(core_pair)

    def activate(self, pair_id, core):
        # if core==0 then high_power must be activated and if core==1 then low_power must be activated
        for pair in self.islands:
            if pair.pair_id == pair_id:
                if(core):
                    pair.is_low_active=True
                else:
                    pair.is_high_active=True

    def deactivate(self, pair_id, core):
        # if core==0 then high_power must be deactivated and if core==1 then low_power must be deactivated
        for pair in self.islands:
            if pair.pair_id == pair_id:
                if(core):
                    pair.is_low_active=False
                else:
                    pair.is_high_active=False


    def get_number_of_active_cores(self):
        t = 0
        for island in self.islands:
            if island.is_high_active: t += 1
            if island.is_low_active: t += 1
        return t


class TaskScheduler:
    def __init__(self, core_pairs, G, system):
        self.graph = G  # Set of tasks in graph G
        self.graph_copy = G
        self.core_pairs = core_pairs  # Set of core pairs CP
        self.leaves = []
        self.priority_queue = []
        self.system = system

    def return_leaves(self):
        # Assuming this method returns the leaves of the graph (tasks with no dependencies)
        for node in self.graph:
            if len(list(self.graph.successors(node))) == 0 and (node not in self.leaves):
                self.leaves.append(node)

    def make_priority_queue(self):
        # Select the task with the latest deadline from priority queue
        while (len(self.graph.nodes) > 0):
            self.return_leaves()
            selected_node = self.graph.nodes.get(self.leaves[0])
            # print(self.leaves[0])
            for key in self.leaves:
                # print(self.graph.nodes[key]['deadline'])
                if self.graph.nodes[key]['deadline'] > selected_node['deadline']:
                    selected_node = self.graph.nodes.get(key)
                    # print(selected_node)

            selected_key = None
            for key in self.graph.nodes.keys():
                if self.graph.nodes.get(key) == selected_node:
                    selected_key = key

            self.graph.remove_node(selected_key)
            self.leaves.remove(selected_key)
            # self.leaves.remove(self.leaves[0])
            self.priority_queue.append(selected_node)

        print('\npriority queue is:')
        print(self.priority_queue)

    def min_utilization(self):
        # Placeholder for finding the minimum utilization core pair
        # This should return a core pair based on some criteria
        return self.core_pairs[random.randint(0, 4)]  # Example: Return the first core pair

    def schedule_tasks(self):
        self.make_priority_queue()
        while len(self.priority_queue)>0:
            unscheduled_task = self.priority_queue[len(self.priority_queue)-1]
            self.priority_queue.remove(unscheduled_task)
            selected_core_pair = self.min_utilization()
            k=0
            if len(self.graph_copy.predecessors(unscheduled_task)) > 0:
                parent_deadlines = [
                    self.graph_copy.nodes[parent]['deadline'] for parent in self.graph_copy.predecessors(unscheduled_task) if self.graph_copy.has_node(parent)
                ]
                if parent_deadlines:
                    k = max(parent_deadlines)

            while k <= unscheduled_task['deadline'] - unscheduled_task['WC_high']:
                t = selected_core_pair.find_first_free_time_slot_after(k)
                # tsp for high power core
                tsp = selected_core_pair.get_tsp(self.system.get_number_of_active_cores(), t)[0]
                if unscheduled_task['high_power'] <= tsp:
                    print(f'core pair: {selected_core_pair.pair_id} , core: primary, task: {unscheduled_task}')
                    self.system.activate(selected_core_pair.pair_id, 0)
                    # schedules unscheduled task on primary core of selected_core_pair

                    break
                else:
                    k = t+1

            k = k + unscheduled_task['WC_high']
            while(1):
                t = selected_core_pair.find_first_free_time_slot_after(k)
                # tsp for low_power core
                tsp = selected_core_pair.get_tsp(self.system.get_number_of_active_cores(), t)[1]
                if unscheduled_task['low_power'] <= tsp:
                    print(f'core pair: {selected_core_pair.pair_id} , core: spare, task: {unscheduled_task}')
                    self.system.activate(selected_core_pair.pair_id, 1)
                    # schedules backup task (B) on spare core of selected_core_pair
                    break

def get_cores():
    # gets cores from gem5 and convert them to our format
    core_pairs = []
    for i in range(5):
        x = random.uniform(2, 8)
        y = random.uniform(2, 8)
        CP = CorePair(max(x, y), min(x, y))
        core_pairs.append(CP)
    return core_pairs

def assign_tasks_power_consumption(G, core_pairs):
    # assigns a power consumption on low_power and high_power core to tasks
    for node in G:
        x = random.uniform(2, 8)
        y = random.uniform(2, 8)
        G.nodes[node]['high_power'] = max(x, y)
        G.nodes[node]['low_power'] = min(x, y)
    return G

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
            low_power = 0
            high_power = 0
            deadline = 0

            G.add_node(current_node,
                       label=f"T{current_node}",
                       WC_low=round(WC_low, 2),
                       WC_high=round(WC_high, 2),
                       low_power=round(low_power, 2),
                       high_power=round(high_power, 2),
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

core_pairs = get_cores()
system = System()
system.islands.append(core_pairs)

dag = assign_tasks_power_consumption(dag, core_pairs)

task_schedular = TaskScheduler(core_pairs, dag, system)
task_schedular.schedule_tasks()