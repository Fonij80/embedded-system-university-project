import networkx as nx
import random
from typing import Dict
from typing import Any
import matplotlib

matplotlib.use('Qt5Agg')
matplotlib.use('TkAgg')  # or 'Qt5Agg' or 'Qt6Agg'
import matplotlib.pyplot as plt


class CorePair:
    def __init__(self, high_power, low_power):
        self.pair_id = id(self)  # Unique ID for each core pair
        self.high_power_core = high_power
        self.low_power_core = low_power
        self.schedule = []  # List of tuples: (task_name, start_time, end_time, core_type)

    def find_first_free_time_slot_after(self, k):
        # Find the first free time slot after time `k`
        return k  # Placeholder logic

    def get_tsp(self, number_of_active_cores, time):
        # Return thermal safe power (TSP) for high and low power cores
        return 1000, 500  # Example values

    def schedule_task(self, task, start_time, core_type):
        end_time = start_time + task['WC_high'] if core_type == "high" else start_time + task['WC_low']
        self.schedule.append((task['label'], start_time, end_time, core_type))


class System:
    def __init__(self, core_pair):
        self.islands = []
        self.total_time = 200
        self.islands.append(core_pair)

    def activate(self, pair_id, core):
        # if core==0 then high_power must be activated and if core==1 then low_power must be activated
        for pair in self.islands:
            if pair.pair_id == pair_id:
                if (core):
                    pair.is_low_active = True
                else:
                    pair.is_high_active = True

    def deactivate(self, pair_id, core):
        # if core==0 then high_power must be deactivated and if core==1 then low_power must be deactivated
        for pair in self.islands:
            if pair.pair_id == pair_id:
                if (core):
                    pair.is_low_active = False
                else:
                    pair.is_high_active = False

    def get_number_of_active_cores(self):
        t = 0
        for island in self.islands:
            if island.is_high_active: t += 1
            if island.is_low_active: t += 1
        return t


class TaskScheduler:
    def __init__(self, core_pairs, G):
        self.graph = G
        self.core_pairs = core_pairs
        self.priority_queue = []

    def make_priority_queue(self):
        # Sort tasks by latest deadline first (LDF)
        self.priority_queue = sorted(list(self.graph.nodes(data=True)), key=lambda x: x[1]['deadline'], reverse=True)

    def schedule_tasks(self):
        self.make_priority_queue()
        while len(self.priority_queue) > 0:
            task_id, task_data = self.priority_queue.pop(0)  # Get the task with the latest deadline
            selected_core_pair = random.choice(self.core_pairs)  # Select a random core pair for simplicity

            # Schedule on high-power core first
            k = 0  # Start time
            while True:
                t_high = selected_core_pair.find_first_free_time_slot_after(k)
                tsp_high = selected_core_pair.get_tsp(0, t_high)[0]
                if task_data['high_power'] <= tsp_high:
                    selected_core_pair.schedule_task(task_data, t_high, "high")
                    break
                else:
                    k += 1

            # Schedule on low-power core as backup
            k += task_data['WC_high']
            while True:
                t_low = selected_core_pair.find_first_free_time_slot_after(k)
                tsp_low = selected_core_pair.get_tsp(0, t_low)[1]
                if task_data['low_power'] <= tsp_low:
                    selected_core_pair.schedule_task(task_data, t_low, "low")
                    break


def get_cores(number_of_cores):
    # gets cores from gem5 and convert them to our format
    core_pairs = []
    for i in range(number_of_cores):
        # LP: ARM Cortex-A7: average power consumption: 226 mW
        # HP: ARM Cortex-A15: average power consumption: 650 mW
        # get a random power consumption of two cores in heterogeneous system
        power_A7 = random.uniform(100, 352)
        power_A15 = random.uniform(500, 1000)
        core_pairs.append(CorePair(power_A15, power_A7))
    return core_pairs


def assign_tasks_power_consumption(G, core_pairs):
    # assign a power consumption on low_power and high_power core to tasks
    for node in G:
        # choose one of the pairs and assign their power to the task power consumption
        randomIndex = random.randint(0, len(core_pairs) - 1)
        G.nodes[node]['high_power'] = core_pairs[randomIndex].high_power_core
        G.nodes[node]['low_power'] = core_pairs[randomIndex].low_power_core
    return G


