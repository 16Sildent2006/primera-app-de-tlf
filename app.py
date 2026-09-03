import os
import glob
import webbrowser
import flet as ft
from bridge.oriente_engine import OrienteTripEngine, Location, TripQuote
from bridge.pdf_generator import generate_quote_pdf
from bridge.docx_generator import generate_quote_docx
from typing import Optional

def open_file_safe(path: str):
    """Abre el archivo (Word o PDF) en la aplicación predeterminada."""
    abs_path = os.path.abspath(path)
    if abs_path.endswith(".docx"):
        # Intentar abrir directamente con Microsoft Word
        try:
            os.system(f'start winword "{abs_path}"')
        except Exception:
            pass
        try:
            os.system(f'start "" "{abs_path}"')
        except Exception:
            pass
    else:
        try:
            os.startfile(abs_path)
        except Exception:
            pass
        try:
            webbrowser.open("file:///" + abs_path.replace("\\", "/"))
        except Exception:
            pass

def open_folder(e=None):
    """Abre la carpeta de cotizaciones en el Explorador de Windows."""
    folder_path = os.path.abspath("cotizaciones")
    os.makedirs(folder_path, exist_ok=True)
    try:
        os.system(f'explorer "{folder_path}"')
    except Exception:
        pass

def main(page: ft.Page):
    page.title = "Fletes Oriente - Camión 350"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 420
    page.window.height = 860
    page.window.min_width = 380
    page.window.min_height = 700
    page.padding = 12
    page.scroll = ft.ScrollMode.ADAPTIVE

    # Inicializar motor C++
    try:
        engine = OrienteTripEngine()
        locations = engine.get_locations()
    except Exception as e:
        page.add(
            ft.Text(f"Error cargando motor C++: {e}", color=ft.Colors.RED_400)
        )
        return

    # Opciones de ciudades para dropdowns
    city_options = [
        ft.DropdownOption(
            key=str(loc.id),
            text=f"{loc.name} ({loc.state})"
        )
        for loc in sorted(locations, key=lambda x: (x.state, x.name))
    ]

    # Estado actual
    current_origin_id = locations[1].id if len(locations) > 1 else 0      # Puerto La Cruz
    current_dest_id = locations[9].id if len(locations) > 9 else 0        # Maturín
    current_quote: Optional[TripQuote] = None

    # --- CONTROLES UI ---

    def parse_float_safe(val_str: str, default: float = 0.0) -> float:
        try:
            return float(str(val_str).replace(",", ".").strip())
        except Exception:
            return default

    # Widgets del Resultado de Cotización
    total_price_text = ft.Text("$ 0.00", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT_400)
    distance_text = ft.Text("-- km", size=14, weight=ft.FontWeight.BOLD)
    time_text = ft.Text("--", size=14, weight=ft.FontWeight.BOLD)
    fuel_text = ft.Text("-- L", size=14, weight=ft.FontWeight.BOLD)
    breakdown_text = ft.Text("", size=12, color=ft.Colors.GREY_400)
    itinerary_col = ft.Column(spacing=4)
    status_snack_text = ft.Text("", size=12, color=ft.Colors.GREEN_400, text_align=ft.TextAlign.CENTER)
    recent_files_col = ft.Column(spacing=6)

    def refresh_recent_files():
        recent_files_col.controls.clear()
        files = sorted(glob.glob("cotizaciones/*.*"), key=os.path.getmtime, reverse=True)
        files = [f for f in files if f.endswith(".docx") or f.endswith(".pdf")]
        
        if not files:
            recent_files_col.controls.append(
                ft.Text("Aún no has generado cotizaciones.", size=11, color=ft.Colors.GREY_500)
            )
            return

        for fpath in files[:5]: # Mostrar los 5 más recientes
            fname = os.path.basename(fpath)
            abs_p = os.path.abspath(fpath)
            is_docx = fname.endswith(".docx")
            
            def create_click_handler(target_path):
                return lambda e: open_file_safe(target_path)

            icon_type = ft.Icons.DESCRIPTION if is_docx else ft.Icons.PICTURE_AS_PDF
            icon_color = ft.Colors.BLUE_400 if is_docx else ft.Colors.RED_400
            tipo_txt = "Documento Word (.docx)" if is_docx else "Documento PDF (.pdf)"

            recent_files_col.controls.append(
                ft.Container(
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    border_radius=8,
                    padding=8,
                    content=ft.Row(
                        controls=[
                            ft.Icon(icon_type, color=icon_color, size=22),
                            ft.Column(
                                controls=[
                                    ft.Text(fname, size=11, weight=ft.FontWeight.BOLD, no_wrap=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text(tipo_txt, size=9, color=ft.Colors.GREY_400)
                                ],
                                expand=True,
                                spacing=1
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_NEW,
                                tooltip="Abrir documento",
                                icon_color=ft.Colors.AMBER_400,
                                icon_size=18,
                                on_click=create_click_handler(abs_p)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
            )

    def recalculate(e=None):
        nonlocal current_quote
        try:
            orig_id = int(origin_dropdown.value)
            dest_id = int(dest_dropdown.value)
            cargo_pct = float(cargo_slider.value)
            price_km = parse_float_safe(price_km_input.value, 1.25)
            base_fee = parse_float_safe(base_fee_input.value, 25.0)
            is_round = bool(round_trip_switch.value)
            extras = parse_float_safe(extras_input.value, 0.0)

            quote = engine.calculate_trip(
                origin=orig_id,
                destination=dest_id,
                cargo_percent=cargo_pct,
                price_per_km=price_km,
                base_rate=base_fee,
                is_round_trip=is_round,
                return_discount_pct=0.30,
                extra_expenses=extras
            )

            current_quote = quote

            if quote and quote.found:
                total_price_text.value = f"$ {quote.total_price:.2f} USD"
                distance_text.value = f"{quote.effective_distance_km:.1f} km"
                
                # Formato de tiempo (ej: 2h 45m)
                total_mins = int(quote.estimated_hours * 60)
                hours = total_mins // 60
                mins = total_mins % 60
                time_text.value = f"{hours}h {mins}m"
                fuel_text.value = f"{quote.fuel_liters:.1f} Lts"

                # Desglose
                breakdown = f"• Base + Distancia: ${quote.base_price:.2f}\n• Recargo por Carga: ${quote.load_surcharge:.2f}"
                if is_round:
                    breakdown += f"\n• Retorno con Descuento: ${quote.return_cost:.2f}"
                if extras > 0:
                    breakdown += f"\n• Extras/Peajes: ${extras:.2f}"
                breakdown_text.value = breakdown

                # Itinerario visual
                itinerary_col.controls.clear()
                for i, node in enumerate(quote.path_nodes):
                    is_last = (i == len(quote.path_nodes) - 1)
                    itinerary_col.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.RADIO_BUTTON_CHECKED if (i == 0 or is_last) else ft.Icons.CIRCLE_OUTLINED,
                                    size=16,
                                    color=ft.Colors.AMBER_400 if (i == 0 or is_last) else ft.Colors.GREY_500
                                ),
                                ft.Text(
                                    f"{node.name} ({node.state})",
                                    size=13,
                                    weight=ft.FontWeight.BOLD if (i == 0 or is_last) else ft.FontWeight.NORMAL,
                                    color=ft.Colors.WHITE if (i == 0 or is_last) else ft.Colors.GREY_300
                                )
                            ],
                            spacing=8
                        )
                    )
            else:
                total_price_text.value = "Ruta no disponible"
                distance_text.value = "--"
                time_text.value = "--"
                fuel_text.value = "--"
                breakdown_text.value = "No se encontró conexión vial entre estas ciudades."
                itinerary_col.controls.clear()

            page.update()
        except Exception as err:
            total_price_text.value = "Error"
            breakdown_text.value = str(err)
            page.update()

    # Selector de Ciudades
    origin_dropdown = ft.Dropdown(
        label="Ciudad de Origen",
        options=city_options,
        value=str(current_origin_id),
        leading_icon=ft.Icons.MY_LOCATION,
        dense=True,
        border_radius=8,
        expand=True,
        on_select=recalculate
    )

    dest_dropdown = ft.Dropdown(
        label="Ciudad de Destino",
        options=city_options,
        value=str(current_dest_id),
        leading_icon=ft.Icons.LOCATION_ON,
        dense=True,
        border_radius=8,
        expand=True,
        on_select=recalculate
    )

    def swap_cities(e):
        temp = origin_dropdown.value
        origin_dropdown.value = dest_dropdown.value
        dest_dropdown.value = temp
        page.update()
        recalculate(None)

    swap_btn = ft.IconButton(
        icon=ft.Icons.SWAP_VERT,
        tooltip="Invertir Origen y Destino",
        icon_color=ft.Colors.AMBER_400,
        on_click=swap_cities
    )

    # Parámetros del Camión 350
    cargo_label = ft.Text("Nivel de Carga: 100% (Batea Completa - 3.500 kg)", size=13, weight=ft.FontWeight.W_500)
    
    def on_cargo_change(e):
        val = int(cargo_slider.value)
        kg_approx = int(3500 * (val / 100.0))
        if val == 0:
            cargo_label.value = "Nivel de Carga: 0% (Camión Vacío)"
        elif val < 50:
            cargo_label.value = f"Nivel de Carga: {val}% (~{kg_approx} kg - Carga Ligera)"
        elif val < 100:
            cargo_label.value = f"Nivel de Carga: {val}% (~{kg_approx} kg - Media Carga)"
        else:
            cargo_label.value = "Nivel de Carga: 100% (Batea Completa - 3.500 kg)"
        recalculate(None)

    cargo_slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=100,
        label="{value}%",
        active_color=ft.Colors.AMBER_500,
        on_change=on_cargo_change
    )

    price_km_input = ft.TextField(
        label="Precio / Km ($)",
        value="1.25",
        keyboard_type=ft.KeyboardType.NUMBER,
        dense=True,
        border_radius=8,
        width=120,
        prefix=ft.Text("$ "),
        on_change=lambda e: recalculate(None)
    )

    base_fee_input = ft.TextField(
        label="Tarifa Base ($)",
        value="25.00",
        keyboard_type=ft.KeyboardType.NUMBER,
        dense=True,
        border_radius=8,
        width=120,
        prefix=ft.Text("$ "),
        on_change=lambda e: recalculate(None)
    )

    round_trip_switch = ft.Switch(
        label="Ida y Vuelta (Retorno)",
        value=False,
        active_color=ft.Colors.AMBER_500,
        on_change=lambda e: recalculate(None)
    )

    extras_input = ft.TextField(
        label="Extras (Peajes / Ayudante) ($)",
        value="0.00",
        keyboard_type=ft.KeyboardType.NUMBER,
        dense=True,
        border_radius=8,
        width=150,
        prefix=ft.Text("$ "),
        on_change=lambda e: recalculate(None)
    )

    def open_docx_quote(e):
        if not current_quote or not current_quote.found:
            status_snack_text.value = "Selecciona una ruta válida antes de generar el documento."
            status_snack_text.color = ft.Colors.RED_400
            page.update()
            return

        try:
            params = {
                "cargo_percent": float(cargo_slider.value),
                "price_per_km": parse_float_safe(price_km_input.value, 1.25),
                "base_fee": parse_float_safe(base_fee_input.value, 25.0),
                "is_round_trip": bool(round_trip_switch.value),
                "extra_expenses": parse_float_safe(extras_input.value, 0.0)
            }

            docx_path = generate_quote_docx(current_quote, params)
            
            # Abrir en Word directamente
            open_file_safe(docx_path)

            filename = os.path.basename(docx_path)
            status_snack_text.value = f"¡Abriendo en Word!\nGuardado: cotizaciones/{filename}"
            status_snack_text.color = ft.Colors.GREEN_ACCENT_400
            
            # Actualizar lista de archivos
            refresh_recent_files()
            page.update()
        except Exception as err:
            status_snack_text.value = f"Error generando Word: {err}"
            status_snack_text.color = ft.Colors.RED_400
            page.update()

    def download_pdf_quote(e):
        if not current_quote or not current_quote.found:
            status_snack_text.value = "Selecciona una ruta válida antes de generar el PDF."
            status_snack_text.color = ft.Colors.RED_400
            page.update()
            return

        try:
            params = {
                "cargo_percent": float(cargo_slider.value),
                "price_per_km": parse_float_safe(price_km_input.value, 1.25),
                "base_fee": parse_float_safe(base_fee_input.value, 25.0),
                "is_round_trip": bool(round_trip_switch.value),
                "extra_expenses": parse_float_safe(extras_input.value, 0.0)
            }

            pdf_path = generate_quote_pdf(current_quote, params)
            open_file_safe(pdf_path)

            filename = os.path.basename(pdf_path)
            status_snack_text.value = f"¡PDF generado con éxito!\nGuardado: cotizaciones/{filename}"
            status_snack_text.color = ft.Colors.GREEN_ACCENT_400
            
            refresh_recent_files()
            page.update()
        except Exception as err:
            status_snack_text.value = f"Error generando PDF: {err}"
            status_snack_text.color = ft.Colors.RED_400
            page.update()

    # --- ENSAMBLAJE DE LA VISTA MÓVIL ---

    # Cabecera
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOCAL_SHIPPING, color=ft.Colors.AMBER_400, size=32),
                ft.Column(
                    controls=[
                        ft.Text("FLETES ORIENTE", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text("Cotizador Camión 350 • Motor C++", size=11, color=ft.Colors.GREY_400),
                    ],
                    spacing=1,
                    expand=True
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.Padding.only(bottom=8)
    )

    # Tarjeta de Ruta
    route_card = ft.Card(
        elevation=4,
        content=ft.Container(
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Text("1. SELECCIÓN DE RUTA", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[origin_dropdown, dest_dropdown],
                                spacing=10,
                                expand=True
                            ),
                            swap_btn
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    )
                ],
                spacing=8
            )
        )
    )

    # Tarjeta de Parámetros del Camión 350
    truck_card = ft.Card(
        elevation=4,
        content=ft.Container(
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Text("2. PARÁMETROS DEL CAMIÓN 350", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                    cargo_label,
                    cargo_slider,
                    ft.Row(
                        controls=[price_km_input, base_fee_input],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        controls=[round_trip_switch, extras_input],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=10
            )
        )
    )

    # Tarjeta de Resultados
    result_card = ft.Card(
        elevation=6,
        bgcolor=ft.Colors.SURFACE_CONTAINER,
        content=ft.Container(
            padding=16,
            content=ft.Column(
                controls=[
                    ft.Text("TOTAL A COBRAR", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300),
                    total_price_text,
                    ft.Divider(color=ft.Colors.GREY_700, height=12),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Distancia", size=11, color=ft.Colors.GREY_400),
                                    distance_text
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Tiempo Est.", size=11, color=ft.Colors.GREY_400),
                                    time_text
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("Combustible", size=11, color=ft.Colors.GREY_400),
                                    fuel_text
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND
                    ),
                    ft.Divider(color=ft.Colors.GREY_700, height=12),
                    ft.Text("Desglose del Costo:", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300),
                    breakdown_text
                ],
                spacing=6
            )
        )
    )

    # Tarjeta de Itinerario de Carretera
    itinerary_card = ft.Card(
        elevation=3,
        content=ft.Container(
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.MAP, size=18, color=ft.Colors.AMBER_400),
                            ft.Text("ITINERARIO DE RUTA (100% OFFLINE)", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                        ],
                        spacing=6
                    ),
                    itinerary_col
                ],
                spacing=10
            )
        )
    )

    # Botones de Acción (Word + PDF + Carpeta)
    action_buttons = ft.Column(
        controls=[
            ft.Button(
                content="Abrir Cotización en Word (DOCX)",
                icon=ft.Icons.DESCRIPTION,
                bgcolor=ft.Colors.BLUE_800,
                color=ft.Colors.WHITE,
                height=48,
                width=380,
                on_click=open_docx_quote
            ),
            ft.Row(
                controls=[
                    ft.Button(
                        content="Descargar PDF",
                        icon=ft.Icons.PICTURE_AS_PDF,
                        bgcolor=ft.Colors.RED_900,
                        color=ft.Colors.WHITE,
                        height=42,
                        expand=True,
                        on_click=download_pdf_quote
                    ),
                    ft.IconButton(
                        icon=ft.Icons.FOLDER_OPEN,
                        tooltip="Abrir Carpeta de Archivos",
                        icon_color=ft.Colors.AMBER_400,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                        icon_size=22,
                        on_click=open_folder
                    )
                ],
                spacing=8
            )
        ],
        spacing=8
    )

    # Tarjeta de Historial / Archivos Guardados
    saved_files_card = ft.Card(
        elevation=3,
        content=ft.Container(
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FOLDER_SPECIAL, size=18, color=ft.Colors.AMBER_400),
                            ft.Text("COTIZACIONES GENERADAS", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.AMBER_400),
                        ],
                        spacing=6
                    ),
                    recent_files_col,
                    ft.TextButton(
                        content="Abrir Carpeta en Windows Explorer",
                        icon=ft.Icons.FOLDER,
                        on_click=open_folder
                    )
                ],
                spacing=8
            )
        )
    )

    # Agregar todo a la página
    page.add(
        header,
        route_card,
        truck_card,
        result_card,
        itinerary_card,
        ft.Container(
            content=ft.Column(
                controls=[action_buttons, status_snack_text],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8
            ),
            alignment=ft.Alignment.CENTER,
            padding=ft.Padding.only(top=6, bottom=10)
        ),
        saved_files_card
    )

    # Inicialización
    refresh_recent_files()
    recalculate(None)

if __name__ == "__main__":
    ft.run(main)
