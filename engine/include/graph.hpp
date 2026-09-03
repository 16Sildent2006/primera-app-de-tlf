#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <string>
#include <vector>
#include <limits>

// Representación de un punto o ciudad geográfica
struct Node {
    int id;
    std::string name;
    std::string state;
    double latitude;
    double longitude;

    Node() : id(-1), name(""), state(""), latitude(0.0), longitude(0.0) {}
    Node(int id, const std::string& name, const std::string& state, double lat, double lon)
        : id(id), name(name), state(state), latitude(lat), longitude(lon) {}
};

// Representación de una conexión vial (Arista)
struct Edge {
    int to_node_id;
    double distance_km;
    std::string road_name;  // Ej: "Troncal 9", "Troncal 16"
    double condition_factor; // 1.0 = excelente, 1.2 = vía regular/lenta

    Edge(int to, double dist, const std::string& road = "Vía Principal", double cond = 1.0)
        : to_node_id(to), distance_km(dist), road_name(road), condition_factor(cond) {}
};

// Resultado de una ruta calculada
struct PathResult {
    bool found;
    double total_distance_km;
    std::vector<int> path_node_ids; // Secuencia de IDs de ciudades recorridas
    std::vector<std::string> road_segments; // Nombres de vías tomadas

    PathResult() : found(false), total_distance_km(0.0) {}
};

class Graph {
private:
    std::vector<Node> nodes;
    std::vector<std::vector<Edge>> adj_list;

public:
    Graph();

    int add_node(const std::string& name, const std::string& state, double lat, double lon);
    void add_edge(int from, int to, double distance_km, const std::string& road_name = "Vía Principal", double condition = 1.0, bool bidirectional = true);

    const Node* get_node(int id) const;
    const std::vector<Node>& get_all_nodes() const;
    int get_node_count() const;
    int find_node_by_name(const std::string& name) const;

    // Algoritmo de Dijkstra para la ruta más corta
    PathResult find_shortest_path(int start_node_id, int end_node_id) const;
};

#endif // GRAPH_HPP
