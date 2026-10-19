import sqlite3
from flask import Flask, render_template, request
from flask import request, redirect, url_for, render_template

app = Flask(__name__)

con = sqlite3.connect("database.db")
cur = con.cursor()

result = cur.execute("SELECT * FROM INTERSECTION")
intersections = result.fetchall()

result = cur.execute("SELECT intersection_name FROM INTERSECTION")
intersection_names_initiall = result.fetchall()
intersection_names = []
for x in range(len(intersection_names_initiall)):
    intersection_names.append(intersection_names_initiall[x][0])
intersection_names.sort()


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

def shortest_path(mode, start_location, end_location):
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



    distance, path = g.dijkstra(start_location, end_location)
    print(f"Path: {path}, Distance: {distance}")

    return render_template("success.html", path=path, mode=mode.capitalize(), distance=round(distance, 1))

@app.route("/", methods=["GET", "POST"])
def home():
    languages = intersection_names
    selected_language = None
    start_location = ""
    end_location = ""

    if request.method == "POST":
        start_location = request.form.get("start_location")
        end_location = request.form.get("end_location")
        # validate they exist here if you want
        return redirect(url_for('time', start=start_location, end=end_location))

    return render_template("home.html", languages=languages, selection=selected_language, start_location=start_location, end_location=end_location)


@app.route('/shortest')
def shortest():
    mode = request.args.get('mode')
    start = request.args.get('start')
    end = request.args.get('end')
    if not start or not end or mode not in ('time', 'distance'):
        return render_template("shortest.html")
    return shortest_path(mode, start, end), "shortest.html"