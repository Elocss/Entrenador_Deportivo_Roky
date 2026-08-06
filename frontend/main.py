import base64
import flet as ft
import time
import sys
import os

def imagen_a_base64(ruta_archivo):
    with open(ruta_archivo, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Configuración de rutas de importación para robustez local
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def log_debug(message):
    try:
        log_path = os.path.join(current_dir, "frontend_debug.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except Exception as e:
        print(f"Error logging: {e}")

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
        src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
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

    def cuando_seleccione_archivo(e: ft.FilePickerResultEvent):
        try:
            if e.files and len(e.files) > 0:
                file_info = e.files[0]
                log_debug(f"[FilePicker] Archivo seleccionado por usuario: name={file_info.name}, path={file_info.path}")
                
                # Obtener bytes
                foto_bytes = file_info.bytes
                if not foto_bytes and file_info.path:
                    import os
                    if os.path.exists(file_info.path):
                        with open(file_info.path, "rb") as f:
                            foto_bytes = f.read()
                            
                if foto_bytes:
                    # 1. BUG DE CAPTURA/SUBIR: Escribir físicamente a 'foto_usuario.jpg' para homologar con el canal de la cámara
                    with open('foto_usuario.jpg', 'wb') as f:
                        f.write(foto_bytes)
                    log_debug("[FilePicker] Copia guardada físicamente en foto_usuario.jpg")
                    
                    state["foto_capturada"] = True
                    state["foto_name"] = "foto_usuario.jpg"
                    state["foto_bytes"] = foto_bytes
                    state["foto_url"] = "foto_usuario.jpg"
                    
                    encoded_string = imagen_a_base64("foto_usuario.jpg")
                    state["foto_base64"] = encoded_string
                    img_preview.src = f"data:image/jpeg;base64,{encoded_string}"
                    
                    # Persistencia en el estado global
                    if page.data is None:
                        page.data = {}
                    page.data["foto_bytes"] = foto_bytes
                    page.data["foto_name"] = "foto_usuario.jpg"
                    page.data["foto_url"] = "foto_usuario.jpg"
                    page.data["foto_base64"] = encoded_string
                    
                    img_preview.visible = True
                    icon_preview.visible = False
                    
                    # Actualizar estilo de botón upload
                    btn_upload.content = ft.Text("¡Foto Cargada!", color="#00FF66", weight=ft.FontWeight.BOLD)
                    btn_upload.icon = ft.Icons.CHECK_CIRCLE
                    btn_upload.icon_color = "#00FF66"
                    
                    # Restaurar botón de cámara
                    btn_photo.content = ft.Text("Capturar Foto Frontal", color="#FFFFFF")
                    btn_photo.icon = ft.Icons.CAMERA_ALT
                    btn_photo.icon_color = "#00F0FF"
                    
                    page.update()
                else:
                    raise Exception("No se pudieron extraer los bytes de la imagen seleccionada.")
            else:
                log_debug("[FilePicker] Cancelado por el usuario.")
        except Exception as file_err:
            log_debug(f"[FilePicker Error] {file_err}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al subir archivo: {file_err}", color="#FFFFFF"),
                bgcolor="#FF3333"
            )
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = cuando_seleccione_archivo
    
    # Limpiar previos pickers en overlay para evitar duplicados
    for ctrl in page.overlay[:]:
        if isinstance(ctrl, ft.FilePicker):
            page.overlay.remove(ctrl)
            
    page.overlay.append(file_picker)

    async def capturar_foto(e):
        import cv2
        import threading
        import base64
        import time

        # Si la cámara ya está corriendo, el botón actúa como "Capturar Ahora"
        if state.get("camera_running", False):
            log_debug("[Camera] Clic en 'Capturar Ahora'. Deteniendo transmisión...")
            
            # 1. Cambiar la bandera para detener el bucle del hilo de inmediato
            state["camera_running"] = False
            
            # 2. Darle un pequeño margen de milisegundos al hilo para salir de su ciclo
            time.sleep(0.1)
            
            # 3. Obtener el objeto capture y liberarlo físicamente
            cap = state.get("active_cap")
            if cap is not None:
                try:
                    cap.release()
                    log_debug("[Camera] Cámara liberada físicamente desde el botón.")
                except Exception as ex:
                    log_debug(f"[Camera] Error al liberar cap: {ex}")
            
            # 4. Obtener y guardar el último frame físicamente
            last_frame_numpy = state.get("last_frame_numpy")
            if last_frame_numpy is not None:
                cv2.imwrite("foto_usuario.jpg", last_frame_numpy)
                log_debug("[Camera] Último frame guardado físicamente en foto_usuario.jpg")
                
                try:
                    # 5. Convertir a Base64 y fijar la propiedad de forma definitiva
                    base64_data = imagen_a_base64("foto_usuario.jpg")
                    state["foto_capturada"] = True
                    state["foto_name"] = "foto_usuario.jpg"
                    with open("foto_usuario.jpg", "rb") as f:
                        state["foto_bytes"] = f.read()
                    state["foto_url"] = "foto_usuario.jpg"
                    state["foto_base64"] = base64_data
                    
                    img_preview.src = f"data:image/jpeg;base64,{base64_data}"
                    
                    # Persistencia en el estado global
                    if page.data is None:
                        page.data = {}
                    page.data["foto_bytes"] = state["foto_bytes"]
                    page.data["foto_name"] = "foto_usuario.jpg"
                    page.data["foto_url"] = "foto_usuario.jpg"
                    page.data["foto_base64"] = base64_data
                    
                    # Estilo de éxito definitivo
                    btn_photo.content = ft.Text("¡Foto Cargada!", color="#00FF66", weight=ft.FontWeight.BOLD)
                    btn_photo.icon = ft.Icons.CHECK_CIRCLE
                    btn_photo.icon_color = "#00FF66"
                except Exception as err:
                    log_debug(f"[Camera] Error al procesar base64: {err}")
            else:
                # Si no hay frame, restaurar estado original
                btn_photo.content = ft.Text("Capturar Foto Frontal", color="#FFFFFF")
                btn_photo.icon = ft.Icons.CAMERA_ALT
                btn_photo.icon_color = "#00F0FF"
            
            # 6. Forzar redibujado de la interfaz
            page.update()
            return

        # Si no está corriendo, iniciamos la cámara en un hilo secundario
        log_debug("[Camera] Iniciando transmisión en vivo...")
        state["camera_running"] = True
        
        # Cambiamos el texto del botón a "Capturar Ahora" y modificamos su color para denotar acción
        btn_photo.content = ft.Text("Capturar Ahora", color="#FFFFFF", weight=ft.FontWeight.BOLD)
        btn_photo.icon = ft.Icons.CAMERA
        btn_photo.icon_color = "#FF007F"  # Rosa/Fucsia Cyberpunk
        page.update()

        def stream_camera():
            cap = None
            cam_index_worked = -1
            
            # 1. BUCLE DE PRUEBA DE ÍNDICES [0, 1, 2]
            for idx in [0, 1, 2]:
                try:
                    log_debug(f"[Camera Thread] Probando índice {idx}...")
                    cap = cv2.VideoCapture(idx)
                    if cap is not None and cap.isOpened():
                        cam_index_worked = idx
                        break
                    else:
                        if cap is not None:
                            cap.release()
                        cap = None
                except Exception as ex:
                    log_debug(f"[Camera Thread] Fallo en índice {idx}: {ex}")
                    if cap is not None:
                        cap.release()
                    cap = None
            
            if cap is None or not cap.isOpened():
                log_debug("[Camera Thread] No se pudo abrir ninguna cámara activa.")
                state["camera_running"] = False
                
                # Restaurar botón
                btn_photo.content = ft.Text("Capturar Foto Frontal", color="#FFFFFF")
                btn_photo.icon = ft.Icons.CAMERA_ALT
                btn_photo.icon_color = "#00F0FF"
                
                # 2. MANEJO DE ERRORES VISUAL: SnackBar
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error: No se detectó ninguna cámara activa. Verifica los permisos de tu terminal.", color="#FFFFFF"),
                    bgcolor="#FF3333",
                    duration=4000
                )
                page.snack_bar.open = True
                page.update()
                return

            log_debug(f"[Camera Thread] Transmisión en vivo iniciada (índice {cam_index_worked}).")
            
            # Guardamos cap en el estado para poder liberarlo desde el hilo principal
            state["active_cap"] = cap
            
            # Cambiar visibilidad de preview
            img_preview.visible = True
            icon_preview.visible = False
            page.update()

            try:
                # Bucle de lectura continua condicionado
                while cap.isOpened() and state.get("camera_running", False):
                    ret, frame = cap.read()
                    if not ret:
                        log_debug("[Camera Thread] Error de lectura del frame.")
                        break
                    
                    # Voltear frame para efecto espejo
                    frame_mirror = cv2.flip(frame, 1)
                    
                    # Codificar fotograma a JPG
                    _, buffer = cv2.imencode('.jpg', frame_mirror)
                    frame_bytes = buffer.tobytes()
                    state["last_frame"] = frame_bytes
                    state["last_frame_numpy"] = frame_mirror
                    
                    # Convertir a base64 y transmitir en vivo a Flet
                    encoded_string = base64.b64encode(frame_bytes).decode('utf-8')
                    img_preview.src = f"data:image/jpeg;base64,{encoded_string}"
                    page.update()
                    
                    # Control de refresco (~30 fps) para evitar uso excesivo de CPU
                    time.sleep(0.03)
                    
            except Exception as loop_err:
                log_debug(f"[Camera Thread] Excepción en bucle de streaming: {loop_err}")
            finally:
                # Asegurar liberación física de la cámara
                try:
                    if cap is not None and cap.isOpened():
                        cap.release()
                except Exception:
                    pass
                log_debug("[Camera Thread] Hilo de cámara finalizado.")

        # Iniciar transmisión en hilo secundario (threading)
        threading.Thread(target=stream_camera, daemon=True).start()

    async def subir_foto_archivo(e):
        log_debug("subir_foto_archivo() disparado por clic del botón.")
        # Detener streaming de cámara en caso de que esté activo
        if state.get("camera_running", False):
            state["camera_running"] = False
            import time
            time.sleep(0.1)
            cap = state.get("active_cap")
            if cap is not None:
                try:
                    cap.release()
                    log_debug("[FilePicker] Cámara liberada físicamente al seleccionar archivo.")
                except Exception:
                    pass
        
        try:
            await file_picker.pick_files(
                allow_multiple=False,
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        except Exception as file_err:
            log_debug(f"[FilePicker Launch Error] {file_err}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al abrir selector: {file_err}", color="#FFFFFF"),
                bgcolor="#FF3333"
            )
            page.snack_bar.open = True
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

    btn_upload = ft.ElevatedButton(
        content=ft.Text("Subir Foto desde Archivo", color="#FFFFFF"),
        icon=ft.Icons.UPLOAD_FILE,
        icon_color="#00F0FF",
        style=ft.ButtonStyle(
            bgcolor="#161B22",
            side=ft.BorderSide(1, "#1F2937"),
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        on_click=subir_foto_archivo
    )

    def enviar_datos_al_backend(nombre, peso, altura, deporte, foto_bytes, foto_name, plan_meses):
        import requests
        import threading
        
        def api_call():
            try:
                url = "https://run.app/registro"
                
                # Intentar abrir la foto físicamente del disco
                ruta_foto = "foto_usuario.jpg"
                if page.data and page.data.get("foto_url"):
                    ruta_foto = page.data.get("foto_url")
                elif state.get("foto_url"):
                    ruta_foto = state.get("foto_url")
                    
                import os
                # Si el archivo físico no existe, lo creamos a partir de los bytes para tener el "archivo real"
                if not os.path.exists(ruta_foto) and foto_bytes:
                    try:
                        with open(ruta_foto, "wb") as f_temp:
                            f_temp.write(foto_bytes)
                    except Exception as w_err:
                        log_debug(f"[API] No se pudo escribir archivo temporal para envío: {w_err}")
                
                logger_msg = f"[API] Enviando datos a {url} (multipart/form-data) leyendo físicamente de {ruta_foto}..."
                log_debug(logger_msg)
                print(logger_msg)
                
                try:
                    with open(ruta_foto, "rb") as f:
                        files = {
                            "foto": (os.path.basename(ruta_foto), f, "image/jpeg")
                        }
                        data = {
                            "nombre": nombre,
                            "peso": str(peso),
                            "altura": str(altura),
                            "deporte": deporte,
                            "plan_meses": str(plan_meses)
                        }
                        response = requests.post(url, data=data, files=files, timeout=15.0)
                except Exception as io_ex:
                    log_debug(f"[API] Falló lectura de archivo {ruta_foto}, fallback en memoria: {io_ex}")
                    files = {
                        "foto": (foto_name, foto_bytes, "image/jpeg")
                    }
                    data = {
                        "nombre": nombre,
                        "peso": str(peso),
                        "altura": str(altura),
                        "deporte": deporte,
                        "plan_meses": str(plan_meses)
                    }
                    response = requests.post(url, data=data, files=files, timeout=15.0)
                
                if response.status_code == 201:
                    plan_data = response.json()
                    state["plan_data"] = plan_data
                    print("[API] Rutina de la IA recibida exitosamente del backend.")
                    
                    # Cargar ejercicios de la IA en el estado para el entrenamiento activo si están disponibles
                    if "bloques_mensuales" in plan_data and len(plan_data["bloques_mensuales"]) > 0:
                        bloque1 = plan_data["bloques_mensuales"][0]
                        for rutina in bloque1.get("rutina_semanal", []):
                            if rutina.get("dia") == "Lunes":
                                state["ejercicios"] = [
                                    {
                                        "nombre": ej["nombre"],
                                        "series": ej["series"],
                                        "repeticiones": ej["repeticiones"],
                                        "anim": ej["id_animacion_avatar"]
                                    } for ej in rutina.get("ejercicios", [])
                                ]
                else:
                    print(f"[API] Error del backend ({response.status_code}): {response.text}")
            except Exception as ex:
                print(f"[API] Error de conexión con el backend: {ex}")
                
        threading.Thread(target=api_call, daemon=True).start()

    def on_registrar(e):
        try:
            lbl_error.value = ""
            log_debug(f"[Registrar] on_registrar ejecutándose. Nombre={txt_nombre.value}, Peso={txt_peso.value}, Altura={txt_altura.value}")
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
                
            foto_bytes = state.get("foto_bytes") or (page.data.get("foto_bytes") if page.data else None)
            foto_name = state.get("foto_name") or (page.data.get("foto_name") if page.data else None)
            log_debug(f"[Registrar] Datos iniciales de foto: bytes_len={len(foto_bytes) if foto_bytes else 'None'}, name={foto_name}")
            print(f"[Registrar DEBUG] Validando foto: name={foto_name}, bytes_len={len(foto_bytes) if foto_bytes else 'None'}")
            
            if not foto_bytes or not foto_name:
                # Fallback de último recurso: intentar leer la ruta guardada si existe
                foto_path = state.get("foto_url") or (page.data.get("foto_url") if page.data else None)
                log_debug(f"[Registrar] Intento de fallback con foto_path={foto_path}")
                if foto_path and os.path.exists(foto_path) and os.path.isfile(foto_path):
                    try:
                        with open(foto_path, "rb") as f:
                            foto_bytes = f.read()
                        state["foto_bytes"] = foto_bytes
                        state["foto_name"] = os.path.basename(foto_path)
                        log_debug(f"[Registrar] Fallback exitoso de lectura: {len(foto_bytes)} bytes de {foto_path}")
                    except Exception as ex_read:
                        log_debug(f"[Registrar] Fallback fallo de lectura: {ex_read}")
                
                # Volver a verificar
                foto_bytes = state.get("foto_bytes") or (page.data.get("foto_bytes") if page.data else None)
                foto_name = state.get("foto_name") or (page.data.get("foto_name") if page.data else None)
                if not foto_bytes or not foto_name:
                    log_debug("[Registrar] Activando SIMULACIÓN DE RESPALDO (MOCK) por falta de hardware/bytes reales.")
                    foto_bytes = b"bytes_de_imagen_de_prueba_roky"
                    foto_name = "foto_camara_mock.png"
                    state["foto_bytes"] = foto_bytes
                    state["foto_name"] = foto_name

            # Guardar datos en el estado y page.data
            state["nombre"] = txt_nombre.value
            state["peso"] = peso
            state["altura"] = altura
            state["deporte"] = dd_deporte.value
            state["avatar_seed"] = txt_nombre.value.replace(" ", "") or "roky"
            
            if page.data is None:
                page.data = {}
            page.data["nombre"] = txt_nombre.value
            page.data["peso"] = peso
            page.data["altura"] = altura
            page.data["deporte"] = dd_deporte.value
            page.data["avatar_seed"] = state["avatar_seed"]
            page.data["foto_bytes"] = foto_bytes
            page.data["foto_name"] = foto_name
            page.data["foto_url"] = state.get("foto_url") or "foto_usuario.jpg"
            page.data["foto_base64"] = state.get("foto_base64")
            
            # Enviar los datos en segundo plano al backend (puerto 8000)
            enviar_datos_al_backend(
                nombre=state["nombre"],
                peso=state["peso"],
                altura=state["altura"],
                deporte=state["deporte"],
                foto_bytes=foto_bytes,
                foto_name=foto_name,
                plan_meses=state.get("plan_meses", 3)
            )
                     
            # Cambiar inmediatamente al estado de la Pantalla 2 ("plan")
            navegar_a("plan")
        except Exception as err:
            print(f"[Registrar DEBUG] Error en on_registrar: {err}")
            lbl_error.value = f"Error al registrar: {err}"
            page.update()


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
                            btn_upload,
                            ft.Text("Sube o simula tu foto", size=11, color="#8B949E")
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=15
                ),

                
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
    # Ya no mostramos la pantalla de carga bloqueante. Se selecciona el plan de inmediato.
    avatar_seed = state.get('avatar_seed', 'roky')
    
    # Una vez cargado, mostramos el avatar y las tarjetas de plan
    avatar_url = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={avatar_seed}&mood[]=happy"
    
    # Recuperamos la foto del estado global para persistencia
    foto_base64 = None
    if page.data and isinstance(page.data, dict) and page.data.get("foto_base64"):
        foto_base64 = page.data["foto_base64"]
    elif state.get("foto_base64"):
        foto_base64 = state.get("foto_base64")
        
    if foto_base64:
        avatar_img_src = f"data:image/jpeg;base64,{foto_base64}"
    else:
        avatar_img_src = avatar_url
        
    avatar_display = ft.Container(
        content=ft.Image(
            src=avatar_img_src, 
            width=110, 
            height=110, 
            fit="cover" if foto_base64 else "contain",
            border_radius=55 if foto_base64 else 0
        ),
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
                padding=ft.padding.Padding(left=6, right=6, top=1, bottom=1),
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
    peso_inicial = state.get("peso", 70.0)
    plan_meses = state.get("plan_meses", 3)
    grasa_inicial = 22.0 if state.get("deporte") == "Fitness / Gimnasio" else 18.0
    
    # 1. Definición exacta de las variables y textos
    lbl_weight = ft.Text(f"{peso_inicial} kg", size=13, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_mes_actual = ft.Text(f"Mes 0 de {plan_meses}", size=12, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_muscle = ft.Text("+0.0 kg", size=13, weight=ft.FontWeight.BOLD, color="#00FF66")
    lbl_fat = ft.Text(f"{grasa_inicial}%", size=13, weight=ft.FontWeight.BOLD, color="#00FF66") # Verde neón
    lbl_slider_mes = ft.Text(f"Mes 0 de {plan_meses}", size=12, weight=ft.FontWeight.BOLD, color="#00F0FF")
    
    # Función para crear contenedores flotantes de estadísticas
    def create_stat_box(title, control, icon, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(icon, size=12, color=color),
                        ft.Text(title, size=8, color="#8B949E", weight=ft.FontWeight.BOLD)
                    ], spacing=3),
                    control
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.START
            ),
            bgcolor="#161B22",
            padding=6,
            border_radius=8,
            border=ft.Border.all(1, "#1F2937"),
            width=100,
            height=58
        )
        
    box_weight = create_stat_box("PESO ACTUAL", lbl_weight, ft.Icons.MONITOR_WEIGHT, "#00F0FF")
    box_mes_actual = create_stat_box("MES ACTUAL", lbl_mes_actual, ft.Icons.CALENDAR_TODAY, "#00F0FF")
    box_muscle = create_stat_box("MÚSCULO GANADO", lbl_muscle, ft.Icons.FITNESS_CENTER, "#00FF66")
    box_fat = create_stat_box("GRASA CORPORAL", lbl_fat, ft.Icons.PERCENT, "#00FF66")

    # 2. Componente de Carga y Tarjeta Central del Avatar
    avatar_loading = ft.Column(
        controls=[
            ft.ProgressRing(color="#00FF66", width=40, height=40),
            ft.Text("Procesando...", size=10, color="#8B949E", weight=ft.FontWeight.BOLD)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=8
    )
    
    # Evitar renderizar "PROCESANDO" como URL de imagen
    has_avatar = state.get("avatar_comic_url") and state.get("avatar_comic_url") != "PROCESANDO"

    img_avatar = ft.Image(
        src=state.get("avatar_comic_url", "") if has_avatar else "",
        width=130,
        height=130,
        fit="contain",
        animate_scale=ft.Animation(300, "easeOut")
    )
    
    avatar_card = ft.Container(
        content=img_avatar if has_avatar else avatar_loading,
        alignment=ft.alignment.Alignment.CENTER,
        width=140,
        height=140,
        border_radius=70,
        bgcolor="#161B22",
        border=ft.Border.all(2, "#00FF66" if has_avatar else "#00F0FF")
    )

    # Polling asíncrono para comprobar el estado del avatar en FastAPI
    def poll_avatar_status():
        import time
        import requests
        nombre_req = state.get("nombre", "")
        if not nombre_req:
            return
            
        url = f"https://run.app/registro/status?nombre={nombre_req}"
        for _ in range(30):  # Limitar a 30 segundos
            try:
                response = requests.get(url, timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ready"):
                        state["avatar_comic_url"] = data.get("avatar_comic_url")
                        state["avatar_generado"] = True
                        
                        # Actualizar la interfaz del avatar
                        img_avatar.src = state["avatar_comic_url"]
                        avatar_card.content = img_avatar
                        avatar_card.border = ft.Border.all(2, "#00FF66")
                        try:
                            page.update()
                        except Exception:
                            pass
                        break
            except Exception as e:
                print(f"[Polling Error] {e}")
            time.sleep(1.0)

    # Iniciar polling si el avatar no está listo
    if not state.get("avatar_generado", False):
        import threading
        threading.Thread(target=poll_avatar_status, daemon=True).start()

    # Columnas flotantes a los lados
    col_left = ft.Column(
        controls=[box_weight, box_mes_actual],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )
    col_right = ft.Column(
        controls=[box_muscle, box_fat],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    seccion_central = ft.Row(
        controls=[col_left, avatar_card, col_right],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10
    )

    exercises_container = ft.Column(spacing=6)
    
    def get_rutina_mes(mes):
        if mes == 0:
            return "Rutina de Entrada", [
                {"nombre": "Movilidad Articular", "series": 3, "reps": 10},
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
        lbl_mes_actual.value = f"Mes {mes} de {plan_meses}"
        lbl_slider_mes.value = f"Mes {mes} de {plan_meses}"
        
        state["peso_estimado"] = peso_estimado
        
        fase_title, ejercicios = get_rutina_mes(mes)
        
        # Escalar avatar levemente si está cargado
        if state.get("avatar_comic_url"):
            img_avatar.scale = 1.0 - (mes * 0.015)
            
        # Actualizar ejercicios del panel inferior en tiempo real
        exercises_container.controls.clear()
        exercises_container.controls.append(
            ft.Text("Entrenamiento de Hoy", size=12, color="#00FF66", weight=ft.FontWeight.BOLD)
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

    # Inicializar estado inicial
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
        content=ft.Text("Iniciar Rutina", color="#000000", weight=ft.FontWeight.BOLD, size=16),
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
                # Header superior centralizado
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_IOS_NEW,
                            icon_color="#00F0FF",
                            icon_size=16,
                            on_click=lambda _: navegar_a("plan")
                        ),
                        ft.Text("Mi Progreso", size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
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
                
                # Sección central simétrica
                seccion_central,
                ft.Divider(height=5, color="transparent"),
                
                # Slider horizontal
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Tu Transformación", size=12, color="#FFFFFF", weight=ft.FontWeight.BOLD),
                            lbl_slider_mes
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        slider
                    ], spacing=5),
                    padding=10,
                    bgcolor="#161B22",
                    border_radius=10,
                    border=ft.Border.all(1, "#1F2937")
                ),
                ft.Divider(height=5, color="transparent"),
                
                # Panel de Control Inferior: Entrenamiento de Hoy
                ft.Container(
                    content=exercises_container,
                    padding=12,
                    bgcolor="#161B22",
                    border_radius=10,
                    border=ft.Border.all(1, "#1F2937")
                ),
                ft.Divider(height=5, color="transparent"),
                
                # Botón de Inicio de Rutina
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
    # Forzar ft.ImageFit a usar strings para máxima compatibilidad con todas las versiones de Flet
    class ImageFitHelper:
        CONTAIN = "contain"
        COVER = "cover"
        FILL = "fill"
    ft.ImageFit = ImageFitHelper

    if "ejercicios" not in state or not state["ejercicios"]:
        state["ejercicios"] = [
            {"nombre": "Sentadillas Cyber", "series": 4, "repeticiones": 15, "anim": "squats"},
            {"nombre": "Flexiones Neón", "series": 3, "repeticiones": 12, "anim": "pushups"},
            {"nombre": "Plancha Cuántica", "series": 3, "repeticiones": 45, "anim": "plank"}
        ]
        
    state["ejercicio_actual"] = state.get("ejercicio_actual", 0)
    state["serie_actual"] = state.get("serie_actual", 1)
    
    # 1. Declaración exacta requerida para la imagen del avatar de Roky
    avatar_roky = ft.Image(
        src="avatar_roky.gif", 
        width=350, 
        height=180, 
        fit=ft.ImageFit.CONTAIN
    )
    
    lbl_ex_name = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF")
    lbl_series_reps = ft.Text("", size=15, color="#00F0FF", weight=ft.FontWeight.W_500)
    lbl_timer = ft.Text("", size=24, weight=ft.FontWeight.BOLD, color="#00FF66", visible=False)
    
    avatar_box = ft.Container(
        content=avatar_roky,
        alignment=ft.alignment.Alignment.CENTER,
        height=180,
        border_radius=15,
        bgcolor="#161B22",
        border=ft.Border.all(1, "#1F2937")
    )

    async def ejecutar_timer_descanso(e=None):
        import asyncio
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
            await asyncio.sleep(1)
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
        
        # 2. Mapeo dinámico eliminando barra inclinada inicial para leer dentro del sandbox
        anim_id = ex.get("anim") or ex.get("id_animacion_avatar") or ""
        local_path = f"assets/animations/{anim_id}.gif" if anim_id else ""
        
        if anim_id and os.path.exists(local_path):
            src_path = f"animations/{anim_id}.gif"  # Mapeo relativo sin barra inicial
            w, h = 350, 180
        else:
            if os.path.exists("assets/animations/jogging.gif"):
                src_path = "animations/jogging.gif"  # Mapeo relativo sin barra inicial
                w, h = 350, 180
            else:
                src_path = f"https://api.dicebear.com/7.x/pixel-art/svg?seed={state.get('avatar_seed', 'roky')}&mood[]=happy"
                w, h = 130, 130
            
        avatar_roky.src = src_path
        avatar_roky.width = w
        avatar_roky.height = h
        print(f"[debug] actualizar_pantalla: src_path = {src_path}")
        
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

    # 3. Refresco diferido para limpiar caché inmediatamente después de montar el componente
    async def refrescar_tras_montar(e=None):
        import asyncio
        await asyncio.sleep(0.08)
        try:
            actualizar_pantalla()
        except Exception:
            pass

    page.run_task(refrescar_tras_montar)

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
    page.data = {}
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

    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    state["file_picker"] = file_picker

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
    ft.app(target=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=8501, host="127.0.0.1")
