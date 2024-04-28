from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from flask import jsonify
import os

app = Flask(__name__)
app.config ["UPLOAD_FOLDER"]="./static/imagenes"
app.secret_key = "clave_secreta"  


client = MongoClient('mongodb://localhost:27017/')
db = client['mi_base_de_datos']
productos_collection = db['productos']
usuarios_collection = db['usuarios']
categorias_collection = db['categorias']

@app.route('/')
def inicio():
    if 'usuario' in session:
        usuario = session["usuario"]
        productos = productos_collection.find()
        categorias = categorias_collection.find()
        return render_template('tabla.html', usuario=usuario, productos=productos, categorias=categorias)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        print(usuario)
        contraseña = request.form['contraseña']
        print(contraseña)
        usuario_encontrado = usuarios_collection.find_one({'nombre': usuario})
        print("hola")
        print(usuario_encontrado )
        if usuario_encontrado:
            print("iiii")
            session['usuario'] = usuario
            return redirect("/")
        else:
            # Mostrar una alerta de SweetAlert si las credenciales son incorrectas
            return render_template('login.html', mensaje="Usuario o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))


@app.route('/registrar_producto', methods=['POST'])
def registrar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            precio = request.form['precio']
            categoria = request.form['categoria']
            foto = request.form['foto']
            foto1 = request.files['foto1']

            # Validación de campos obligatorios
            if not codigo or not nombre or not precio or not categoria or not foto:
                return "Todos los campos son obligatorios. Por favor, completa el formulario."

            # este inserta los datos a la base de datos
            producto = {
                "codigo": codigo,
                "nombre": nombre,
                "precio": precio,
                "categoria": categoria,
                "foto": foto
            }
            resultado = productos_collection.insert_one(producto)
            if (resultado.acknowledged):
                foto1.save(f"{os.path.join(app.config['UPLOAD_FOLDER'])}/{producto['codigo']}.jpg")


            return redirect(url_for('inicio'))
    return redirect(url_for('login'))


@app.route('/eliminar_producto', methods=['POST'])
def eliminar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            codigo = request.json.get('codigo')
            productos_collection.delete_one({'codigo': codigo})
            return 'Producto eliminado exitosamente', 200
    return redirect(url_for('login'))




@app.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    if 'usuario' in session:
        if request.method == 'POST':
            datos_producto = request.json
            codigo = datos_producto.get('codigo')
            nombre = datos_producto.get('nombre')
            precio = datos_producto.get('precio')
            categoria = datos_producto.get('categoria')
            foto = datos_producto.get('foto')

            # Actualiza el producto en la base de datos
            productos_collection.update_one(
                {'codigo': codigo},
                {'$set': {'nombre': nombre, 'precio': precio, 'categoria': categoria, 'foto': foto}}
            )

            return 'Producto actualizado exitosamente', 200
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)
