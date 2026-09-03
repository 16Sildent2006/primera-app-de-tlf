#ifndef ORIENTE_DATA_HPP
#define ORIENTE_DATA_HPP

#include "graph.hpp"

inline Graph build_oriente_network() {
    Graph g;

    // --- NODOS (Ciudades / Puntos clave de Oriente) ---
    // Anzoátegui
    int barcelona      = g.add_node("Barcelona", "Anzoátegui", 10.1340, -64.6869);       // 0
    int plc            = g.add_node("Puerto La Cruz", "Anzoátegui", 10.2138, -64.6328);  // 1
    int guanta         = g.add_node("Guanta", "Anzoátegui", 10.2372, -64.5939);          // 2
    int piritu         = g.add_node("Píritu", "Anzoátegui", 10.0571, -65.0336);          // 3
    int clarines       = g.add_node("Clarines", "Anzoátegui", 9.9415, -65.1742);         // 4
    int anaco          = g.add_node("Anaco", "Anzoátegui", 9.4347, -64.4646);            // 5
    int cantaura       = g.add_node("Cantaura", "Anzoátegui", 9.3051, -64.3592);         // 6
    int el_tigre       = g.add_node("El Tigre", "Anzoátegui", 8.8875, -64.2454);         // 7
    int pariaguan      = g.add_node("Pariaguán", "Anzoátegui", 8.8550, -64.7100);        // 8

    // Monagas
    int maturin        = g.add_node("Maturín", "Monagas", 9.7457, -63.1793);             // 9
    int punta_de_mata  = g.add_node("Punta de Mata", "Monagas", 9.6917, -63.6300);      // 10
    int temblador      = g.add_node("Temblador", "Monagas", 9.0142, -62.6186);          // 11
    int caripe         = g.add_node("Caripe", "Monagas", 10.1667, -63.4833);             // 12

    // Sucre
    int cumana         = g.add_node("Cumaná", "Sucre", 10.4539, -64.1750);               // 13
    int carupano       = g.add_node("Carúpano", "Sucre", 10.6678, -63.2585);             // 14
    int cariaco        = g.add_node("Cariaco", "Sucre", 10.4950, -63.5539);              // 15
    int guiria         = g.add_node("Güiria", "Sucre", 10.5794, -62.3006);               // 16

    // Bolívar (Conexión Sur / Eje Industrial y Minero)
    int cd_bolivar     = g.add_node("Ciudad Bolívar", "Bolívar", 8.1292, -63.5408);      // 17
    int puerto_ordaz   = g.add_node("Puerto Ordaz", "Bolívar", 8.2974, -62.7303);        // 18
    int san_felix      = g.add_node("San Félix", "Bolívar", 8.3683, -62.6469);           // 19

    // --- ARISTAS (Conexiones Viales y Distancias en KM) ---
    // Zona Metropolitana Norte Anzoátegui
    g.add_edge(barcelona, plc, 12.0, "Av. Intercomunal", 1.0);
    g.add_edge(plc, guanta, 10.0, "Troncal 9", 1.0);
    g.add_edge(barcelona, piritu, 48.0, "Troncal 9 (Autopista)", 1.0);
    g.add_edge(piritu, clarines, 25.0, "Troncal 9", 1.05);

    // Eje Centro - Sur Anzoátegui (Troncal 16)
    g.add_edge(barcelona, anaco, 85.0, "Troncal 16", 1.0);
    g.add_edge(anaco, cantaura, 20.0, "Troncal 16", 1.0);
    g.add_edge(cantaura, el_tigre, 40.0, "Troncal 16", 1.0);
    g.add_edge(el_tigre, pariaguan, 55.0, "Troncal 15", 1.1);

    // Conexión Anzoátegui <-> Monagas
    g.add_edge(anaco, punta_de_mata, 110.0, "Carretera Anaco-Maturín", 1.15);
    g.add_edge(punta_de_mata, maturin, 45.0, "Troncal 13", 1.0);
    g.add_edge(barcelona, maturin, 180.0, "Vía Los Potocos / Troncal 13", 1.05);

    // Red interna de Monagas
    g.add_edge(maturin, temblador, 75.0, "Troncal 10", 1.05);
    g.add_edge(maturin, caripe, 80.0, "Vía Caripe El Guácharo", 1.2); // Zona montañosa

    // Conexión Norte Anzoátegui <-> Sucre (Troncal 9 Costera)
    g.add_edge(guanta, cumana, 80.0, "Troncal 9 (Costera)", 1.1);
    g.add_edge(barcelona, cumana, 92.0, "Troncal 9", 1.1);

    // Red de Sucre
    g.add_edge(cumana, cariaco, 75.0, "Troncal 9", 1.05);
    g.add_edge(cariaco, carupano, 45.0, "Troncal 9", 1.05);
    g.add_edge(carupano, guiria, 140.0, "Troncal 9 (Paria)", 1.2);
    g.add_edge(cariaco, caripe, 65.0, "Vía Cariaco-Caripe", 1.25); // Conexión Sucre - Monagas

    // Conexión Monagas <-> Sucre
    g.add_edge(maturin, carupano, 165.0, "Troncal 10 / Vía Carúpano", 1.15);

    // Conexión Sur hacia Bolívar
    g.add_edge(el_tigre, cd_bolivar, 130.0, "Troncal 16 (Puente Angostura)", 1.05);
    g.add_edge(cd_bolivar, puerto_ordaz, 105.0, "Autopista Simón Bolívar", 1.0);
    g.add_edge(puerto_ordaz, san_felix, 15.0, "Av. Guayana", 1.0);

    // Conexión Monagas Sur <-> Bolívar (Puente Orinoquia)
    g.add_edge(temblador, puerto_ordaz, 120.0, "Vía Los Pozos / Puente Orinoquia", 1.05);
    g.add_edge(el_tigre, puerto_ordaz, 195.0, "Troncal 16 + Orinoquia", 1.05);

    return g;
}

#endif // ORIENTE_DATA_HPP
