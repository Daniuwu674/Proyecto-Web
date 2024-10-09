from flask import Flask, render_template, request, redirect, url_for, request, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__, template_folder='.', static_folder='static')

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Leonxd674'
app.config['MYSQL_DB'] = 'tienda'

mysql = MySQL(app)

@app.route('/')
def index():
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM producto")
    productos_raw = cur.fetchall()

    cur.execute("SELECT * FROM categoria")
    categorias_raw=cur.fetchall()
    cur.close()

    productos = []
    for producto in productos_raw:
        productos.append({
            'id': producto[0],
            'nombre': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'imagen': producto[5]
        })
    for producto in productos:
        print(f"URL completa de imagen: {url_for('static', filename='images/' + producto['imagen'], _external=True)}")

    categorias=[]
    for categoria in categorias_raw:
        categorias.append({
            'id': categoria[0],
            'nombre': categoria[1],
            'descripcion': categoria[2],
        })
    return render_template('index.html', productos=productos, categorias=categorias)
     
@app.route('/hacer-pedido/<int:producto_id>')
def hacer_pedido(producto_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM producto WHERE id_Producto = %s", (producto_id,))
    producto = cur.fetchone()
    cur.close()
    return render_template('hacer_pedido.html', producto=producto)

@app.route('/procesar-pedido', methods=['POST'])
def procesar_pedido():
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        nombre = request.form['nombre']
        email = request.form['email']
        direccion = request.form['direccion']
        cantidad = request.form['cantidad']
        
        
        cur = mysql.connection.cursor()
        id_usuario=1
        fecha_pedido=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("INSERT INTO pedido (id_usuario, fecha_pedido) VALUES (%s, %s)", (id_usuario, fecha_pedido))
                    
        mysql.connection.commit()
        id_pedido=cur.lastrowid

        cur.execute("SELECT precio FROM producto WHERE id_Producto= %s", (producto_id))
        precio_unitario=cur.fetchone()[0]

        cur.execute("INSERT INTO detalle_pedido(id_pedido, id_producto, cantidad, precio_unitario) VALUES (%s,%s,%s,%s)",
                    (id_pedido, producto_id, cantidad, precio_unitario))
        mysql.connection.commit()
        cur.close()
        
        return render_template('pedido_exitoso.html')

@app.route('/categoria/<int:categoria_id>')
def productos_por_categoria(categoria_id):
    cur =mysql.connection.cursor()

    cur.execute("""
        SELECT p.id_Producto, p.nombre_producto, p.descripcion, p.precio, p.imagen
        FROM producto p
        WHERE p.id_categoria = %s
    """, (categoria_id,))
    productos_raw= cur.fetchall()
    print(productos_raw)

    cur.execute("SELECT * FROM categoria")
    categorias_raw =cur.fetchall()
    cur.close()

    productos= []
    for producto in productos_raw:
        print(productos_raw)
        productos.append({
            'id': producto[0],
            'nombre': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'imagen': producto[5]
        })
    categorias = []
    for categoria in categorias_raw:
        categorias.append({
            'id': categoria[0],
            'nombre': categoria[1],
            'descripcion': categoria[2]
        })
    return render_template('index.html', productos=productos, categorias=categorias, categoria_selecionada=categoria_id)
  

@app.route('/buscar' , methods=['GET'])
def buscar():
    query=request.args.get('q')
    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM producto WHERE nombre_producto LIKE %s OR descripcion LIKE %s", ('%' + query + '%', '%' + query + '%'))
    productos_raw=cur.fetchall()
    cur.close()

    productos=[]
    for producto in productos_raw:
        productos.append({
            'id':producto[0],
            'nombre': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'imagen': producto[5],
        })

    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM categoria")
    categorias_raw=cur.fetchall()
    cur.close()

    categorias=[]
    for categoria in categorias_raw:
        categorias.append({
            'id': categoria[0],
            'nombre': categoria[1],
            'descripcion': categoria[2],
        })    
    return render_template('index.html', productos=productos, categorias= categorias)
     
if __name__ == '__main__':
    app.run(debug=True)