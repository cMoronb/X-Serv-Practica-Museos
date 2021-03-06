from django.shortcuts import render
from django.http import HttpResponse
from .xmlparser import getrss
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import auth
from django.contrib.auth import logout,login,authenticate
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context

from .models import Museo
from .models import Comentario
from .models import Usuario
from .models import Seleccion

# Create your views here.

FILT_ACCESIBILIDAD_POST = '''
            <form action="" Method="POST">
            <input type="submit" value="Accesibles">
</form>
'''

FILT_ACCESIBILIDAD_GET = '''
            <form action="" Method="GET">
            <input type="submit" value="Todos">
</form>
'''

FORMULARIO_COMENTARIOS = '''
            <form action="" Method="POST">
            Introduce:<br>
            <input type="text" name="comentario" placeholder="Escriba aqui su comentario...">
            <input type="submit" value="Enviar">
</form>
'''

LIKE = '''
            <form action="" Method="POST">
            <input type="hidden" name="like" value="like">
            <input type="submit" value="like" default="like">
'''

FORMULARIO_FONDO = '''<form action="" Method="POST" id="respuesta">
            <input type="submit" value="Enviar">
            </form>
            <select name="fondo" form="respuesta">
            <option value="white">Blanco</option>
            <option value="red">Rojo</option>
            <option value="aqua">Azul clarito</option>
            <option value="green">Verde</option>
            <option value="yellow">Amarillo</option>
            <option value="orange">Naranja</option>
            <option value="purple">Morado</option>
            <option value="pink">Rosa</option>
            <option value="brown">Marron</option>
            <option value="fuchsia">Fuchsia</option>
            </select>
'''

FORMULARIO_LETRA = '''
            <form action="" Method="POST">
            <input type="text" name="tamaño" placeholder="Tamaño">
            <input type="submit" value="Enviar">
</form>
'''

FORMULARIO_TITULO = '''
            <form action="" Method="POST">
            <input type="text" name="titulo" placeholder="Cambiar titulo">
            <input type="submit" value="Enviar">
</form>
'''

FORMULARIO_LOGIN = '''
            <form method="post" action="http://localhost:8000/login/">
            Username:
            <input type="text" name="usuario" placeholder="Usuario">
            <br>Password
            <input type="password" name="contraseña" placeholder="Contraseña">
            <input type="submit" value="login">
            </form>
'''

def contador(comentarios):
    lista = {}
    for comentario in comentarios:
        if comentario.museo.nombre in lista:
            lista[comentario.museo.nombre] = lista[comentario.museo.nombre] + 1
        else:
            lista[comentario.museo.nombre] = 1
    return lista

def mascomentarios(lista,museos_mostrar):
    museos = []
    iteraciones = museos_mostrar
    if len(lista) < museos_mostrar:
        iteraciones = len(lista)
    for i in range(0,iteraciones):
        aux = 0
        museo = ""
        for elemento in lista:
            if lista[elemento] >= aux:
                aux = lista[elemento]
                museo = elemento
        lista[museo] = 0
        museos.append(museo)
    return museos

def filtaccesibilidad(lista):
    aux = []
    for i in range(0,len(lista)):
        museo = Museo.objects.get(nombre=lista[i])
        if int(museo.accesibilidad) == 1:
            aux.append(lista[1])
    return aux

def getdistritos(museos):
    aux = []
    for museo in museos:
       aux.append(museo.distrito)
    aux = list(set(aux))
    return aux

def menu_filtrado(distritos):
    aux = '''<form action="" Method="POST" id="respuesta">
            <input type="submit" value="Enviar">
            </form>
            <select name="distrito" form="respuesta">
    '''
    for distrito in distritos:
        aux += '<option value="'+distrito+'">'+distrito+'</option>'
    aux += '</select>'
    return aux

def gettitulo(usuario):
    if usuario.titulo == "":
        return "Titulo de "+usario.nombre.username
    else:
        return usuario.titulo

def saltopagina(usuario,view_museos,pagina):
    selecciones = Seleccion.objects.filter(usuario_id=usuario)
    paginas = len(selecciones)
    if pagina == 0 and paginas>5:
        view_museos += '<br><a href="?'+str(pagina+1)+'">Siguiente</a>'
    else:
        view_museos += '<br><a href="?'+str(pagina-1)+'">Anterior</a>'
        aux = (paginas/5)-1
        if pagina < aux:
            view_museos += '<br><a href="?'+str(pagina+1)+'">Siguiente</a>'
    return view_museos

