# Recomendador de Animes, RecoAnimesFLV

Sistema de recomendación de animes basado en valoraciones de los usuarios, desarrollado con **Flask (BackEnd)** y una interfaz web **HTML + CSS + javascript (FrontEnd)** con temática de anime y inspiración de Solo Leveling.

---

## Iniciar la App

1. Abre una terminal dentro de la carpeta `/back` del proyecto o cambia el directorio a dicha carpeta.
   ```bash
   /cd ../Recomendador_Animes/back
   ```
2. Instala **Python** y **pip** desde navegador o desde la terminal:

   **Windows**: [Descargar desde python.org](https://www.python.org/downloads/)  
     (marca la opción *“Add Python to PATH”* durante la instalación)

   **macOS**
     ```bash
     brew install python3
     ```

   **Linux (Ubuntu/Debian)**
     ```bash
     sudo apt update
     sudo apt install python3 python3-pip -y
     ```
3. activar entorno de myenv 
   ```
   source myvenv/bin/activate
   ```
4. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```
5. Ejecuta el servidor:
   ```bash
   flask --app back/app.py run
   ```
6. Por defecto, el servidor se ejecutará en:
   ```
   http://127.0.0.1:5000
   ```

---

## Iniciar la pagina de Loggin

1. Entra en la pagina`http://localhost:5500/logginweb.html` en tu navegador (usa doble clic o “Abrir con > navegador”).
2. Inicia sesión con un usuario válido.
3. Una vez logueado, accederás automáticamente a la pagina principal de RecoAnimesFLV (`app.html`).

---

## Cómo usar la pagina Principal de RecoAnimesFLV

1. Inicia sesión con tu usuario.
2. Entrena el modelo de recomendaciones, en el pie de la pagina.
3. Verifica el estado del sistema, en el pie de la pagina
4. Escribe tu ID en el panel principal de recomendaciones.
5. En la sección de resultados, se mostrarán los animes más afines según tus puntuaciones previas siempre y cuando hagas puntuado mas de 5 animes.

---

## Estructura del proyecto

```
📂 Proyecto_Recomendador_Animes
 ┣ 📂 back
 ┃ ┣ 📜 app.py
 ┃ ┣ 📂 models
 ┃ ┃ ┣ 📜 recommendation_model.py
 ┣ 📂 data
 ┃ ┣ 📜 anime.csv
 ┃ ┣ 📜 rating.csv
 ┣ 📂 front
 ┃ ┣ 📜 logginweb.html
 ┃ ┣ 📜 app.html
 ┃ ┣ 📜 style.css
```

---

## Machine Learning

El modelo implementa un **sistema de recomendación colaborativo**, que analiza las valoraciones de los usuarios para detectar patrones y sugerir animes con características similares a los que más les gustan.

### Características técnicas:
- **Python + Flask** para el servidor BackEnd  
- **pandas + numpy** para manejo de datos  
- **Modelo colaborativo simple basado en similitud de usuarios**  
- **Estructura modular (modelo separado del servidor)**  

---

## Diseño del FrontEnd

- Interfaz visual tipo **anime / oscuridad** con degradados morado-azules  
- Fondos personalizables con imágenes de anime  
- Botones animados con efectos “glow” y hover  
- Distribución responsive (se adapta a todas las pantallas)  
- Integración con el sistema de recomendaciones del BackEnd
- Animaciones CSS tipo “anime”  

---

## Vista previa

### Pantalla de Inicio de Sesión
![Login Preview](https://i.imgur.com/7fQmsfG.png)

### Panel Principal del Recomendador
![App Preview](https://i.imgur.com/dpzL17O.png)

---

## Tecnologías utilizadas

### BackEnd
- Flask
- pandas / numpy
- joblib (para guardar modelos)
- Flask-CORS

### FrontEnd
- HTML5 + CSS3
- JavaScript (fetch API)

---

## Autores

**Pablo y Mario**  
- Proyecto de recomendación de animes — 2025  
- Desarrollado como práctica de integración Flask + FrontEnd
- Todos los Derechos Reservados

---

