import flet as ft
import time
from frontend import api_client

def get_loading_selection_view(page: ft.Page, user_data, on_plan_selected):
    user_id = user_data["id_usuario"]
    
    # Contenedor dinámico que cambiará de estado
    content_container = ft.Container(alignment=ft.alignment.Alignment.CENTER)

    # Estado 1: Cargando y Generando Avatar
    lbl_status = ft.Text(
        "Analizando facciones...", 
        size=16, 
        color="#8B949E", 
        text_align=ft.TextAlign.CENTER
    )
    progress_bar = ft.ProgressBar(color="#00F0FF", width=300)
    
    loading_layout = ft.Column(
        controls=[
            ft.Text("ROKY IA GENERATIVA", size=24, weight=ft.FontWeight.BOLD, color="#00F0FF"),
            ft.Divider(height=20, color="transparent"),
            lbl_status,
            progress_bar,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )
    
    content_container.content = loading_layout

    # Función para simular el proceso de generación en pasos
    def simular_generacion():
        pasos = [
            "Procesando foto de medio cuerpo...",
            "Extrayendo puntos de referencia faciales...",
            "Aplicando estilo de dibujo Comic 2D...",
            "Optimizando paleta de colores Cyber...",
            "¡Avatar ROKY listo!"
        ]
        
        for paso in pasos:
            lbl_status.value = paso
            page.update()
            time.sleep(0.8)
            
        mostrar_seleccion_plan()

    # Estado 2: Mostrar Avatar y Botones de Selección de Plan
    def mostrar_seleccion_plan():
        # Obtener el avatar generado del usuario
        avatar_url = user_data.get("avatar_comic_url", "https://api.dicebear.com/7.x/pixel-art/svg?seed=roky")
        
        avatar_image = ft.Image(
            src=avatar_url,
            width=180,
            height=180,
            fit="contain",
            border_radius=90
        )
        
        def select_plan(meses):
            # Registrar plan seleccionado actualizando el usuario
            try:
                page.splash = ft.ProgressBar(color="#00FF66")
                page.update()
                
                # Actualizar plan del usuario en el backend
                api_client.registrar_usuario(
                    name=user_data["nombre"],
                    email=user_data["correo"],
                    weight=user_data["peso_actual_kg"],
                    height=user_data["altura_cm"],
                    sport=user_data["deporte_elegido"],
                    plan_months=meses
                )
                
                page.splash = None
                page.update()
                
                # Avanzar con el plan elegido
                on_plan_selected(meses)
            except Exception as ex:
                page.splash = None
                page.update()
                print(f"Error al guardar plan: {ex}")
                on_plan_selected(meses) # Fallback

        plan_layout = ft.Column(
            controls=[
                ft.Text("¡Tu Avatar Roky está Listo!", size=22, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                ft.Text("Inspirado en tus facciones, listo para entrenar", size=14, color="#8B949E"),
                ft.Divider(height=10, color="transparent"),
                
                # Tarjeta de Avatar
                ft.Container(
                    content=avatar_image,
                    padding=10,
                    border_radius=100,
                    bgcolor="#0D1117",
                    border=ft.Border.all(2, "#00F0FF")
                ),
                ft.Divider(height=15, color="transparent"),
                
                # Selección de planes
                ft.Text("Selecciona la duración de tu plan:", size=16, weight=ft.FontWeight.BOLD, color="#00FF66"),
                ft.Divider(height=5, color="transparent"),
                
                ft.ElevatedButton(
                    content="Plan Inicial - 3 Meses",
                    style=ft.ButtonStyle(
                        color="#000000",
                        bgcolor="#00F0FF",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=260,
                    height=45,
                    on_click=lambda _: select_plan(3)
                ),
                ft.ElevatedButton(
                    content="Plan Intermedio - 6 Meses",
                    style=ft.ButtonStyle(
                        color="#000000",
                        bgcolor="#00FF66",
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=260,
                    height=45,
                    on_click=lambda _: select_plan(6)
                ),
                ft.ElevatedButton(
                    content="Plan Élite - 9 Meses",
                    style=ft.ButtonStyle(
                        color="#FFFFFF",
                        bgcolor="#161B22",
                        side=ft.BorderSide(1, "#00FF66"),
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=260,
                    height=45,
                    on_click=lambda _: select_plan(9)
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        )
        
        content_container.content = plan_layout
        page.update()

    # Iniciar simulación en segundo plano al montar la vista
    # Usamos page.run_task para ejecutar la simulación de forma no bloqueante
    page.run_task(simular_generacion)

    return ft.View(
        route="/loading_selection",
        bgcolor="#0D1117",
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                content=content_container,
                width=360,
                padding=30,
                border_radius=15,
                bgcolor="#161B22",
                border=ft.Border.all(1, "#1F2937")
            )
        ]
    )