def identificado(request,recurso):
    view_barra = ""
    view_log = ""
    view_fondo = ""
    view_letra = ""
    view_titulo = ""
    view_coment = ""
    view_like = ""
    existe = False
    if request.user.is_authenticated():
        view_log = '<a href="http://localhost:8000/logout">Cerrar sesion</a>'
    else:
        view_log = FORMULARIO_LOGIN
    if recurso != "barra":
        view_barra = '<li><a href="http://localhost:8000">Inicio</a></li>'
    if recurso == "museo" and request.user.is_authenticated():
        view_coment = FORMULARIO_COMENTARIOS;
        selecciones = Seleccion.objects.filter(museo=request.path.split('/')[2])
        for seleccion in selecciones:
            if seleccion.usuario_id == request.user.id:
                existe = True
        if not existe:
            view_like = LIKE
    if recurso == "usuario" and request.user.is_authenticated():
        if request.user.id == int(request.path.split('/')[2]):
            view_fondo = FORMULARIO_FONDO
            view_letra = FORMULARIO_LETRA
            view_titulo = FORMULARIO_TITULO
    return view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo

@csrf_exempt
def barra(request):
    museos_mostrar = 5
    boton = FILT_ACCESIBILIDAD_POST
    view_museos = "<ul>"
    view_usuarios = '<h2 class="title">Usuarios</h2><nav><ul>'
    comentarios = Comentario.objects.all()
    usuarios = Usuario.objects.all()
    for usuario in usuarios:
        view_usuarios += '<li>'+usuario.nombre.username+'-->'+'<a href="http://localhost:8000/usuario/'+str(usuario.id)+'">'+gettitulo(usuario)+'</a></li>'
    view_usuarios += '</ul></nav>'
    lista = contador(comentarios)
    lista = mascomentarios(lista,museos_mostrar)
    if request.method == "POST":
        lista = filtaccesibilidad(lista)
        boton = FILT_ACCESIBILIDAD_GET
    for i in range(0,len(lista)):
        museo = Museo.objects.get(nombre=lista[i])
        view_museos += '<li><h2><a href="' + museo.enlace + '">'+ museo.nombre + '</a></h2><p>' + museo.direccion + '</p><footer class="more"><a href="http://localhost:8000/museos/'+str(museo.id) + '">mas info</a></footer></li>'
    view_museos += '</ul>'
    view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo = identificado(request,"barra")
    template = get_template('index.html')
    contexto = Context({'view_barra':view_barra,'view_museos':boton+'<br>'+view_museos,'view_usuarios':view_usuarios,'view_log':view_log,'view_coment':view_coment,'view_like':view_like,'view_fondo':view_fondo,'view_titulo':view_titulo,'view_letra':view_letra})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta)

@csrf_exempt
def usuario(request,usuario_id):
    if request.method == "POST":
        aux_usuario = User.objects.get(username=request.user.username)
        aux_usuario = Usuario.objects.get(nombre_id=aux_usuario)
        if "tamaño" in request.POST:
            aux_usuario.tamaño = int(request.POST['tamaño'])
        if "fondo" in request.POST:
            aux_usuario.fondo = request.POST['fondo']
        if "titulo" in request.POST:
            aux_usuario.titulo = request.POST['titulo']
        aux_usuario.save()
    pagina = request.GET.urlencode().split('=')[0]
    if pagina == "":
        pagina = 0
    else:
        pagina = int(pagina) 
    selecciones = Seleccion.objects.filter(usuario_id=usuario_id)
    selecciones = selecciones[5*int(pagina):5*int(pagina+1)]
    view_museos = '<h4>'+Usuario.objects.get(id=usuario_id).titulo+'</h4><br>'"<ul>"
    for seleccion in selecciones:
        view_museos += '<li><h2><a href="' + seleccion.museo.enlace + '">'+ seleccion.museo.nombre + '</a></h2><p>' + seleccion.museo.direccion +'</li><li>'+ str(seleccion.fecha) +'</p><footer class="more"><a href="http://localhost:8000/museos/'+str(seleccion.museo.id) + '">mas info</a></footer></li>'
    view_museos = '</ul>'+saltopagina(usuario_id,view_museos,pagina)+'<br><a href="http://localhost:8000/usuario/'+usuario_id+'/xml">Obtener XML</a>'
    view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo = identificado(request,"usuario")
    template = get_template('index.html')
    contexto = Context({'view_barra':view_barra,'view_museos':view_museos,'view_log':view_log,'view_coment':view_coment,'view_like':view_like,'view_fondo':view_fondo,'view_titulo':view_titulo,'view_letra':view_letra})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta)

