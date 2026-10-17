import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
intersections = result.fetchall()

result = cur.execute("SELECT intersection_name FROM INTERSECTION")
intersection_names = result.fetchall()

########################################################fix intersection naming to impliment dropdowns

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

def shortest_path(mode):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM INTERSECTION")
    intersection_info = result.fetchall()
    print(len(intersection_info))


    result = cur.execute("SELECT * FROM path")
    path_info = result.fetchall()
    
    g = Graph(len(intersection_info))

    # Create mapping: db_id -> internal index (0..n-1)
    id_to_index = {}
    for i, section in enumerate(intersection_info):
        db_id = section[0]    # primary key in INTERSECTION
        label = section[1]    # human-readable name e.g. 'Northwood'
        id_to_index[db_id] = i
        g.add_vertex_data(i, label)   # use contiguous index

    # Debug: show samples
    print("num_nodes:", len(intersection_info))
    print("id_to_index sample:", list(id_to_index.items())[:10])
    print("path_info sample:", path_info[:5])

    col_map = {'distance': 3, 'time': 4}   # adjust indices if your schema differs
    if mode not in col_map:
        raise ValueError(f"Unknown mode {mode!r}; choose one of {list(col_map)}")
    weight_col = col_map[mode]

    # Add edges using the mapping and guard against missing nodes
    for section in path_info:
        from_db = section[1]
        to_db = section[2]
        weight = float(section[weight_col])

        if from_db not in id_to_index or to_db not in id_to_index:
            raise ValueError(f"Edge references missing node: {section}")

        u = id_to_index[from_db]
        v = id_to_index[to_db]

        g.add_edge(u, v, weight)
        g.add_edge(v, u, weight) 



    distance, path = g.dijkstra('Halswell', 'Sumner')
    print(f"Path: {path}, Distance: {distance}")
    return (f"Path: {path}, Distance: {distance:.1f}")

    

@app.route("/hi", methods=["GET", "POST"])
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

@app.route("/", methods=["GET", "POST"])
def home():
    print(intersection_names[0][0])
    languages = intersection_names
    selected_language = None

    if request.method == "POST":
        # 2. Extract the user selection using the matching HTML 'name' attribute
        selected_language = request.form.get("programming_language")

    # 3. Pass both the list and the selection context back to the user
    return render_template("home.html", languages=languages, selection=selected_language)


@app.route('/time')
def time():
    return shortest_path("time")

@app.route('/distance')
def distance():
    return shortest_path("distance")