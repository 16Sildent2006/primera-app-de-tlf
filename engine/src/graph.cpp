#include "../include/graph.hpp"
#include <queue>
#include <algorithm>
#include <cctype>

Graph::Graph() {}

int Graph::add_node(const std::string& name, const std::string& state, double lat, double lon) {
    int new_id = static_cast<int>(nodes.size());
    nodes.emplace_back(new_id, name, state, lat, lon);
    adj_list.emplace_back(); // Agregar lista de adyacencia para el nuevo nodo
    return new_id;
}

void Graph::add_edge(int from, int to, double distance_km, const std::string& road_name, double condition, bool bidirectional) {
    if (from < 0 || from >= static_cast<int>(nodes.size()) || to < 0 || to >= static_cast<int>(nodes.size())) {
        return;
    }
    adj_list[from].emplace_back(to, distance_km, road_name, condition);
    if (bidirectional) {
        adj_list[to].emplace_back(from, distance_km, road_name, condition);
    }
}

const Node* Graph::get_node(int id) const {
    if (id >= 0 && id < static_cast<int>(nodes.size())) {
        return &nodes[id];
    }
    return nullptr;
}

const std::vector<Node>& Graph::get_all_nodes() const {
    return nodes;
}

int Graph::get_node_count() const {
    return static_cast<int>(nodes.size());
}

static std::string to_lower_str(const std::string& s) {
    std::string result = s;
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c){ return static_cast<char>(std::tolower(c)); });
    return result;
}

int Graph::find_node_by_name(const std::string& name) const {
    std::string search = to_lower_str(name);
    for (const auto& node : nodes) {
        if (to_lower_str(node.name) == search) {
            return node.id;
        }
    }
    // Búsqueda por subcadena
    for (const auto& node : nodes) {
        if (to_lower_str(node.name).find(search) != std::string::npos) {
            return node.id;
        }
    }
    return -1;
}

PathResult Graph::find_shortest_path(int start_node_id, int end_node_id) const {
    PathResult result;
    int n = static_cast<int>(nodes.size());

    if (start_node_id < 0 || start_node_id >= n || end_node_id < 0 || end_node_id >= n) {
        return result;
    }

    if (start_node_id == end_node_id) {
        result.found = true;
        result.total_distance_km = 0.0;
        result.path_node_ids.push_back(start_node_id);
        return result;
    }

    const double INF = std::numeric_limits<double>::infinity();
    std::vector<double> dist(n, INF);
    std::vector<int> prev(n, -1);
    std::vector<std::string> prev_road(n, "");

    // Min-priority queue: pair<distancia, node_id>
    typedef std::pair<double, int> DistNode;
    std::priority_queue<DistNode, std::vector<DistNode>, std::greater<DistNode>> pq;

    dist[start_node_id] = 0.0;
    pq.push({0.0, start_node_id});

    while (!pq.empty()) {
        auto [current_dist, u] = pq.top();
        pq.pop();

        if (current_dist > dist[u]) {
            continue;
        }

        if (u == end_node_id) {
            break; // Llegamos al destino óptimo
        }

        for (const auto& edge : adj_list[u]) {
            int v = edge.to_node_id;
            double weight = edge.distance_km * edge.condition_factor;
            if (dist[u] + weight < dist[v]) {
                dist[v] = dist[u] + weight;
                prev[v] = u;
                prev_road[v] = edge.road_name;
                pq.push({dist[v], v});
            }
        }
    }

    if (dist[end_node_id] == INF) {
        result.found = false;
        return result;
    }

    // Reconstrucción del camino desde destino hasta origen
    std::vector<int> path;
    std::vector<std::string> roads;
    double actual_real_distance = 0.0;

    int curr = end_node_id;
    while (curr != -1) {
        path.push_back(curr);
        int p = prev[curr];
        if (p != -1) {
            roads.push_back(prev_road[curr]);
            // Buscar la distancia real del arco
            for (const auto& edge : adj_list[p]) {
                if (edge.to_node_id == curr) {
                    actual_real_distance += edge.distance_km;
                    break;
                }
            }
        }
        curr = p;
    }

    std::reverse(path.begin(), path.end());
    std::reverse(roads.begin(), roads.end());

    result.found = true;
    result.total_distance_km = actual_real_distance;
    result.path_node_ids = path;
    result.road_segments = roads;

    return result;
}
