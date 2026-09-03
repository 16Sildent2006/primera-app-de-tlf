#include "../include/c_api.h"
#include "../include/graph.hpp"
#include "../include/oriente_data.hpp"
#include "../include/pricing.hpp"
#include <cstring>
#include <memory>

static std::unique_ptr<Graph> g_oriente_graph = nullptr;

static Graph& get_graph() {
    if (!g_oriente_graph) {
        g_oriente_graph = std::make_unique<Graph>(build_oriente_network());
    }
    return *g_oriente_graph;
}

extern "C" {

void oriente_init_engine() {
    g_oriente_graph = std::make_unique<Graph>(build_oriente_network());
}

int oriente_get_node_count() {
    return get_graph().get_node_count();
}

int oriente_get_node_by_id(int id, struct CNodeInfo* out_node) {
    if (!out_node) return 0;
    const Node* n = get_graph().get_node(id);
    if (!n) return 0;

    out_node->id = n->id;
    std::strncpy(out_node->name, n->name.c_str(), sizeof(out_node->name) - 1);
    out_node->name[sizeof(out_node->name) - 1] = '\0';

    std::strncpy(out_node->state, n->state.c_str(), sizeof(out_node->state) - 1);
    out_node->state[sizeof(out_node->state) - 1] = '\0';

    out_node->latitude = n->latitude;
    out_node->longitude = n->longitude;
    return 1;
}

int oriente_find_node_by_name(const char* name) {
    if (!name) return -1;
    return get_graph().find_node_by_name(std::string(name));
}

struct CTripCalculationResult oriente_calculate_trip(
    int origin_id,
    int dest_id,
    double cargo_percent,
    double price_per_km,
    double base_rate,
    int is_round_trip,
    double return_discount_pct,
    double extra_expenses
) {
    struct CTripCalculationResult res;
    std::memset(&res, 0, sizeof(res));

    Graph& g = get_graph();
    PathResult path = g.find_shortest_path(origin_id, dest_id);

    if (!path.found) {
        res.status = 1; // Ruta no encontrada
        return res;
    }

    Truck350Params params;
    params.cargo_percent = cargo_percent;
    params.price_per_km = price_per_km;
    params.base_rate = base_rate;
    params.is_round_trip = (is_round_trip != 0);
    params.return_discount_pct = return_discount_pct;
    params.extra_expenses = extra_expenses;

    QuoteResult quote = PricingCalculator::calculate_truck350_quote(path.total_distance_km, params);

    res.status = 0;
    res.total_distance_km = path.total_distance_km;
    res.effective_distance_km = quote.effective_distance_km;
    res.total_price = quote.total_price;
    res.base_price = quote.base_price;
    res.load_surcharge = quote.load_surcharge;
    res.return_cost = quote.return_cost;
    res.estimated_liters_fuel = quote.estimated_liters_fuel;
    res.estimated_hours = quote.estimated_hours;

    int count = static_cast<int>(path.path_node_ids.size());
    if (count > 100) count = 100;
    res.path_length = count;

    for (int i = 0; i < count; ++i) {
        res.path_node_ids[i] = path.path_node_ids[i];
    }

    return res;
}

}
