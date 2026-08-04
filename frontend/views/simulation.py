import flet as ft
from frontend import api_client

def get_simulation_view(page: ft.Page, user_data, plan_months, on_start_workout):
    user_id = user_data["id_usuario"]
    peso_inicial = user_data["peso_actual_kg"]
    
    # Obtener el plan de entrenamiento para este usuario
    plan = api_client.obtener_plan_entrenamiento(user_id)
    bloques = plan.get("bloques_mensuales", [])
    
    # Estadísticas estimadas iniciales
    grasa_inicial = 22.0 if user_data["deporte_elegido"] == "Fitness / Gimnasio" else 18.0

    # Elementos dinámicos del Avatar y Estadísticas
    img_avatar = ft.Image(
        src=user_data.get("avatar_comic_url", "https://api.dicebear.com/7.x/pixel-art/svg?seed=roky"),
        width=180,
        height=180,
        fit="contain",
        animate_scale=ft.Animation(300, "easeOut") # Animación al cambiar de tamaño
    )
    
    # Etiquetas de estadísticas flotantes
    lbl_weight = ft.Text(f"{peso_inicial} kg", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_plan_status = ft.Text(f"Mes 0 de {plan_months}", size=14, color="#8B949E")
    lbl_muscle = ft.Text("+0.0 kg", size=18, weight=ft.FontWeight.BOLD, color="#00FF66")
    lbl_fat = ft.Text(f"{grasa_inicial}%", size=18, weight=ft.FontWeight.BOLD, color="#00FF66")

    # Contenedores flotantes estéticos
    def create_stat_card(title, value_control, icon):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([ft.Icon(icon, size=16, color="#00F0FF"), ft.Text(title, size=11, color="#8B949E")], spacing=4),
                    value_control
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            bgcolor="#161B22",
            padding=10,
            border_radius=8,
            border=ft.Border.all(1, "#1F2937"),
            width=130,
            height=60
        )

    card_weight = create_stat_card("PESO ESTIMADO", lbl_weight, ft.Icons.MONITOR_WEIGHT)
    card_plan = create_stat_card("PROGRESO", lbl_plan_status, ft.Icons.CALENDAR_MONTH)
    card_muscle = create_stat_card("MÚSCULO GANADO", lbl_muscle, ft.Icons.FITNESS_CENTER)
    card_fat = create_stat_card("GRASA CORPORAL", lbl_fat, ft.Icons.PERCENT)

    # Subtítulo del control de simulación
    lbl_transform_title = ft.Text("Mes 0 de 3 (Inicio)", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    
    # Lista de ejercicios del panel inferior
    exercises_column = ft.Column(spacing=8)

    def actualizar_rutina_hoy(mes_index):
        exercises_column.controls.clear()
        
        # Buscar el bloque del mes correspondiente (1-indexed)
        # Si mes_index es 0, mostramos la rutina del Mes 1 (punto de partida)
        target_mes = max(1, mes_index)
        bloque_mes = None
        for b in bloques:
            if b["mes"] == target_mes:
                bloque_mes = b
                break
                
        if bloque_mes:
            # Obtener ejercicios del Lunes de esa semana por defecto
            rutina_semanal = bloque_mes.get("rutina_semanal", [])
            if rutina_semanal:
                hoy = rutina_semanal[0] # Lunes
                exercises_column.controls.append(
                    ft.Text(f"Hoy ({hoy['dia']}) - {hoy['grupo_muscular']}", size=14, color="#00F0FF", weight=ft.FontWeight.W_500)
                )
                for ej in hoy.get("ejercicios", []):
                    exercises_column.controls.append(
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=14, color="#00FF66"),
                                ft.Text(f"{ej['nombre']}", size=14, color="#FFFFFF", weight=ft.FontWeight.W_500),
                                ft.Text(f"({ej['series']}x{ej['repeticiones']})", size=13, color="#8B949E")
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            spacing=5
                        )
                    )
        else:
            exercises_column.controls.append(
                ft.Text("No hay rutina registrada.", size=14, color="#8B949E")
            )

    # Inicializar con el mes 0
    actualizar_rutina_hoy(0)

    # Slider interactivo de meses
    def on_slider_change(e):
        val = int(e.control.value)
        
        # 1. Actualizar título "Tu Transformación"
        lbl_transform_title.value = f"Mes {val} de {plan_months}"
        
        # 2. Calcular métricas dinámicas
        peso_actual = round(peso_inicial - (val * 0.8), 1)
        musculo_ganado = round(val * 0.4, 1)
        grasa_actual = round(grasa_inicial - (val * 0.6), 1)
        
        lbl_weight.value = f"{peso_actual} kg"
        lbl_plan_status.value = f"Mes {val} de {plan_months}"
        lbl_muscle.value = f"+{musculo_ganado} kg"
        lbl_fat.value = f"{grasa_actual}%"
        
        # 3. Simular cambios visuales en el avatar mediante escala
        # Perder grasa/ganar músculo estiliza al avatar (escalado visual reactivo)
        if val > 0:
            img_avatar.scale = 1.0 - (val * 0.02) # Se reduce ligeramente el ancho de grasa
        else:
            img_avatar.scale = 1.0
            
        # 4. Actualizar rutina mostrada en el panel inferior
        actualizar_rutina_hoy(val)
        page.update()

    slider_sim = ft.Slider(
        min=0,
        max=plan_months,
        divisions=plan_months,
        value=0,
        label="{value} Mes",
        active_color="#00F0FF",
        inactive_color="#161B22",
        on_change=on_slider_change
    )

    # Botones superiores de la barra
    btn_back = ft.IconButton(
        icon=ft.Icons.ARROW_BACK_IOS_NEW,
        icon_color="#00F0FF",
        icon_size=16,
        on_click=lambda _: page.go("/register")
    )
    
    btn_info = ft.IconButton(
        icon=ft.Icons.INFO_OUTLINE,
        icon_color="#00F0FF",
        icon_size=18,
        on_click=lambda _: page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Mueve el slider para ver tu cambio predictivo."))
        )
    )

    # Layout de la vista
    return ft.View(
        route="/simulation",
        bgcolor="#0D1117",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header
                        ft.Row(
                            controls=[
                                btn_back,
                                ft.Text("Mi Progreso", size=20, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                btn_info
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(color="#1F2937", height=10),
                        
                        # Control de Simulación
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Tu Transformación", size=12, color="#8B949E", weight=ft.FontWeight.BOLD),
                                    lbl_transform_title,
                                    slider_sim
                                ],
                                spacing=5
                            ),
                            padding=10,
                            bgcolor="#161B22",
                            border_radius=10,
                            border=ft.Border.all(1, "#1F2937")
                        ),
                        ft.Divider(height=10, color="transparent"),
                        
                        # Tarjeta Central del Avatar con Estadísticas Flotantes
                        ft.Container(
                            content=ft.Stack(
                                controls=[
                                    # Avatar en el centro
                                    ft.Container(
                                        content=img_avatar,
                                        alignment=ft.alignment.Alignment.CENTER,
                                        margin=ft.margin.only(top=20, bottom=20)
                                    ),
                                    # Flotante Superior Izquierda (Peso)
                                    ft.Container(card_weight, top=10, left=0),
                                    # Flotante Superior Derecha (Músculo)
                                    ft.Container(card_muscle, top=10, right=0),
                                    # Flotante Inferior Izquierda (Mes)
                                    ft.Container(card_plan, bottom=10, left=0),
                                    # Flotante Inferior Derecha (Grasa)
                                    ft.Container(card_fat, bottom=10, right=0),
                                ],
                                height=280
                            ),
                            padding=5,
                        ),
                        
                        # Panel de Control Inferior (Entrenamiento de Hoy)
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("ENTRENAMIENTO DE HOY", size=12, color="#8B949E", weight=ft.FontWeight.BOLD),
                                    ft.Divider(color="#1F2937", height=5),
                                    exercises_column,
                                    ft.Divider(height=10, color="transparent"),
                                    
                                    # Botón Iniciar Rutina
                                    ft.Container(
                                        content=ft.Text("Iniciar Rutina", color="#000000", weight=ft.FontWeight.BOLD, size=16),
                                        alignment=ft.alignment.Alignment.CENTER,
                                        bgcolor="#00FF66",
                                        height=48,
                                        border_radius=10,
                                        on_click=lambda _: on_start_workout(plan),
                                    )
                                ],
                                spacing=8
                            ),
                            padding=15,
                            bgcolor="#161B22",
                            border_radius=12,
                            border=ft.Border.all(1, "#1F2937")
                        )
                    ],
                    spacing=15
                ),
                width=360,
                padding=15,
                bgcolor="#0D1117"
            )
        ]
    )
