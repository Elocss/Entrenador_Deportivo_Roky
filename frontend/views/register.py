import flet as ft
import re
from frontend import api_client

def get_register_view(page: ft.Page, on_register_success):
    # Validaciones
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    # Elementos de la interfaz
    txt_name = ft.TextField(
        label="Nombre Completo",
        border_color="#8B949E",
        focused_border_color="#00F0FF",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF"),
        cursor_color="#00F0FF",
    )
    
    txt_email = ft.TextField(
        label="Correo Electrónico",
        border_color="#8B949E",
        focused_border_color="#00F0FF",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF"),
        cursor_color="#00F0FF",
    )
    
    txt_weight = ft.TextField(
        label="Peso (kg)",
        keyboard_type="number",
        border_color="#8B949E",
        focused_border_color="#00F0FF",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF"),
        cursor_color="#00F0FF",
    )
    
    txt_height = ft.TextField(
        label="Altura (cm)",
        keyboard_type="number",
        border_color="#8B949E",
        focused_border_color="#00F0FF",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF"),
        cursor_color="#00F0FF",
    )
    
    dd_sport = ft.Dropdown(
        label="Deporte de Entrenamiento",
        options=[
            ft.dropdown.Option("Fitness / Gimnasio"),
            ft.dropdown.Option("Running"),
        ],
        value="Fitness / Gimnasio",
        border_color="#8B949E",
        focused_border_color="#00F0FF",
        label_style=ft.TextStyle(color="#8B949E"),
        text_style=ft.TextStyle(color="#FFFFFF"),
    )

    lbl_error = ft.Text(value="", color="#FF3333", size=14, weight=ft.FontWeight.BOLD)
    
    # Simulación de foto de cámara
    img_preview = ft.Image(
        src="https://placehold.co/400x400/161B22/8B949E?text=Captura+de+Cámara",
        width=150,
        height=150,
        fit="cover",
        border_radius=75
    )
    
    uploaded_file_path = None
    
    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal uploaded_file_path
        if e.files:
            uploaded_file_path = e.files[0].path
            img_preview.src = uploaded_file_path
            btn_photo.content = "¡Foto Cargada!"
            btn_photo.icon = ft.Icons.CHECK_CIRCLE
            btn_photo.style = ft.ButtonStyle(color="#00FF66")
            page.update()

    file_picker = ft.FilePicker()
    file_picker.on_result = on_file_selected
    page.overlay.append(file_picker)

    async def handle_photo_btn_click(e):
        # Simular apertura de cámara / selección de archivo
        await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["jpg", "png", "jpeg"]
        )

    btn_photo = ft.ElevatedButton(
        content="Capturar Foto Frontal",
        icon=ft.Icons.CAMERA_ALT,
        style=ft.ButtonStyle(
            color="#FFFFFF",
            bgcolor="#161B22",
            side=ft.BorderSide(1, "#00F0FF"),
        ),
        on_click=handle_photo_btn_click
    )

    def on_register_click(e):
        lbl_error.value = ""
        
        # Validar campos
        if not txt_name.value or not txt_email.value or not txt_weight.value or not txt_height.value:
            lbl_error.value = "Por favor, completa todos los campos."
            page.update()
            return
            
        if not validate_email(txt_email.value):
            lbl_error.value = "Correo electrónico inválido."
            page.update()
            return
            
        try:
            weight = float(txt_weight.value)
            height = int(txt_height.value)
            if weight <= 0 or height <= 0:
                lbl_error.value = "El peso y la altura deben ser mayores que cero."
                page.update()
                return
        except ValueError:
            lbl_error.value = "Peso y altura deben ser numéricos."
            page.update()
            return
            
        # Registrar en backend
        page.splash = ft.ProgressBar(color="#00FF66")
        page.update()
        
        try:
            # Plan por defecto es 3 meses inicialmente, se puede cambiar en la siguiente pantalla
            user = api_client.registrar_usuario(
                name=txt_name.value,
                email=txt_email.value,
                weight=weight,
                height=height,
                sport=dd_sport.value,
                plan_months=3 # Inicialmente 3
            )
            
            # Subir foto si se seleccionó una
            if uploaded_file_path and user:
                api_client.subir_foto_perfil(user["id_usuario"], uploaded_file_path)
                
            page.splash = None
            page.update()
            
            # Callback de éxito con datos de usuario
            on_register_success(user)
            
        except Exception as ex:
            page.splash = None
            lbl_error.value = f"Error de conexión: {str(ex)}"
            page.update()

    btn_submit = ft.Container(
        content=ft.Text("Registrar y Crear Avatar", color="#000000", weight=ft.FontWeight.BOLD, size=16),
        alignment=ft.alignment.Alignment.CENTER,
        bgcolor="#00FF66",
        height=50,
        border_radius=10,
        on_click=on_register_click,
    )

    # Layout de la pantalla
    return ft.View(
        route="/register",
        bgcolor="#0D1117",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        # Título
                        ft.Text("ROKY", size=42, weight=ft.FontWeight.BOLD, color="#00FF66", text_align=ft.TextAlign.CENTER),
                        ft.Text("Tu Avatar Inteligente de Entrenamiento", size=14, color="#8B949E", text_align=ft.TextAlign.CENTER),
                        ft.Divider(height=10, color="transparent"),
                        
                        # Avatar Preview / Cámara
                        ft.Column(
                            controls=[
                                img_preview,
                                btn_photo
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10
                        ),
                        ft.Divider(height=10, color="transparent"),
                        
                        # Campos
                        txt_name,
                        txt_email,
                        ft.Row(
                            controls=[txt_weight, txt_height],
                            spacing=10
                        ),
                        dd_sport,
                        
                        lbl_error,
                        ft.Divider(height=5, color="transparent"),
                        
                        # Botón
                        btn_submit
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                ),
                width=360,
                padding=25,
                border_radius=15,
                bgcolor="#161B22",
                border=ft.Border.all(1, "#1F2937")
            )
        ]
    )
