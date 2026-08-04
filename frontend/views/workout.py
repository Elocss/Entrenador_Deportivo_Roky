import flet as ft
import time
from typing import Dict

def get_workout_view(page: ft.Page, plan_data, on_workout_finished):
    # Cargar ejercicios de la rutina activa (por defecto el primer bloque, primer día)
    bloques = plan_data.get("bloques_mensuales", [])
    ejercicios = []
    grupo_muscular = "Entrenamiento"
    
    if bloques and bloques[0].get("rutina_semanal", []):
        rutina_hoy = bloques[0]["rutina_semanal"][0] # Lunes
        ejercicios = rutina_hoy.get("ejercicios", [])
        grupo_muscular = rutina_hoy.get("grupo_muscular", "Tren Superior")

    # Si por alguna razón no hay ejercicios, agregar placeholders
    if not ejercicios:
        ejercicios = [
            {"nombre": "Flexiones de pecho", "series": 4, "repeticiones": 12, "id_animacion_avatar": "pushups"},
            {"nombre": "Sentadillas libres", "series": 4, "repeticiones": 15, "id_animacion_avatar": "squats"}
        ]

    # Variables de estado del entrenamiento
    current_exercise_idx = 0
    current_serie = 1
    is_animating = False
    is_resting = False
    rest_seconds_left = 30
    
    # UI Elements
    lbl_ex_name = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color="#FFFFFF", text_align=ft.TextAlign.CENTER)
    lbl_ex_details = ft.Text("", size=14, color="#8B949E", text_align=ft.TextAlign.CENTER)
    lbl_series_reps = ft.Text("", size=18, color="#00F0FF", weight=ft.FontWeight.W_500)
    
    # Imagen de Roky con animación
    img_roky = ft.Image(
        src="https://api.dicebear.com/7.x/pixel-art/svg?seed=roky&mood[]=happy",
        width=150,
        height=150,
        fit="contain",
        animate_offset=ft.Animation(300, "easeInOut"),
        animate_scale=ft.Animation(300, "easeInOut"),
    )
    
    # Animación de Bucle para Roky en segundo plano
    def loop_animacion_roky():
        nonlocal is_animating
        is_animating = True
        scale_state = True
        
        while is_animating:
            # Obtener el ejercicio actual
            if current_exercise_idx >= len(ejercicios):
                break
            ex = ejercicios[current_exercise_idx]
            anim_type = ex.get("id_animacion_avatar", "pushups")
            
            # Aplicar animaciones basadas en el tipo de ejercicio
            if anim_type == "pushups":
                # Escalar para simular subir/bajar flexión
                img_roky.scale = 0.85 if scale_state else 1.05
                img_roky.offset = ft.transform.Offset(0, 0.05 if scale_state else 0)
            elif anim_type == "squats":
                # Desplazamiento vertical para sentadillas
                img_roky.offset = ft.transform.Offset(0, 0.2 if scale_state else -0.1)
                img_roky.scale = 1.0
            else: # Saltos u otros
                # Salto (escala + desplazamiento)
                img_roky.offset = ft.transform.Offset(0, -0.15 if scale_state else 0.05)
                img_roky.scale = 0.95 if scale_state else 1.05
                
            scale_state = not scale_state
            try:
                page.update()
            except Exception:
                # Evitar errores si cambiamos de pantalla abruptamente
                break
            time.sleep(0.4) # Intervalo de la animación

    # Control de descanso
    lbl_timer = ft.Text("", size=36, weight=ft.FontWeight.BOLD, color="#00FF66")
    timer_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("TIEMPO DE DESCANSO", size=11, color="#8B949E", weight=ft.FontWeight.BOLD),
                lbl_timer
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        visible=False,
        bgcolor="#161B22",
        padding=10,
        border_radius=8,
        border=ft.Border.all(1, "#00FF66"),
        alignment=ft.alignment.Alignment.CENTER
    )

    def actualizar_pantalla():
        nonlocal current_exercise_idx, current_serie, is_resting
        if current_exercise_idx >= len(ejercicios):
            completar_entrenamiento()
            return
            
        ex = ejercicios[current_exercise_idx]
        lbl_ex_name.value = ex["nombre"]
        lbl_ex_details.value = f"Ejercicio {current_exercise_idx + 1} de {len(ejercicios)} • {grupo_muscular}"
        lbl_series_reps.value = f"Serie {current_serie} de {ex['series']}  |  {ex['repeticiones']} Repeticiones"
        
        # Ocultar o mostrar timer
        timer_container.visible = is_resting
        btn_start_series.content = "Terminar Descanso" if is_resting else "Iniciar Serie"
        btn_start_series.bgcolor = "#00F0FF" if is_resting else "#161B22"
        btn_start_series.style.color = "#000000" if is_resting else "#FFFFFF"
        
        page.update()

    def completar_entrenamiento():
        nonlocal is_animating
        is_animating = False
        
        # Mostrar diálogo de felicitación
        dialog = ft.AlertDialog(
            title=ft.Text("¡Entrenamiento Completado!", color="#00FF66", weight=ft.FontWeight.BOLD),
            content=ft.Text("Excelente trabajo hoy. ¡Roky está orgulloso de tu progreso!", color="#FFFFFF"),
            actions=[
                ft.TextButton("Volver al Inicio", on_click=lambda e: cerrar_dialogo_y_volver(dialog))
            ],
            bgcolor="#161B22"
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def cerrar_dialogo_y_volver(dialog):
        dialog.open = False
        page.update()
        on_workout_finished()

    # Manejo de temporizador de descanso
    def ejecutar_timer_descanso():
        nonlocal rest_seconds_left, is_resting
        rest_seconds_left = 30
        while rest_seconds_left > 0 and is_resting:
            lbl_timer.value = f"00:{rest_seconds_left:02d}"
            try:
                page.update()
            except Exception:
                break
            time.sleep(1)
            rest_seconds_left -= 1
            
        # Al terminar descanso
        if is_resting:
            is_resting = False
            actualizar_pantalla()

    # Eventos de botones
    def on_start_series_click(e):
        nonlocal is_resting, current_serie, current_exercise_idx
        ex = ejercicios[current_exercise_idx]
        
        if is_resting:
            # Terminar descanso antes
            is_resting = False
            actualizar_pantalla()
        else:
            # Serie completada -> Iniciar descanso
            if current_serie < ex["series"]:
                current_serie += 1
                is_resting = True
                actualizar_pantalla()
                page.run_task(ejecutar_timer_descanso)
            else:
                # Si completó las series de este ejercicio, avanzar directamente
                on_next_exercise_click(None)

    def on_next_exercise_click(e):
        nonlocal current_exercise_idx, current_serie, is_resting
        is_resting = False
        current_exercise_idx += 1
        current_serie = 1
        actualizar_pantalla()

    # Asignar clicks
    btn_start_series = ft.ElevatedButton(
        content="Iniciar Serie",
        icon=ft.Icons.PLAY_ARROW_ROUNDED,
        style=ft.ButtonStyle(
            color="#FFFFFF",
            bgcolor="#161B22",
            side=ft.BorderSide(1, "#00F0FF"),
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=170,
        height=50,
        on_click=on_start_series_click
    )
    
    btn_next = ft.ElevatedButton(
        content="Siguiente Ejercicio",
        icon=ft.Icons.SKIP_NEXT_ROUNDED,
        style=ft.ButtonStyle(
            color="#000000",
            bgcolor="#00FF66",
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=170,
        height=50,
        on_click=on_next_exercise_click
    )

    # Iniciar actualizaciones y animaciones
    actualizar_pantalla()
    page.run_task(loop_animacion_roky)

    return ft.View(
        route="/workout",
        bgcolor="#0D1117",
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Header
                        ft.Row(
                            controls=[
                                ft.IconButton(icon=ft.Icons.CLOSE, icon_color="#FF3333", on_click=lambda _: on_workout_finished()),
                                ft.Text("Entrenamiento Activo", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                ft.Icon(ft.Icons.TIMER, color="#00F0FF", size=20)
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Divider(color="#1F2937", height=10),
                        
                        # Zona Superior: Animación de Roky
                        ft.Container(
                            content=img_roky,
                            alignment=ft.alignment.Alignment.CENTER,
                            height=220,
                            border_radius=15,
                            bgcolor="#161B22",
                            border=ft.Border.all(1, "#1F2937")
                        ),
                        ft.Divider(height=10, color="transparent"),
                        
                        # Zona Central: Detalles del Ejercicio
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    lbl_ex_name,
                                    lbl_ex_details,
                                    ft.Divider(color="#1F2937", height=15),
                                    lbl_series_reps,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8
                            ),
                            padding=15,
                            bgcolor="#161B22",
                            border_radius=12,
                            border=ft.Border.all(1, "#1F2937"),
                            alignment=ft.alignment.Alignment.CENTER
                        ),
                        
                        # Temporizador de Descanso
                        timer_container,
                         
                         ft.Divider(height=10, color="transparent"),
                        
                        # Zona Inferior: Botones grandes
                        ft.Row(
                            controls=[
                                btn_start_series,
                                btn_next
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=10
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
