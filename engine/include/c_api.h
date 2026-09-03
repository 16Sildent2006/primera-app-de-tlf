#ifndef C_API_H
#define C_API_H

#ifdef _WIN32
    #define EXPORT_API __declspec(dllexport)
#else
    #define EXPORT_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Estructura C para un nodo/ciudad
struct CNodeInfo {
    int id;
    char name[64];
    char state[64];
    double latitude;
    double longitude;
};

// Estructura C para el resultado de cálculo completo
struct CTripCalculationResult {
    int status;                  // 0 = Éxito, 1 = Error/No encontrado
    double total_distance_km;    // Distancia de ida
    double effective_distance_km;// Distancia total considerada
    double total_price;          // Precio final total
    double base_price;           // Precio base
    double load_surcharge;       // Recargo por peso
    double return_cost;          // Costo de retorno
    double estimated_liters_fuel;// Consumo estimado de combustible
    double estimated_hours;      // Tiempo estimado en horas
    int path_length;             // Cantidad de nodos en la ruta
    int path_node_ids[100];      // Secuencia de IDs de ciudades
};

// Inicializa o resetea el grafo de Oriente
EXPORT_API void oriente_init_engine();

// Obtiene la cantidad de nodos registrados
EXPORT_API int oriente_get_node_count();

// Obtiene la información de un nodo por su ID
EXPORT_API int oriente_get_node_by_id(int id, struct CNodeInfo* out_node);

// Busca un nodo por su nombre exacto o aproximado
EXPORT_API int oriente_find_node_by_name(const char* name);

// Calcula la ruta y cotización completa para el Camión 350
EXPORT_API struct CTripCalculationResult oriente_calculate_trip(
    int origin_id,
    int dest_id,
    double cargo_percent,
    double price_per_km,
    double base_rate,
    int is_round_trip,
    double return_discount_pct,
    double extra_expenses
);

#ifdef __cplusplus
}
#endif

#endif // C_API_H
