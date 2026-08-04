import flet as ft
import time
import sys
import os

# Configuración de rutas de importación para robustez local
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Intentar importar api_client de manera flexible
try:
    import api_client
except ImportError:
    try:
        from frontend import api_client
    except ImportError:
        api_client = None

# --- VISTA 1: REGISTRO ---
def vista_registro(page: ft.Page, state: dict, navegar_a):
    txt_nombre = ft.TextField(
        label="Nombre Completo",
        value=state["nombre"],
        border_color="#1F2937",
        focused_border_color="#00FF66",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF", weight=ft.FontWeight.W_500),
        cursor_color="#00FF66",
        bgcolor="#161B22",
        border_radius=10,
        height=50,
    )
    
    txt_peso = ft.TextField(
        label="Peso (kg)",
        value=str(state["peso"]) if state["peso"] > 0 else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color="#1F2937",
        focused_border_color="#00FF66",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF", weight=ft.FontWeight.W_500),
        cursor_color="#00FF66",
        bgcolor="#161B22",
        border_radius=10,
        height=50,
        expand=True
    )
    
    txt_altura = ft.TextField(
        label="Altura (cm)",
        value=str(state["altura"]) if state["altura"] > 0 else "",
        keyboard_type=ft.KeyboardType.NUMBER,
        border_color="#1F2937",
        focused_border_color="#00FF66",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF", weight=ft.FontWeight.W_500),
        cursor_color="#00FF66",
        bgcolor="#161B22",
        border_radius=10,
        height=50,
        expand=True
    )
    
    dd_deporte = ft.Dropdown(
        label="Deporte de Entrenamiento",
        options=[
            ft.dropdown.Option("Fitness / Gimnasio"),
            ft.dropdown.Option("Running"),
            ft.dropdown.Option("Crossfit"),
            ft.dropdown.Option("Calistenia")
        ],
        value=state["deporte"],
        border_color="#1F2937",
        focused_border_color="#00FF66",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF", weight=ft.FontWeight.W_500),
        bgcolor="#161B22",
        border_radius=10,
        height=50,
    )

    lbl_error = ft.Text(value="", color="#FF3333", size=13, weight=ft.FontWeight.BOLD)

    # Preview y captura de foto
    img_preview = ft.Image(
        src=state.get("foto_url", "https://api.dicebear.com/7.x/pixel-art/svg?seed=roky&mood[]=happy"),
        width=100,
        height=100,
        fit="cover",
        border_radius=50,
        visible=state.get("foto_capturada", False)
    )
    
    icon_preview = ft.Container(
        content=ft.Icon(ft.Icons.CAMERA_ALT, size=36, color="#8B949E"),
        width=100,
        height=100,
        border_radius=50,
        bgcolor="#161B22",
        alignment=ft.alignment.Alignment.CENTER,
        border=ft.Border.all(1, "#1F2937"),
        visible=not state.get("foto_capturada", False)
    )

    file_picker = ft.FilePicker()
    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files:
            state["foto_capturada"] = True
            state["foto_url"] = e.files[0].path
            img_preview.src = e.files[0].path
            img_preview.visible = True
            icon_preview.visible = False
            btn_photo.content = ft.Text("¡Foto Cargada!", color="#00FF66", weight=ft.FontWeight.BOLD)
            btn_photo.icon = ft.Icons.CHECK_CIRCLE
            btn_photo.icon_color = "#00FF66"
            page.update()
            
    file_picker.on_result = on_file_selected
    page.overlay.append(file_picker)

    def capturar_foto(e):
        # Simula captura o abre selector de archivos
        state["foto_capturada"] = True
        seed = txt_nombre.value.replace(" ", "") if txt_nombre.value else "roky"
        state["foto_url"] = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={seed}"
        img_preview.src = state["foto_url"]
        img_preview.visible = True
        icon_preview.visible = False
        btn_photo.content = ft.Text("¡Foto Capturada!", color="#00FF66", weight=ft.FontWeight.BOLD)
        btn_photo.icon = ft.Icons.CHECK_CIRCLE
        btn_photo.icon_color = "#00FF66"
        page.update()

    btn_photo = ft.ElevatedButton(
        content=ft.Text("Capturar Foto Frontal", color="#FFFFFF"),
        icon=ft.Icons.CAMERA_ALT,
        icon_color="#00F0FF",
        style=ft.ButtonStyle(
            bgcolor="#161B22",
            side=ft.BorderSide(1, "#1F2937"),
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=capturar_foto
    )

    def on_registrar(e):
        lbl_error.value = ""
        if not txt_nombre.value:
            lbl_error.value = "Por favor ingresa tu nombre."
            page.update()
            return
        
        try:
            peso = float(txt_peso.value)
            altura = float(txt_altura.value)
            if peso <= 0 or altura <= 0:
                lbl_error.value = "Peso y altura deben ser mayores a 0."
                page.update()
                return
        except ValueError:
            lbl_error.value = "Peso y altura deben ser números."
            page.update()
            return
            
        # Guardar datos en el estado
        state["nombre"] = txt_nombre.value
        state["peso"] = peso
        state["altura"] = altura
        state["deporte"] = dd_deporte.value
        state["avatar_seed"] = txt_nombre.value.replace(" ", "") or "roky"
        
        # Conectar con el backend en segundo plano si está disponible
        if api_client:
            try:
                api_client.registrar_usuario(
                    name=state["nombre"],
                    email="roky_user@gmail.com",
                    weight=state["peso"],
                    height=int(state["altura"]),
                    sport=state["deporte"],
                    plan_months=state["plan_meses"]
                )
            except Exception as ex:
                print(f"Error api_client: {ex}")
                
        navegar_a("plan")

    btn_registrar = ft.Container(
        content=ft.Text("Registrar", color="#000000", weight=ft.FontWeight.BOLD, size=16),
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor="#00FF66",
        height=50,
        border_radius=10,
        on_click=on_registrar,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#00FF66",
            offset=ft.Offset(0, 2)
        )
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("ROKY CYBER", size=32, weight=ft.FontWeight.BOLD, color="#00FF66", text_align=ft.TextAlign.CENTER),
                ft.Text("Registro de Entrenamiento", size=14, color="#8B949E", text_align=ft.TextAlign.CENTER),
                ft.Divider(height=10, color="transparent"),
                
                # Preview y Captura
                ft.Row(
                    controls=[
                        ft.Stack([icon_preview, img_preview]),
                        ft.Column([
                            btn_photo,
                            ft.Text("Sube o simula tu foto", size=11, color="#8B949E")
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ),
                ft.Divider(height=10, color="transparent"),
                
                txt_nombre,
                ft.Row(controls=[txt_peso, txt_altura], spacing=10),
                dd_deporte,
                lbl_error,
                ft.Divider(height=10, color="transparent"),
                btn_registrar
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=10
    )


# --- VISTA 2: CARGA Y SELECCIÓN DE PLAN ---
def vista_plan(page: ft.Page, state: dict, navegar_a):
    # Si aún no se ha completado la generación del avatar, mostramos el loading spinner
    if not state.get("avatar_generado", False):
        lbl_status = ft.Text("Escaneando facciones...", color="#8B949E", size=14, text_align=ft.TextAlign.CENTER)
        bar_loading = ft.ProgressBar(color="#00F0FF", width=250)
        
        def simular_creacion_avatar():
            pasos = [
                "Procesando foto de perfil...",
                "Modelando estructura muscular...",
                "Aplicando estilo de dibujo Cómic 2D...",
                "¡Avatar ROKY Creado con Éxito!"
            ]
            for paso in pasos:
                lbl_status.value = paso
                try:
                    page.update()
                except Exception:
                    return
                time.sleep(0.8)
            
            state["avatar_generado"] = True
            try:
                navegar_a("plan")
            except Exception:
                pass

        page.run_task(simular_creacion_avatar)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("IA GENERATIVA ROKY", size=24, weight=ft.FontWeight.BOLD, color="#00F0FF", text_align=ft.TextAlign.CENTER),
                    ft.Text("Modelando avatar en tiempo real", size=13, color="#8B949E", text_align=ft.TextAlign.CENTER),
                    ft.Divider(height=30, color="transparent"),
                    ft.Container(
                        content=ft.ProgressRing(color="#00FF66", width=60, height=60),
                        alignment=ft.alignment.Alignment.CENTER
                    ),
                    ft.Divider(height=20, color="transparent"),
                    lbl_status,
                    bar_loading
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            height=550,
            alignment=ft.alignment.Alignment.CENTER
        )

    # Una vez cargado, mostramos el avatar y las tarjetas de plan
    avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={state['avatar_seed']}&mood[]=happy"
    
    avatar_display = ft.Container(
        content=ft.Image(src=avatar_url, width=110, height=110, fit="contain"),
        width=120,
        height=120,
        border_radius=60,
        bgcolor="#0D1117",
        border=ft.Border.all(2, "#00FF66"),
        alignment=ft.alignment.Alignment.CENTER
    )
    
    cards_container = ft.Column(spacing=10)
    
    def on_select_plan(months):
        state["plan_meses"] = months
        rebuild_cards()
        page.update()
        
    def rebuild_cards():
        cards_container.controls.clear()
        
        plans_info = [
            {"months": 3, "title": "Plan Inicial - 3 Meses", "price": "$19.99/mes", "desc": "Acondicionamiento Físico Básico", "color": "#00F0FF"},
            {"months": 6, "title": "Plan Guerrero - 6 Meses", "price": "$14.99/mes", "desc": "Hipertrofia & Pérdida de Grasa", "color": "#00FF66"},
            {"months": 9, "title": "Plan Élite - 9 Meses", "price": "$9.99/mes", "desc": "Recomposición Física Total", "color": "#FF007F"}
        ]
        
        current_sel = state.get("plan_meses", 3)
        
        for p in plans_info:
            is_selected = p["months"] == current_sel
            m = p["months"]
            
            badge = ft.Container(
                content=ft.Text("POPULAR", color="#000000", size=9, weight=ft.FontWeight.BOLD),
                bgcolor="#00FF66",
                padding=ft.padding.only(left=6, right=6, top=1, bottom=1),
                border_radius=4,
                visible=(m == 6)
            )
            
            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Row([
                                    ft.Text(p["title"], size=14, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    badge
                                ], spacing=5),
                                ft.Text(p["desc"], size=11, color="#8B949E"),
                                ft.Text(p["price"], size=13, weight=ft.FontWeight.BOLD, color=p["color"])
                            ],
                            spacing=3,
                            expand=True
                        ),
                        ft.Icon(
                            ft.Icons.RADIO_BUTTON_CHECKED if is_selected else ft.Icons.RADIO_BUTTON_UNCHECKED,
                            color=p["color"] if is_selected else "#1F2937"
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                padding=12,
                border_radius=10,
                bgcolor="#161B22",
                border=ft.Border.all(2, p["color"] if is_selected else "#1F2937"),
                on_click=lambda _, months=m: on_select_plan(months)
            )
            cards_container.controls.append(card)
            
    rebuild_cards()

    btn_continuar = ft.Container(
        content=ft.Text("Continuar", color="#000000", weight=ft.FontWeight.BOLD, size=16),
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor="#00FF66",
        height=50,
        border_radius=10,
        on_click=lambda _: navegar_a("simulacion"),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#00FF66",
            offset=ft.Offset(0, 2)
        )
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("¡AVATAR CREADO!", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
                ft.Text("Estilo Cómic 2D Cyber listo para entrenar", size=12, color="#8B949E", text_align=ft.TextAlign.CENTER),
                ft.Divider(height=10, color="transparent"),
                
                avatar_display,
                ft.Divider(height=10, color="transparent"),
                
                ft.Text("Elige la duración de tu plan:", size=13, weight=ft.FontWeight.BOLD, color="#00FF66"),
                cards_container,
                ft.Divider(height=10, color="transparent"),
                btn_continuar
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=5
    )


# --- VISTA 3: SIMULACIÓN DE PROGRESO ---
def vista_simulacion(page: ft.Page, state: dict, navegar_a):
    peso_inicial = state["peso"]
    plan_meses = state["plan_meses"]
    grasa_inicial = 22.0 if state["deporte"] == "Fitness / Gimnasio" else 18.0
    
    avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={state['avatar_seed']}&mood[]=happy"
    img_avatar = ft.Image(
        src=avatar_url,
        width=130,
        height=130,
        fit="contain",
        animate_scale=ft.Animation(300, "easeOut")
    )
    
    # Controles de Estadísticas
    lbl_weight = ft.Text(f"{peso_inicial} kg", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_muscle = ft.Text("+0.0 kg", size=16, weight=ft.FontWeight.BOLD, color="#00FF66")
    lbl_fat = ft.Text(f"{grasa_inicial}%", size=16, weight=ft.FontWeight.BOLD, color="#FF007F")
    lbl_focus = ft.Text("Acondicionamiento", size=15, weight=ft.FontWeight.BOLD, color="#00F0FF")
    
    def create_stat_box(title, control, icon, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(icon, size=14, color=color),
                        ft.Text(title, size=9, color="#8B949E", weight=ft.FontWeight.BOLD)
                    ], spacing=4),
                    control
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            bgcolor="#161B22",
            padding=8,
            border_radius=8,
            border=ft.Border.all(1, "#1F2937"),
            width=155,
            height=52
        )
        
    box_weight = create_stat_box("PESO ESTIMADO", lbl_weight, ft.Icons.MONITOR_WEIGHT, "#00F0FF")
    box_muscle = create_stat_box("MÚSCULO GANADO", lbl_muscle, ft.Icons.FITNESS_CENTER, "#00FF66")
    box_fat = create_stat_box("GRASA CORPORAL", lbl_fat, ft.Icons.PERCENT, "#FF007F")
    box_focus = create_stat_box("ENFOQUE MENSUAL", lbl_focus, ft.Icons.TRACK_CHANGES, "#00F0FF")

    exercises_container = ft.Column(spacing=6)
    
    def get_rutina_mes(mes):
        if mes == 0:
            return "Rutina de Entrada", [
                {"nombre": "Movilidad Articular Articulaciones", "series": 3, "reps": 10},
                {"nombre": "Caminata Moderada", "series": 1, "reps": 15}
            ]
        elif mes <= 3:
            return "Fase 1: Hipertrofia & Core", [
                {"nombre": "Sentadillas Cyber", "series": 4, "reps": 15},
                {"nombre": "Flexiones Neón", "series": 3, "reps": 12},
                {"nombre": "Plancha Cuántica", "series": 3, "reps": 45}
            ]
        elif mes <= 6:
            return "Fase 2: Fuerza y Quema", [
                {"nombre": "Sentadillas con Salto", "series": 4, "reps": 12},
                {"nombre": "Flexiones Diamante Cyber", "series": 4, "reps": 10},
                {"nombre": "Plancha Dinámica", "series": 3, "reps": 60}
            ]
        else:
            return "Fase 3: Tonificación Máxima", [
                {"nombre": "Pistol Squats (Asistidas)", "series": 4, "reps": 8},
                {"nombre": "Flexiones Explosivas", "series": 4, "reps": 10},
                {"nombre": "Plancha Spiderman", "series": 3, "reps": 60}
            ]

    def actualizar_simulacion(mes):
        peso_estimado = round(peso_inicial - (mes * 0.8), 1)
        grasa_estimada = round(max(5.0, grasa_inicial - (mes * 0.6)), 1)
        musculo_ganado = round(mes * 0.4, 1)
        
        lbl_weight.value = f"{peso_estimado} kg"
        lbl_fat.value = f"{grasa_estimada}%"
        lbl_muscle.value = f"+{musculo_ganado} kg"
        
        state["peso_estimado"] = peso_estimado
        
        fase_title, ejercicios = get_rutina_mes(mes)
        lbl_focus.value = fase_title
        
        # Simula tonificación reduciendo el ancho del avatar levemente
        img_avatar.scale = 1.0 - (mes * 0.015)
        
        exercises_container.controls.clear()
        exercises_container.controls.append(
            ft.Text(f"Plan de Trabajo - Mes {mes}", size=12, color="#00FF66", weight=ft.FontWeight.BOLD)
        )
        for ej in ejercicios:
            exercises_container.controls.append(
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=14, color="#00F0FF"),
                        ft.Text(f"{ej['nombre']}", size=13, color="#FFFFFF", weight=ft.FontWeight.W_500),
                        ft.Text(f"({ej['series']}x{ej['reps']})", size=11, color="#8B949E")
                    ],
                    spacing=5
                )
            )
            
    actualizar_simulacion(0)

    def on_slider_change(e):
        actualizar_simulacion(int(e.control.value))
        page.update()

    slider = ft.Slider(
        min=0,
        max=plan_meses,
        divisions=plan_meses,
        value=0,
        label="Mes {value}",
        active_color="#00FF66",
        inactive_color="#161B22",
        on_change=on_slider_change
    )

    btn_empezar = ft.Container(
        content=ft.Text("Empezar Rutina", color="#000000", weight=ft.FontWeight.BOLD, size=16),
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor="#00FF66",
        height=50,
        border_radius=10,
        on_click=lambda _: navegar_a("entrenamiento"),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color="#00FF66",
            offset=ft.Offset(0, 2)
        )
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS_NEW,
                            icon_color="#00F0FF",
                            icon_size=16,
                            on_click=lambda _: navegar_a("plan")
                        ),
                        ft.Text("Tu Transformación", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        ft.IconButton(
                            icon=ft.Icons.INFO_OUTLINE,
                            icon_color="#00F0FF",
                            icon_size=18,
                            on_click=lambda _: page.show_snack_bar(
                                ft.SnackBar(content=ft.Text("Usa el slider para ver tu cambio predictivo."))
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="#1F2937", height=5),
                
                # Avatar central
                ft.Container(
                    content=img_avatar,
                    alignment=ft.alignment.Alignment.CENTER,
                    height=140
                ),
                
                # Bloque de estadísticas
                ft.Column(
                    controls=[
                        ft.Row([box_weight, box_muscle], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        ft.Row([box_fat, box_focus], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                    ],
                    spacing=10
                ),
                ft.Divider(height=5, color="transparent"),
                
                # Slider
                ft.Column([
                    ft.Text("Desliza para simular tu progreso físico", size=11, color="#8B949E", weight=ft.FontWeight.BOLD),
                    slider
                ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                
                # Rutina recomendada
                ft.Container(
                    content=exercises_container,
                    padding=12,
                    bgcolor="#161B22",
                    border_radius=10,
                    border=ft.Border.all(1, "#1F2937")
                ),
                ft.Divider(height=5, color="transparent"),
                btn_empezar
            ],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=5
    )


# --- VISTA 4: ENTRENAMIENTO ACTIVO ---
def vista_entrenamiento(page: ft.Page, state: dict, navegar_a):
    if "ejercicios" not in state or not state["ejercicios"]:
        state["ejercicios"] = [
            {"nombre": "Sentadillas Cyber", "series": 4, "repeticiones": 15, "anim": "squats"},
            {"nombre": "Flexiones Neón", "series": 3, "repeticiones": 12, "anim": "pushups"},
            {"nombre": "Plancha Cuántica", "series": 3, "repeticiones": 45, "anim": "plank"}
        ]
        
    state["ejercicio_actual"] = state.get("ejercicio_actual", 0)
    state["serie_actual"] = state.get("serie_actual", 1)
    
    avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={state['avatar_seed']}&mood[]=happy"
    img_avatar = ft.Image(
        src=avatar_url,
        width=130,
        height=130,
        fit="contain",
        animate_offset=ft.Animation(300, "easeInOut"),
        animate_scale=ft.Animation(300, "easeInOut"),
    )
    
    lbl_ex_name = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_series_reps = ft.Text("", size=15, color="#00F0FF", weight=ft.FontWeight.W_500)
    lbl_timer = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color="#00FF66", visible=False)
    
    avatar_box = ft.Container(
        content=img_avatar,
        alignment=ft.alignment.Alignment.CENTER,
        height=180,
        border_radius=15,
        bgcolor="#161B22",
        border=ft.Border.all(1, "#1F2937")
    )
    
    def loop_animacion_avatar():
        state["is_animating"] = True
        scale_up = True
        while state.get("is_animating", False):
            if state["ejercicio_actual"] >= len(state["ejercicios"]):
                break
            ex = state["ejercicios"][state["ejercicio_actual"]]
            anim = ex["anim"]
            
            if anim == "pushups":
                img_avatar.scale = 0.85 if scale_up else 1.05
                img_avatar.offset = ft.transform.Offset(0, 0.05 if scale_up else 0)
            elif anim == "squats":
                img_avatar.offset = ft.transform.Offset(0, 0.15 if scale_up else -0.05)
                img_avatar.scale = 1.0
            else:  # plank
                img_avatar.offset = ft.transform.Offset(0.03 if scale_up else -0.03, 0)
                img_avatar.scale = 1.0
                
            scale_up = not scale_up
            try:
                page.update()
            except Exception:
                break
            time.sleep(0.4)

    page.run_task(loop_animacion_avatar)

    def ejecutar_timer_descanso():
        state["rest_time"] = 30
        state["is_resting"] = True
        lbl_timer.visible = True
        try:
            page.update()
        except Exception:
            return
            
        while state.get("is_resting", False) and state.get("rest_time", 0) > 0:
            lbl_timer.value = f"Descanso: {state['rest_time']}s"
            try:
                page.update()
            except Exception:
                break
            time.sleep(1)
            state["rest_time"] -= 1
            
        state["is_resting"] = False
        lbl_timer.visible = False
        actualizar_pantalla()

    def completar_entrenamiento():
        state["is_animating"] = False
        state["is_resting"] = False
        
        dialog = ft.AlertDialog(
            title=ft.Text("¡Entrenamiento Completado!", color="#00FF66", weight=ft.FontWeight.BOLD),
            content=ft.Text("Excelente trabajo hoy. ¡Tu avatar Roky está orgulloso de tu esfuerzo!", color="#FFFFFF"),
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
        state["ejercicio_actual"] = 0
        state["serie_actual"] = 1
        state["avatar_generado"] = False
        page.update()
        navegar_a("registro")

    def actualizar_pantalla():
        ex_idx = state["ejercicio_actual"]
        if ex_idx >= len(state["ejercicios"]):
            completar_entrenamiento()
            return
            
        ex = state["ejercicios"][ex_idx]
        lbl_ex_name.value = ex["nombre"]
        lbl_series_reps.value = f"Serie {state['serie_actual']} de {ex['series']} | {ex['repeticiones']} Reps"
        
        if state.get("is_resting", False):
            btn_accion.content = ft.Text("Omitir Descanso", color="#000000", weight=ft.FontWeight.BOLD)
            btn_accion.bgcolor = "#00F0FF"
            btn_accion.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color="#00F0FF", offset=ft.Offset(0, 2))
        else:
            btn_accion.content = ft.Text("Iniciar Serie", color="#000000", weight=ft.FontWeight.BOLD)
            btn_accion.bgcolor = "#00FF66"
            btn_accion.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color="#00FF66", offset=ft.Offset(0, 2))
            
        try:
            page.update()
        except Exception:
            pass

    def on_accion_click(e):
        if state.get("is_resting", False):
            state["is_resting"] = False
            return
            
        ex_idx = state["ejercicio_actual"]
        ex = state["ejercicios"][ex_idx]
        
        if state["serie_actual"] < ex["series"]:
            state["serie_actual"] += 1
            page.run_task(ejecutar_timer_descanso)
        else:
            state["ejercicio_actual"] += 1
            state["serie_actual"] = 1
            actualizar_pantalla()

    btn_accion = ft.Container(
        content=ft.Text("Iniciar Serie", color="#000000", weight=ft.FontWeight.BOLD, size=16),
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor="#00FF66",
        height=52,
        border_radius=10,
        on_click=on_accion_click,
        expand=True
    )
    
    btn_omitir = ft.IconButton(
        icon=ft.Icons.SKIP_NEXT_ROUNDED,
        icon_color="#FFFFFF",
        bgcolor="#161B22",
        icon_size=24,
        on_click=lambda _: skip_exercise()
    )
    
    def skip_exercise():
        state["is_resting"] = False
        state["ejercicio_actual"] += 1
        state["serie_actual"] = 1
        actualizar_pantalla()

    actualizar_pantalla()

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CLOSE_ROUNDED,
                            icon_color="#FF3333",
                            on_click=lambda _: navegar_a("simulacion")
                        ),
                        ft.Text("Entrenamiento Activo", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                        ft.Icon(ft.Icons.TIMER_OUTLINED, color="#00F0FF", size=20)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color="#1F2937", height=5),
                
                # Avatar
                avatar_box,
                ft.Divider(height=5, color="transparent"),
                
                # Datos Ejercicio
                ft.Container(
                    content=ft.Column(
                        controls=[
                            lbl_ex_name,
                            lbl_series_reps,
                            lbl_timer
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
                ft.Divider(height=10, color="transparent"),
                
                # Botones de Acción
                ft.Row(
                    controls=[
                        btn_accion,
                        btn_omitir
                    ],
                    spacing=10
                )
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=5
    )


# --- MÉTODO PRINCIPAL ---
def main(page: ft.Page):
    # Configuración de ventana y diseño del simulador de móvil
    page.title = "ROKY - Inteligencia Deportiva"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#080B10"  # Fondo exterior
    
    page.window.width = 410
    page.window.height = 790
    page.window.resizable = False
    
    # Fuentes personalizadas
    page.fonts = {
        "Outfit": "https://github.com/google/fonts/raw/main/ofl/outfit/Outfit%5Bwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Outfit")

    # Estado de la sesión del usuario
    state = {
        "current_view": "registro",
        "nombre": "",
        "peso": 0.0,
        "altura": 0.0,
        "deporte": "Fitness / Gimnasio",
        "foto_capturada": False,
        "foto_url": None,
        "plan_meses": 3,
        "avatar_seed": "roky",
        "avatar_generado": False,
        
        # Animaciones / Rest
        "is_animating": False,
        "is_resting": False,
        "ejercicio_actual": 0,
        "serie_actual": 1
    }

    # Contenedor dinámico principal
    main_container = ft.Container(expand=True)

    # Función del enrutador dinámico
    def navegar_a(vista_name):
        state["current_view"] = vista_name
        # Limpiar flags asíncronos para evitar fugas de memoria o hilos huérfanos
        state["is_animating"] = False
        state["is_resting"] = False
        
        if vista_name == "registro":
            main_container.content = vista_registro(page, state, navegar_a)
        elif vista_name == "plan":
            main_container.content = vista_plan(page, state, navegar_a)
        elif vista_name == "simulacion":
            main_container.content = vista_simulacion(page, state, navegar_a)
        elif vista_name == "entrenamiento":
            main_container.content = vista_entrenamiento(page, state, navegar_a)
        
        page.update()

    # Estructura del marco del móvil (estilo Cyberpunk Premium)
    mobile_frame = ft.Container(
        width=380,
        height=720,
        bgcolor="#0D1117",
        border_radius=30,
        border=ft.Border.all(2, "#1F2937"),
        padding=15,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="#000000",
            offset=ft.Offset(0, 5)
        ),
        content=main_container
    )

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.add(mobile_frame)

    # Iniciar flujo
    navegar_a("registro")

if __name__ == "__main__":
    ft.app(target=main, port=8501, host="0.0.0.0", view=ft.AppView.WEB_BROWSER)