def generate_dag(number_of_tasks: int, density: float, regularity: float, fatness: float) -> nx.DiGraph:
    if number_of_tasks <= 1:
        raise ValueError("Number of tasks must be greater than 1")

    G = nx.DiGraph()

    max_width = int(number_of_tasks * fatness)
    num_levels = max(2, number_of_tasks // max_width)

    nodes_per_level = [[] for _ in range(num_levels)]
    current_node = 0

    for level in range(num_levels):
        if level == 0:
            width = min(max_width // 2, number_of_tasks)
        elif level == num_levels - 1:
            width = number_of_tasks - current_node
        else:
            width = min(max_width, number_of_tasks - current_node)

        for i in range(width):
            exec_time_1 = random.uniform(1, 15)
            exec_time_2 = random.uniform(1, 15)
            WC_low = max(exec_time_1, exec_time_2)
            WC_high = min(exec_time_1, exec_time_2)
            low_power = 0
            high_power = 0
            deadline = 0

            G.add_node(current_node,
                       id=current_node,
                       label=f"T{current_node}",
                       WC_low=round(WC_low, 2),
                       WC_high=round(WC_high, 2),
                       low_power=round(low_power, 2),
                       high_power=round(high_power, 2),
                       deadline=round(deadline, 2))

            nodes_per_level[level].append(current_node)
            if current_node < number_of_tasks - 1:
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
        labels[
            node] = f"{data['label']}\nLow:{data['WC_low']:.1f}\nHigh:{data['WC_high']:.1f}\nDeadline:{data['deadline']:.1f}"

    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.title(title)
    plt.axis('off')
    plt.tight_layout()

    # Save or show the plot
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


def plot_schedule(core_pairs):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ["#FF9999", "#99CCFF", "#99FF99", "#FFCC99", "#CCCCFF"]
    color_map = {}

    for i, core_pair in enumerate(core_pairs):
        y_high = i * 2 + 1  # High-power core row
        y_low = i * 2  # Low-power core row

        for task_name, start_time, end_time, core_type in core_pair.schedule:
            if task_name not in color_map:
                color_map[task_name] = colors[len(color_map) % len(colors)]
            color = color_map[task_name]

            # Draw the bar for high-power core
            if core_type == "high":
                ax.barh(y_high, end_time - start_time, left=start_time, height=0.8,
                        color=color, edgecolor="black")
                # Add task number to the bar
                ax.text(start_time + (end_time - start_time) / 2, y_high, task_name,
                        ha='center', va='center', color='black')

            else:  # Low-power core
                ax.barh(y_low, end_time - start_time, left=start_time, height=0.8,
                        color=color, edgecolor="black")
                # Add task number to the bar
                ax.text(start_time + (end_time - start_time) / 2, y_low, task_name,
                        ha='center', va='center', color='black')

    ax.set_yticks([i for i in range(len(core_pairs) * 2)])
    ax.set_yticklabels([f"Core {i // 2} {'High' if i % 2 == 1 else 'Low'}" for i in range(len(core_pairs) * 2)])
    ax.set_xlabel("Time")
    ax.set_title("Task Scheduling on Core Pairs")
    plt.tight_layout()
    plt.show()


# run simulation based on different number of tasks considered in paper
# for 36 tasks
number_of_cores = 8  # 8 LP core and 8 HP core
density = 0.4  # how many edges exist between nodes in the graph relative to the maximum possible edges
regularity = 0.6  # Higher regularity ensures that edges are evenly distributed, making the graph more balanced
fatness = 0.4  # Higher fatness creates wider levels with more parallel tasks, while lower fatness creates narrower levels

# same set of core pairs for different set of tasks, but in different system
dag_36 = generate_dag(36, density, regularity, fatness)
draw_dag(dag_36, "Generated DAG with 36 tasks")
print_dag_stats(dag_36)

core_pairs = get_cores(number_of_cores)

system = System(core_pairs)
dag_36 = assign_tasks_power_consumption(dag_36, core_pairs)

TaskScheduler(core_pairs, dag_36).schedule_tasks()
plot_schedule(core_pairs)

# for 45 tasks
dag_45 = generate_dag(45, density, regularity, fatness)
draw_dag(dag_45, "Generated DAG with 45 tasks")
print_dag_stats(dag_45)

dag_45 = assign_tasks_power_consumption(dag_45, core_pairs)

TaskScheduler(core_pairs, dag_45).schedule_tasks()
plot_schedule(core_pairs)

# for 54 tasks
dag_54 = generate_dag(54, density, regularity, fatness)
draw_dag(dag_54, "Generated DAG with 54 tasks")
print_dag_stats(dag_54)

dag_54 = assign_tasks_power_consumption(dag_54, core_pairs)

TaskScheduler(core_pairs, dag_54).schedule_tasks()
plot_schedule(core_pairs)

# for 63 tasks
dag_63 = generate_dag(63, density, regularity, fatness)
draw_dag(dag_63, "Generated DAG with 63 tasks")
print_dag_stats(dag_63)

dag_63 = assign_tasks_power_consumption(dag_63, core_pairs)

TaskScheduler(core_pairs, dag_63).schedule_tasks()
plot_schedule(core_pairs)

# for 72 tasks
dag_72 = generate_dag(72, density, regularity, fatness)
draw_dag(dag_72, "Generated DAG with 72 tasks")
print_dag_stats(dag_72)

dag_72 = assign_tasks_power_consumption(dag_72, core_pairs)

TaskScheduler(core_pairs, dag_72).schedule_tasks()
plot_schedule(core_pairs)

# for 81 tasks
dag_81 = generate_dag(81, density, regularity, fatness)
draw_dag(dag_81, "Generated DAG with 81 tasks")
print_dag_stats(dag_81)

dag_81 = assign_tasks_power_consumption(dag_81, core_pairs)

TaskScheduler(core_pairs, dag_81).schedule_tasks()
plot_schedule(core_pairs)

# for 90 tasks
dag_90 = generate_dag(90, density, regularity, fatness)
draw_dag(dag_90, "Generated DAG with 90 tasks")
print_dag_stats(dag_90)

dag_90 = assign_tasks_power_consumption(dag_90, core_pairs)

TaskScheduler(core_pairs, dag_90).schedule_tasks()
plot_schedule(core_pairs)
