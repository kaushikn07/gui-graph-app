import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import random

class GraphVisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Algorithm Visualization")
        self.graph = nx.DiGraph()
        self.path_edges = []  
        self.setup_gui()
    def setup_gui(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        tk.Label(control_frame, text="Select Algorithm").pack()
        self.algorithm_var = tk.StringVar()
        algorithms = ["Bellman-Ford", "Floyd-Warshall", "Dijkstra"]
        algorithm_menu = ttk.Combobox(control_frame, textvariable=self.algorithm_var, values=algorithms)
        algorithm_menu.pack()
        tk.Label(control_frame, text="Source Node").pack()
        self.source_entry = tk.Entry(control_frame)
        self.source_entry.pack()
        tk.Label(control_frame, text="Destination Node").pack()
        self.destination_entry = tk.Entry(control_frame)
        self.destination_entry.pack()
        tk.Button(control_frame, text="Run Algorithm", command=self.run_algorithm).pack()
        tk.Label(control_frame, text="Add Node").pack()
        self.node_entry = tk.Entry(control_frame)
        self.node_entry.pack()
        tk.Button(control_frame, text="Add Node", command=self.add_node).pack()
        tk.Label(control_frame, text="Add Edge").pack()
        self.edge_entry = tk.Entry(control_frame)
        self.edge_entry.insert(0, "Format: node1,node2,weight")
        self.edge_entry.pack()
        tk.Button(control_frame, text="Add Edge", command=self.add_edge).pack()
        tk.Label(control_frame, text="Random Graph Generation").pack()
        tk.Label(control_frame, text="Nodes").pack()
        self.node_count_entry = tk.Entry(control_frame)
        self.node_count_entry.pack()
        tk.Label(control_frame, text="Edge Probability (0-1)").pack()
        self.edge_prob_entry = tk.Entry(control_frame)
        self.edge_prob_entry.pack()
        tk.Button(control_frame, text="Generate Random Graph", command=self.generate_random_graph).pack()
        self.info_text = tk.Text(control_frame, height=10, width=30, wrap=tk.WORD)
        self.info_text.pack()
    def add_node(self):
        node = self.node_entry.get().strip()
        if node:
            self.graph.add_node(node)
            self.update_graph_display()
        else:
            messagebox.showerror("Input Error", "Node name cannot be empty.")
    def add_edge(self):
        edge_input = self.edge_entry.get().strip().split(',')
        if len(edge_input) == 3:
            node1, node2, weight = edge_input
            try:
                weight = float(weight)
                self.graph.add_edge(node1, node2, weight=weight)
                self.update_graph_display()
            except ValueError:
                messagebox.showerror("Invalid Input", "Weight must be a number.")
        else:
            messagebox.showerror("Input Error", "Edge format should be: node1,node2,weight.")
    def generate_random_graph(self):
        try:
            node_count = int(self.node_count_entry.get())
            edge_prob = float(self.edge_prob_entry.get())
            if node_count <= 0 or not (0 <= edge_prob <= 1):
                raise ValueError("Invalid node count or probability.")
            self.graph.clear()
            nodes = range(node_count)
            self.graph.add_nodes_from(nodes)
            for node1 in nodes:
                for node2 in nodes:
                    if node1 != node2 and random.random() < edge_prob:
                        self.graph.add_edge(node1, node2)
            self.update_graph_display()
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid integers for node count and a probability between 0 and 1.")
    def update_graph_display(self):
        self.ax.clear()
        pos = nx.spring_layout(self.graph)
        edge_colors = ["red" if edge in self.path_edges else "black" for edge in self.graph.edges()]
        nx.draw(self.graph, pos, with_labels=True, ax=self.ax, node_color='lightblue', font_weight='bold')
        nx.draw_networkx_edges(self.graph, pos, edgelist=self.graph.edges(), edge_color=edge_colors, ax=self.ax)
        self.canvas.draw()
        self.update_info_text()
    def update_info_text(self):
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, "Nodes:\n")
        self.info_text.insert(tk.END, f"{list(self.graph.nodes)}\n\n")
        self.info_text.insert(tk.END, "Edges:\n")
        self.info_text.insert(tk.END, f"{list(self.graph.edges)}\n")
    def run_algorithm(self):
        algorithm = self.algorithm_var.get()
        source = self.source_entry.get().strip()
        destination = self.destination_entry.get().strip()
        if not self.graph.nodes:
            messagebox.showerror("Input Error", "The graph is empty. Please add nodes or generate a graph.")
            return
        try:
            if isinstance(next(iter(self.graph.nodes)), int):
                source = int(source)
                destination = int(destination)
        except ValueError:
            messagebox.showerror("Input Error", "Node names must match the type of nodes in the graph (e.g., integers or strings).")
            return
        if source not in self.graph.nodes:
            messagebox.showerror("Input Error", f"Source node '{source}' does not exist in the graph.")
            return
        if destination not in self.graph.nodes:
            messagebox.showerror("Input Error", f"Destination node '{destination}' does not exist in the graph.")
            return
 
        self.path_edges.clear()
        self.path = [] 
    
        if algorithm == "Bellman-Ford":
            self.run_bellman_ford(source, destination)
        elif algorithm == "Floyd-Warshall":
            self.run_floyd_warshall(source, destination)
        elif algorithm == "Dijkstra":
            self.run_dijkstra(source, destination)
        else:
            messagebox.showerror("Algorithm Error", "Please select a valid algorithm.")
            return
    
        self.update_graph_display()
        self.display_path()
    def run_bellman_ford(self, source, destination):
        try:
            distances, paths = nx.single_source_bellman_ford(self.graph, source)
            if destination in paths:
                self.highlight_path(paths[destination])
        except nx.NetworkXUnbounded:
            messagebox.showerror("Algorithm Error", "Negative weight cycle detected in the graph.")
    def run_floyd_warshall(self, source, destination):
        try:
            all_pairs_paths = dict(nx.floyd_warshall_predecessor_and_distance(self.graph)[0])
            path = self.reconstruct_path(all_pairs_paths, source, destination)
            if path:
                self.highlight_path(path)
        except KeyError:
            messagebox.showerror("Algorithm Error", "No path exists between the source and destination.")
    def run_dijkstra(self, source, destination):
        distances, paths = nx.single_source_dijkstra(self.graph, source)
        if destination in paths:
            self.highlight_path(paths[destination])
    def highlight_path(self, path):
        self.path_edges.extend([(path[i], path[i+1]) for i in range(len(path) - 1)])
        self.path = path  # Store the path
    def display_path(self):
        if not self.path:
            self.info_text.insert(tk.END, "\nNo path found between the source and destination.\n")
        else:
            self.info_text.insert(tk.END, "\nPath:\n")
            self.info_text.insert(tk.END, " -> ".join(map(str, self.path)) + "\n")
    def reconstruct_path(self, predecessors, source, target):
        path = []
        while target in predecessors:
            path.insert(0, target)
            target = predecessors[target]
            if target == source:
                path.insert(0, source)
                return path
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphVisualizationApp(root)
    root.mainloop()
