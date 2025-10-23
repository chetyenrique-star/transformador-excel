from flask import Flask, request, send_file, render_template_string
import pandas as pd
import tempfile

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>Transformador de Excel</title>
<h2>Sube tu archivo Diario_original.xlsx</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file accept=".xlsx">
  <input type=submit value=Transformar>
</form>
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

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
