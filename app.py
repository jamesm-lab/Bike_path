import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
path_id = result.fetchall()

class Graph:
    def __init__(self, size):
        self.adj_matrix = [[0] * size for _ in range(size)]
        self.size = size
        self.vertex_data = [''] * size

    def add_edge(self, u, v, weight):
        if 0 <= u < self.size and 0 <= v < self.size:
            self.adj_matrix[u][v] = weight
            #self.adj_matrix[v][u] = weight   For undirected graph

    def add_vertex_data(self, vertex, data):
        if 0 <= vertex < self.size:
            self.vertex_data[vertex] = data

    def get_path(self, predecessors, start_vertex, end_vertex):
        path = []
        current = self.vertex_data.index(end_vertex)
        while current is not None:
            path.insert(0, self.vertex_data[current])
            current = predecessors[current]
            if current == self.vertex_data.index(start_vertex):
                path.insert(0, start_vertex)
                break
        return '->'.join(path)  # Join the vertices with '->'
    def dijkstra(self, start_vertex_data, end_vertex_data):
        start_vertex = self.vertex_data.index(start_vertex_data)
        end_vertex = self.vertex_data.index(end_vertex_data)
        distances = [float('inf')] * self.size
        predecessors = [None] * self.size
        distances[start_vertex] = 0
        visited = [False] * self.size

    

        for _ in range(self.size):
            min_distance = float('inf')
            u = None
            for i in range(self.size):
                if not visited[i] and distances[i] < min_distance:
                    min_distance = distances[i]
                    u = i

            if u is None or u == end_vertex:
                print(f"Breaking out of loop. Current vertex: {self.vertex_data[u]}")
                print(f"Distances: {distances}")
                break

            visited[u] = True
            print(f"Visited vertex: {self.vertex_data[u]}")

            for v in range(self.size):
                if self.adj_matrix[u][v] != 0 and not visited[v]:
                    alt = distances[u] + self.adj_matrix[u][v]
                    if alt < distances[v]:
                        distances[v] = alt
                        predecessors[v] = u

        return distances[end_vertex], self.get_path(predecessors, start_vertex_data, end_vertex_data)



@app.route("/", methods=["GET", "POST"])
def index():
    # The default background image that always stays on screen
    base_image = "hello.jpg"

    # List your transparent overlay files here
    overlay_options = {
        "option1": "le_png.png",
        "option2": "img1.jpg",
    }

    selected_option = None
    overlay_image = None

    if request.method == "POST":
        # Get the option selected by the user
        selected_option = request.form.get("overlay_choice")
        # Find the matching transparent image filename
        overlay_image = overlay_options.get(selected_option)

    return render_template(
        "index.html",
        base_image=base_image,
        overlay_image=overlay_image,
        selected_option=selected_option,
    )

@app.route("/hi", methods=["GET", "POST"])
def hi():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM INTERSECTION")
    path_id = result.fetchall()

    g = Graph(size=7)

    for section in path_id:
        g.add_vertex_data(section[0], section[1])

   
    

  

    g.add_edge(3, 0, 4)  # D -> A, weight 4
    g.add_edge(3, 4, 2)  # D -> E, weight 2
    g.add_edge(0, 2, 3)  # A -> C, weight 3
    g.add_edge(0, 4, 4)  # A -> E, weight 4
    g.add_edge(4, 2, 4)  # E -> C, weight 4
    g.add_edge(4, 6, 5)  # E -> G, weight 5
    g.add_edge(2, 5, 5)  # C -> F, weight 5
    g.add_edge(1, 2, 2)  # B -> C, weight 2
    g.add_edge(1, 5, 2)  # B -> F, weight 2
    g.add_edge(6, 5, 5)  # G -> F, weight 5
        # ... (rest of the graph setup)
    distance, path = g.dijkstra('Northwood', 'Heathcote Valley')
    print(f"Path: {path}, Distance: {distance}")
    return (f"Path: {path}, Distance: {distance}")