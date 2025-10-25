from flask import Flask, request, send_file, render_template_string
import pandas as pd
import tempfile
import os

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Transformador Aconpy</title>
  <style>
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #f6f8fa;
      color: #333;
      text-align: center;
      padding: 50px;
    }
    .container {
      background: white;
      border-radius: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      display: inline-block;
      padding: 40px 60px;
    }
    h2 {
      color: #2c3e50;
      margin-bottom: 30px;
    }
    input[type=file] {
      display: block;
      margin: 0 auto 20px auto;
      border: 2px dashed #ccc;
      border-radius: 10px;
      padding: 10px;
      width: 280px;
      cursor: pointer;
      background-color: #fafafa;
    }
    input[type=submit] {
      background: #007bff;
      border: none;
      color: white;
      padding: 12px 28px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 16px;
      transition: background 0.3s;
    }
    input[type=submit]:hover {
      background: #0056b3;
    }
    .loading {
      display: none;
      font-size: 16px;
      color: #007bff;
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>📊 Transformador Aconpy</h2>
    <form id="upload-form" method="post" enctype="multipart/form-data">
      <input type="file" name="file" accept=".xlsx" required>
      <input type="submit" value="Transformar Excel">
    </form>
    <div class="loading" id="loading">⏳ Procesando archivo...</div>
  </div>

  <script>
    const form = document.getElementById('upload-form');
    form.addEventListener('submit', () => {
      document.getElementById('loading').style.display = 'block';
    });
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if not file:
            return "No se subió ningún archivo", 400

        df_entrada = pd.read_excel(file)

        grupos = df_entrada.groupby("Detalle")
        filas_transformadas = []

        columnas_salida = [
            "Fecha", "Descripción", "AXI", "Cuenta", "Debe", "Haber",
            "Organización", "Centro de Costos"
        ]

        for nombre_grupo, grupo in grupos:
            grupo = grupo.copy()

            fila_encabezado = [None] * len(columnas_salida)
            fila_encabezado[0] = grupo["Fecha"].iloc[0]
            fila_encabezado[1] = nombre_grupo
            filas_transformadas.append(fila_encabezado)

            for _, fila in grupo.iterrows():
                nueva_fila = [None] * len(columnas_salida)
                nueva_fila[3] = fila["Cuenta"]
                nueva_fila[4] = fila["Debe"] if pd.notna(fila["Debe"]) else None
                nueva_fila[5] = fila["Haber"] if pd.notna(fila["Haber"]) else None
                filas_transformadas.append(nueva_fila)

        df_resultado = pd.DataFrame(filas_transformadas, columns=columnas_salida)
        df_resultado["Fecha"] = pd.to_datetime(df_resultado["Fecha"], errors="coerce").dt.strftime("%d/%m/%Y")

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        df_resultado.to_excel(temp_file.name, index=False)

        return send_file(temp_file.name, as_attachment=True, download_name="transformado_aconpy.xlsx")

    return render_template_string(HTML_FORM)

# ✅ Este bloque garantiza compatibilidad con Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Puerto asignado por Render
    app.run(host="0.0.0.0", port=port)
