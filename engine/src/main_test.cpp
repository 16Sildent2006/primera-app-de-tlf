#include <iostream>
#include <iomanip>
#include "../include/graph.hpp"
#include "../include/oriente_data.hpp"
#include "../include/pricing.hpp"

int main() {
    std::cout << "========================================================\n";
    std::cout << "  MOTOR DE GRAFOS DE ORIENTE - PRUEBA DE RUTAS Y FLETES\n";
    std::cout << "========================================================\n\n";

    Graph g = build_oriente_network();
    std::cout << "[+] Red vial de Oriente cargada con " << g.get_node_count() << " ciudades/nodos.\n\n";

    // Prueba 1: De Puerto La Cruz (1) a Maturín (9)
    int origin = g.find_node_by_name("Puerto La Cruz");
    int dest = g.find_node_by_name("Maturín");

    std::cout << ">> Calculando ruta: " << g.get_node(origin)->name << " -> " << g.get_node(dest)->name << "\n";
    PathResult path = g.find_shortest_path(origin, dest);

    if (path.found) {
        std::cout << "    Ruta encontrada! Distancia total: " << path.total_distance_km << " km\n";
        std::cout << "    Paradas / Nodos intermedios:\n    ";
        for (size_t i = 0; i < path.path_node_ids.size(); ++i) {
            std::cout << g.get_node(path.path_node_ids[i])->name;
            if (i + 1 < path.path_node_ids.size()) std::cout << " -> ";
        }
        std::cout << "\n\n";

        // Cotización Camión 350 con 80% de carga y $1.30/km
        Truck350Params params;
        params.cargo_percent = 80.0;
        params.price_per_km = 1.30;
        params.base_rate = 25.0;
        params.is_round_trip = false;

        QuoteResult quote = PricingCalculator::calculate_truck350_quote(path.total_distance_km, params);

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "    --- DETALLE DE COTIZACIÓN (CAMIÓN 350) ---\n";
        std::cout << "    * Porcentaje de Carga: " << params.cargo_percent << "%\n";
        std::cout << "    * Tarifa por KM: $" << params.price_per_km << " / km\n";
        std::cout << "    * Tarifa Base: $" << quote.base_price << "\n";
        std::cout << "    * Recargo por Carga/Peso: $" << quote.load_surcharge << "\n";
        std::cout << "    * Combustible Estimado: " << quote.estimated_liters_fuel << " Litros\n";
        std::cout << "    * Tiempo Estimado: " << quote.estimated_hours << " Horas\n";
        std::cout << "    ==========================================\n";
        std::cout << "    >>> PRECIO TOTAL DEL FLETE: $" << quote.total_price << " <<<\n";
        std::cout << "    ==========================================\n\n";
    } else {
        std::cout << "[-] Error: Ruta no encontrada.\n";
    }

    // Prueba 2: De Cumaná (Sucre) a Puerto Ordaz (Bolívar)
    origin = g.find_node_by_name("Cumaná");
    dest = g.find_node_by_name("Puerto Ordaz");

    std::cout << ">> Calculando ruta larga: " << g.get_node(origin)->name << " -> " << g.get_node(dest)->name << "\n";
    path = g.find_shortest_path(origin, dest);

    if (path.found) {
        std::cout << "    Ruta encontrada! Distancia total: " << path.total_distance_km << " km\n";
        std::cout << "    Itinerario: ";
        for (size_t i = 0; i < path.path_node_ids.size(); ++i) {
            std::cout << g.get_node(path.path_node_ids[i])->name;
            if (i + 1 < path.path_node_ids.size()) std::cout << " -> ";
        }
        std::cout << "\n\n";
    }

    return 0;
}