@csrf_exempt
def museo(request,museo_id):
    museo = Museo.objects.get(id=museo_id)
    if request.method == "POST":
        aux_usuario = User.objects.get(username=request.user.username)
        aux_usuario = Usuario.objects.get(nombre_id=aux_usuario)
        if "like" in request.POST:
            nuevo = Seleccion(usuario=aux_usuario,museo=museo)
            nuevo.save()
        else:
            aux_comentario = request.POST['comentario']
            nuevo = Comentario(usuario=aux_usuario,comentario=aux_comentario,museo=museo)
            nuevo.save()
    comentarios = Comentario.objects.filter(museo = museo)
    view_museos = "Nombre: " + museo.nombre+"<br>"+"Direccion: "+museo.direccion+"<br>"+"Enlace: "+museo.enlace + "<br>" + "Descripcion: " + museo.descripcion + "<br>" + "Barrio: "+museo.barrio+"<br>"+"Distrito: "+museo.distrito+"<br>"+"Accesibilidad: "+museo.accesibilidad+"<br>"+"Telefono: "+museo.telefono+"<br>"+"Fax: "+museo.fax+"<br>"+"Email: "+museo.email+"<br>"
    view_museos += '<h3>Lista de comentarios</h3>'
    for comentario in comentarios:
        view_museos += '<h4>'+comentario.usuario.nombre.username+'</h4>: '+comentario.comentario+'<br>'+str(comentario.fecha)
    view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo = identificado(request,"museo")
    template = get_template('index.html')
    contexto = Context({'view_barra':view_barra,'view_museos':view_museos,'view_log':view_log,'view_coment':view_coment,'view_like':view_like,'view_fondo':view_fondo,'view_titulo':view_titulo,'view_letra':view_letra})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta)

@csrf_exempt
def museos(request):
    museos = Museo.objects.all()
    distritos = getdistritos(museos)
    menu = menu_filtrado(distritos)
    view_museos = '<ul>'
    if request.method == "POST":
        view_museos += '<h3>Museos del distrito '+request.POST['distrito']+'</h3>'
        museos = Museo.objects.filter(distrito=request.POST['distrito'])
    for museo in museos:
        view_museos += '<li><a href="http://localhost:8000/museos/'+str(museo.id)+'">'+museo.nombre+'</a></li>'
    view_museos += '</ul>'
    view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo = identificado(request,"museos")
    template = get_template('index.html')
    contexto = Context({'view_barra':view_barra,'view_museos':menu+'<br>'+view_museos,'view_log':view_log,'view_coment':view_coment,'view_like':view_like,'view_fondo':view_fondo,'view_titulo':view_titulo,'view_letra':view_letra})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta)

def update(request):
    Museo.objects.all().delete()
    getrss()
    return redirect("http://localhost:8000")

@csrf_exempt
def login(request):
    user = auth.authenticate(username=request.POST['usuario'],password=request.POST['contraseña'])
    if user is not None:
        auth.login(request,user)
    return redirect('http://localhost:8000')

def about(request):
    view_museos = ""
    view_barra,view_log,view_coment,view_like,view_fondo,view_letra,view_titulo = identificado(request,"about")
    view_museos += '<h2>Pagina de información</h2><br><li>Para ver todos los museos pincha en el enlace "Todos"</li>'
    view_museos += '<li>Para ver la pagina personal de cada usuario pincha en "Inicio" y despues en enlace de un usuario</li>'
    view_museos += '<li>Para porder disfrutar de todas las funcionalidades como añadir comentarios inicia sesion</li>'
    view_museos += '<li>Cuando hayas inicado sesion podras cambiar el color y la letra de la pagina, y guardar los museos que mas te gusten</li>'
    view_museos += '<li>En la lista de todos los museos podras filtrar por distritos</li>'
    view_museos += '<li>En la pagina principal se mostraran los museos con mas comentarios y podras filtrar por accesibilidad</li>'
    template = get_template('index.html')
    contexto = Context({'view_barra':view_barra,'view_museos':view_museos,'view_log':view_log,'view_coment':view_coment,'view_like':view_like,'view_fondo':view_fondo,'view_titulo':view_titulo,'view_letra':view_letra})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta)

def css(request):
    color = "blue"
    tamaño = "13px"
    if request.user.is_authenticated():
         aux_usuario = User.objects.get(username=request.user.username)
         aux_usuario = Usuario.objects.get(nombre_id=aux_usuario)
         color = aux_usuario.fondo
         tamaño = str(aux_usuario.tamaño)+'px'
    template = get_template('styles/layout.css')
    contexto = Context({'color': color,'letra': tamaño})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta,content_type="text/css")
    

def xml(request,usuario_id):
    selecciones = Seleccion.objects.filter(usuario_id=usuario_id)
    template = get_template('usuario.xml')
    contexto = Context({'selecciones':selecciones})
    respuesta = template.render(contexto)
    return HttpResponse(respuesta,content_type="text/xml")
