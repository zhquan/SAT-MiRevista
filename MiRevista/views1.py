from django.http import HttpResponse,HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from models import UserCss, Notices, Channels, Revista
from django.contrib.auth.models import User
import urllib2
from django import *
from django.http import *
from django.db import *
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render_to_response
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
#from django.forms import widgets
import feedparser
import datetime
import rfc822
import time
import calendar
from bs4 import BeautifulSoup
import urllib

def ordenar(lista):
    max_list = len(lista)
    x = 0
    while x < max_list:
        y = 0
        while y < max_list:
            if (lista[x].Date > lista[y].Date):
                aux1 = lista[x]
                aux2 = lista[y]
                lista[x] = aux2
                lista[y] = aux1
            y = y+1
        x = x+1
    return lista

def ordenarDateNow(lista):
    max_list = len(lista)
    x = 0
    while x < max_list:
        y = 0
        while y < max_list:
            if (lista[x].DateNow > lista[y].DateNow):
                aux1 = lista[x]
                aux2 = lista[y]
                lista[x] = aux2
                lista[y] = aux1
            y = y+1
        x = x+1
    return lista
#################################### HOME #########################################################################
def home(request):
    page = ""    
    color = ""
    fondo = "white"
    colorTitulo = "black"
    fondoTitulo = "white"
    sizeTitulo = ""
    sizeTexto = ""
    if request.user.is_authenticated():
        # Para saber si el usuario tiene ya guardado un css propio
        try:
            T_css = UserCss.objects.get(User = request.user.username)
            color = T_css.Color
            fondo = T_css.Fondo
            colorTitulo = T_css.ColorTitulo
            fondoTitulo = T_css.FondoTitulo
            sizeTitulo = T_css.SizeTitulo
            sizeTexto = T_css.SizeTexto
        except UserCss.DoesNotExist:
            color = ""
    #Bucle cogiendo el Date como identificador de cada noticias y guardarlo para ordenar
    id_max = Revista.objects.all()
    ordena = []
    for N_Date in id_max:
        ordena.append(Revista.objects.get(Date = N_Date.Date))
    lista = ordenar(ordena)
    for N_Date in lista[:]:
        T_Revista = Revista.objects.get(Date = N_Date.Date)
        Titulo = str(T_Revista.Title)
        page += '<h2><a href=http://localhost:1234/'+T_Revista.User+'>'+Titulo+"</a></h2><h3>Autor: "+str(T_Revista.User) + "</h3> Fecha de la ultima actualizacion: " + str(T_Revista.Date)+"<br>"
    dic = {'fondo': fondo, 'color': color, 'fondoTitulo': fondoTitulo, 'colorTitulo': colorTitulo, 'sizeTitulo': sizeTitulo, 'sizeTexto': sizeTexto}
    dic.update(csrf(request))
    css = render_to_response('style.css', dic)
    dic2 = {'css':css, "page": page, "user": request.user.username}
    dic2.update(csrf(request))
    return render_to_response('index.html',dic2)
################################ PROFILE #####################################################
def profile(request):
    return HttpResponseRedirect("http://localhost:1234/")
#################################### REGISTER ###########################################################################
@csrf_exempt
def register (request):
    path = request.body
    solution = path.split("=")
    username= solution[1].split("&")[0]
    title = solution[2].split("&")[0]
    if title == "":
        title = "Revista de "+username
    email = solution[3].split("&")[0]
    email = email.split("%40")[0]+'@'+email.split("%40")[1]
    password = solution[4]
    existe = False
    # Registrarte con username, email, password
    try: 
        user = User.objects.create_user(username, email, password)
        existe = True
    except IntegrityError:
        existe = False
    # Crear un nuevo usuario
    if existe:
        T_Revista = Revista(User = username, Title = title)
        T_Revista.save()
    # Cambiar el titulo
    else:
        try:
            T_Revista = Revista.objects.get(User = username)
            T_Revista.Title = title
        except Revista.DoesNotExist:
            T_Revista = Revista(User = username, Title = title)
        T_Revista.save()
    return HttpResponseRedirect("http://localhost:1234/")
#################################### USUARIO ###################################################################
@csrf_exempt
def usuario(request, resource):
    page = ""
    autenticado = ""
    fondo = "white"
    color = ""
    colorTitulo = "black"
    fondoTitulo = "white"
    sizeTitulo = ""
    sizeTexto = ""
    try:
        T_revista = Revista.objects.get(User = resource)
        titular = T_revista.Title
    except Revista.DoesNotExist:
        return HttpResponse("No existe la revista para este usuario")
    # si esta autenticado y es el usuario autenticado
    if request.user.is_authenticated() & (request.user.username == resource):
        autenticado = "si"
        try:
            T_css = UserCss.objects.get(User = request.user.username)
            color = T_css.Color
            fondo = T_css.Fondo
            colorTitulo = T_css.ColorTitulo
            fondoTitulo = T_css.FondoTitulo
            sizeTitulo = T_css.SizeTitulo
            sizeTexto = T_css.SizeTexto
        except UserCss.DoesNotExist:
            color = ""
            
    Noticias = Notices.objects.all()
    ordena = []
    for N_noticias in Noticias:
        # Seleccionar los mensajes de este Usuario
        if (N_noticias.User == resource):
            ordena.append(Notices.objects.get(DateNow = N_noticias.DateNow))
    # Ordena por orden de DateNow
    lista = ordenarDateNow(ordena)
    for N_lista in lista[:]:
        if (N_lista.User == resource):
            titulo = N_lista.Title
            link = N_lista.Link
            noticia = N_lista.Content
            canal = N_lista.Canal
            punto = N_lista.Puntuar
            comentario = N_lista.Comentar
            # Para saber a que canal corresponde de /canales/id
            canalid = Channels.objects.get(Title = canal)
            date = N_lista.Date
            if request.user.is_authenticated() & (request.user.username == resource):
                page += '<h2><a href="'+link+'">'+titulo +"</a></h2>publicado en "+ str(date) +'<br>elegida en '+ str(N_lista.DateNow) + '<br><h4>'+ noticia+'</h4><a href="http://localhost:1234/canales/'+str(canalid.id)+'">'+canal+'</a><br>Puntuacion: '+str(punto)+'<br>Comentarios '+comentario+'<br><br>'
            else:
                page += '<h2><a href="'+link+'">'+titulo +"</a></h2>publicado en "+ str(date) +'<br>elegida en '+ str(N_lista.DateNow) + '<br><h4>'+ noticia+'</h4><a href="http://localhost:1234/canales/'+str(canalid.id)+'">'+canal+'</a><br>Puntuacion: '+str(punto)+'<br>Comentarios:<br>'+comentario
                page += '</a><form action="" method="POST">'
                page += '<input type="text" name="comenta" value="" id="comenta">'
                page += '<input type="hidden" name="noticia" value="'+str(N_lista.id)+'">'
                page += '<input type="submit" value="Comentar"></form>'
                page += '<form action="" method="POST">'
                page += '<input type="hidden" name="noticia" value="'+str(N_lista.id)+'"><select name="puntua">'
                page += '<option value="-1">-1</option>'
                page += '<option value="1">1</option></select>'
                page += '<input type="submit" value="Calificar">'
                page += '</form> <br><br>'
    if request.method == 'POST':       
        if request.user.username == resource:
            autenticado = "si"
            fondo = request.body.split("fondo=")[1].split("&")[0].replace("%2F","/").replace("%3A", ":")
            fondoTitulo = request.body.split("fondoTitulo=")[1].split("&")[0].replace("%2F","/").replace("%3A", ":")
            # para saber si es una URL o color
            try:
                url = fondo.split("http://")[1]
                fondo = "url("+fondo+")"
            except IndexError:
                fondo = fondo
            try:
                url2 = fondoTitulo.split("http://")[1]
                fondoTitulo = "url("+fondoTitulo+")"
            except IndexError:
                fondoTitulo = fondoTitulo
            color = request.body.split("color=")[1].split("&")[0]
            colorTitulo = request.body.split("colorTitulo=")[1].split("&")[0]
            sizeTitulo = request.body.split("sizeTitulo=")[1].split("&")[0]
            sizeTexto = request.body.split("sizeTexto=")[1].split("&")[0]
            try:
                T_css = UserCss.objects.get(User = request.user.username)
                if color != "":
                    T_css.Color = color
                else:
                    color = T_css.Color
                if fondo != "":
                    T_css.Fondo = fondo
                else:
                    fondo = T_css.Fondo
                if colorTitulo != "":
                    T_css.ColorTitulo = colorTitulo
                else:
                    colorTitulo = T_css.ColorTitulo
                if fondoTitulo != "":
                    T_css.FondoTitulo = fondoTitulo
                else:
                    fondoTitulo = T_css.FondoTitulo
                T_css.SizeTitulo = sizeTitulo
                T_css.SizeTexto = sizeTexto
            except UserCss.DoesNotExist:
                T_css = UserCss(User = request.user.username, Color = color, Fondo = fondo, ColorTitulo = colorTitulo, FondoTitulo = fondoTitulo, SizeTitulo = sizeTitulo, SizeTexto = sizeTexto)
            T_css.save()
        else:
            respuesta = request.body.replace("+", " ").replace("%3A", ":")
            try:
                ID = respuesta.split("noticia=")[1].split("&")[0]
            except:
                ID = respuesta.split("noticia=")[1]
            print ID
            puntua = False
            comentar = False
            try:
                punto = respuesta.split("puntua=")[1]
                puntua = True
            except:
                comenta = respuesta.split("comenta=")[1].split("&")[0]
                comentar = True
            if puntua:
                T_noticia = Notices.objects.get(id = ID)
                T_noticia.Puntuar = T_noticia.Puntuar + int(punto)
                T_noticia.save()
            elif comentar:
                T_noticia = Notices.objects.get(id = ID)
                T_noticia.Comentar = T_noticia.Comentar + request.user.username + ': ' + comenta + '<br>'
                T_noticia.save()
    elif (request.method != 'GET')&(request.method != 'PUT'):
        return HttpResponse("Solo se admiten los metodos GET y POST")
    dic = {'fondo': fondo, 'color': color, 'fondoTitulo': fondoTitulo, 'colorTitulo': colorTitulo, 'sizeTitulo': sizeTitulo, 'sizeTexto': sizeTexto}
    dic.update(csrf(request))
    css = render_to_response('style.css', dic)
    dic2 = {'css':css, 'page': page, 'user':resource, 'autenticado': autenticado, 'titular': titular}
    dic2.update(csrf(request))
    return render_to_response('user.html',dic2)
################################ RSS #########################################################
def RSS(request, resource):
    try:
        T_revista = Revista.objects.get(User = resource)
        titular = T_revista.Title
        fecha = T_revista.Date
        descripcion = "Esta es la revista de "+resource
        linkP = "http://localhost:1234/"+resource+"/rss"
    except Revista.DoesNotExist:
        return HttpResponse("No existe la revista para este usuario")

    page = ""
    Noticias = Notices.objects.all()
    ordena = []
    for N_noticias in Noticias:
        # Seleccionar los mensajes de este Usuario
        if (N_noticias.User == resource):
            ordena.append(Notices.objects.get(DateNow = N_noticias.DateNow))
    lista = ordenarDateNow(ordena)
    # Creacion del RSS
    for N_lista in lista[:]:
        if (N_lista.User == resource):
            titulo = N_lista.Title
            link = N_lista.Link
            noticia = N_lista.Content.replace("&nbsp;", "")
            canal = N_lista.Canal
            date = N_lista.Date
            page+='<item>\n'
            page+='<title>'+titulo+'</title>\n'
            page+='<description>'+noticia+'</description>\n'
            page+='<link>'+link+'</link>\n'
            page+='<guid>unique string per item</guid>\n'
            page+='<pubDate>'+str(date)+'</pubDate>\n'
            page+='</item>\n'
            print date
    dic = {'titular': titular, 'descripcion': descripcion, 'link': linkP, 'fecha': fecha, 'page': page}
    dic.update(csrf(request))
    return render_to_response('mirevista.rss', dic)

################################# AYUDA ######################################################
def ayuda(request):
    fondo = "white"
    color = ""
    colorTitulo = "black"
    fondoTitulo = "white"
    sizeTitulo = ""
    sizeTexto = ""
    if request.user.is_authenticated():
        try:
            T_css = UserCss.objects.get(User = request.user.username)
            color = T_css.Color
            fondo = T_css.Fondo
            colorTitulo = T_css.ColorTitulo
            fondoTitulo = T_css.FondoTitulo
            sizeTitulo = T_css.SizeTitulo
            sizeTexto = T_css.SizeTexto
        except UserCss.DoesNotExist:
            color = ""
    dic = {'fondo': fondo, 'color': color, 'fondoTitulo': fondoTitulo, 'colorTitulo': colorTitulo, 'sizeTitulo': sizeTitulo, 'sizeTexto': sizeTexto}
    dic.update(csrf(request))
    css = render_to_response('style.css', dic)
    dic2 = {'css':css, 'user': request.user.username}
    dic2.update(csrf(request))
    return render_to_response('help.html', dic2)

################################ GUARDAR ########################################################
def guardar(RSS, resource, num, usuario):
    if resource == "rss":
        rss = RSS
    else:
        rss = resource
    try:
        d = feedparser.parse(rss)
        Rss = True
    except UnboundLocalError:
        Rss = False
    if Rss:
        title = d.feed.title
        url = d.feed.link
        Num_Mensaje = len(d.entries)
        try:
            logo = '<img src="'+d.feed.image.href+'">'
        except:
            logo = ""
        date = d.feed.published
        date = datetime.datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(date)))
        try:
            T_Canal = Channels.objects.get(Title = title)
            T_Canal.Logo = logo
            T_Canal.RSS = rss
            T_Canal.Date = date
            T_Canal.Url = url
            T_Canal.NumMensaje = Num_Mensaje
        except Channels.DoesNotExist:
            T_Canal = Channels(Title = title, Logo = logo, RSS = rss, Date = date, Url = url, NumMensaje = Num_Mensaje)
        T_Canal.save()
        for N_noticia in d.entries:
            titulo = N_noticia.title
            link = N_noticia.link
            date = N_d.published
            date = datetime.datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(date)))
            descripcion = N_d.description
            titular = d.feed.title
            try:
                T_num = CanalNum.objects.get(Titulo = titulo, Titular = titular)
                T_num.Link = link
                T_num.Date = date
                T_num.Descripcion = descripcion
            except CanalNum.DoesNotExist:
                T_num = CanalNum(Titulo = titulo, Titular = titular, Link = link, Date = date, Descripcion = descripcion)
            T_num.save()
        try:
            T_Num = CanalNum.objects.get()
    if resource != "rss":
        return HttpResponseRedirect("http://localhost:1234/canales/"+num)
################################## CANALES ##########################################################################
@csrf_exempt
def canales(request):
    page = ""
    autenticado = ""
    color = ""
    fondo = "white"
    colorTitulo = "black"
    fondoTitulo = "white"
    sizeTitulo = ""
    sizeTexto = ""
    try:
        canal = Channels.objects.all()
        # Lista de canales
        for N_canal in canal:
            page += '<h2><a href="http://localhost:1234/canales/'+str(N_canal.id)+'">'+N_canal.Title + '</a></h2><h3>' + str(N_canal.NumMensaje) +' mensajes disponibles</h3>'+ N_canal.Logo + str(N_canal.Date) +'<br>'
    except Channels.DoesNotExist:
        page = "Aun no hay canales disponibles"

    if request.user.is_authenticated():
        autenticado = "Si"
        try:
            T_css = UserCss.objects.get(User = request.user.username)
            color = T_css.Color
            fondo = T_css.Fondo
            colorTitulo = T_css.ColorTitulo
            fondoTitulo = T_css.FondoTitulo
            sizeTitulo = T_css.SizeTitulo
            sizeTexto = T_css.SizeTexto
        except UserCss.DoesNotExist:
            color = ""
        if request.method == "POST":
            path = request.body
            separar = path.split("=")
            try:
                rss = separar[1].split("&")[0].replace("%2F","/").replace("%3A", ":")
            except IndexError:
                rss = separar[1].split("&")[0]
            guardar(rss, "rss", "", request.user)
        if (request.method != 'GET') & (request.method != 'POST'):
            return HttpResponse("Solo se admiten los metodos GET y POST")
    dic = {'fondo': fondo, 'color': color, 'fondoTitulo': fondoTitulo, 'colorTitulo': colorTitulo, 'sizeTitulo': sizeTitulo, 'sizeTexto': sizeTexto}
    dic.update(csrf(request))
    css = render_to_response('style.css', dic)
    dic2 = {'css':css, "page": page, "autenticado":autenticado, 'user':request.user.username}
    dic2.update(csrf(request))
    return render_to_response('channel.html',dic2)
################################ CANALES/NUM ############################################################################
@csrf_exempt
def CanalNum(request, resource):
    canal = Channels.objects.all()
    page = ""
    autenticado = ""
    color = ""
    fondo = "white"
    colorTitulo = "black"
    fondoTitulo = "white"
    sizeTitulo = ""
    sizeTexto = ""
    if request.user.is_authenticated():
        usuario = request.user
        autenticado = "Si"
        try:
            T_css = UserCss.objects.get(User = request.user.username)
            color = T_css.Color
            fondo = T_css.Fondo
            colorTitulo = T_css.ColorTitulo
            fondoTitulo = T_css.FondoTitulo
            sizeTitulo = T_css.SizeTitulo
            sizeTexto = T_css.SizeTexto
        except UserCss.DoesNotExist:
            color = ""
        if request.method == "GET":
            for N_canal in canal:
                if str(N_canal.id) == resource:
                    # Crear la lista completa de noticias desde el canal RSS
                    d = feedparser.parse(N_canal.RSS)
                    titulares = '<form action="" method = "post"><h3>'
                    for N_title in d.entries:
                        titulares += '<p><input type="checkbox" name="'+N_canal.RSS+'" value="'+N_title.link+'"/><a href="'+N_title.link+'">'+N_title.title+'</a></p>'
                    titulares += '</h3><input type="submit" value="Add" /></form>'
                    # composicion de page
                    title = '<h2><a href="'+N_canal.Url+'">'+N_canal.Title+'</a></h2>'
                    canal = '<h4><a href="'+N_canal.RSS+'">(canal)</a></h4>'
                    # Actualiza pasando el Rss, id, usuario a la funcion guardar
                    actualizar = '<h3><a href="http://localhost:1234/canales/guardar/'+N_canal.RSS+'/'+str(N_canal.id)+'/'+str(usuario)+'">Actualizar</a></h3>'
                    page += title + canal + actualizar + N_canal.Logo + str(N_canal.Date) + titulares + "<br>"
                else:
                    titulo = '<h4><a href="http://localhost:1234/canales/'+str(N_canal.id)+'">'+N_canal.Title+'</a></h4>'
                    page += titulo + '<br>'
        elif request.method == "POST":
            respuesta = request.body.replace("%3A", ":").replace("%2F", "/").split("&")
            for i in respuesta[:]:
                i = i.split("=")
                rss = i[0]
                link = i[1]
                d = feedparser.parse(rss)
                for N_d in d.entries:
                    if (link == N_d.link):
                        date = N_d.published
                        date = datetime.datetime.fromtimestamp(calendar.timegm(rfc822.parsedate(date)))
                        notice = N_d.description
                        title = N_d.title
                Noticias = Notices.objects.all()
                ordena = []
                for N_noticias in Noticias:
                    # Para saber sacar las noticias de ese usuario
                    if (N_noticias.User == request.user.username):
                        ordena.append(Notices.objects.get(DateNow = N_noticias.DateNow))
                lista = ordenarDateNow(ordena)
                # Mirar si hay mas de 10 o no
                if len(lista) > 9:
                    # Seleccionar el mas antiguo y coger su titulo para reemplazarlo
                    rm_title = lista[9].Title
                    for N_user in lista[:]:
                        if N_user.Title == rm_title:
                            N_user.delete()
                            N_user = Notices(Title = title, Link = link, Content = notice, Canal = d.feed.title, Date = date, User = request.user.username, Comentar = "", Puntuar = 0)
                            N_user.save()
                else:
                    try:
                        T_noticia = Notices.objects.get(Title = title, User = request.user.username)
                        T_noticia.Link = link
                        T_noticia.Content = notice
                        T_noticia.Canal = d.feed.title
                        T_noticia.Date = date
                        T_noticia.Puntuar = 0
                        T_noticia.Comentar = ""
                    except Notices.DoesNotExist:
                        T_noticia = Notices(Title = title, Link = link, Content = notice, Canal = d.feed.title, Date = date, User = request.user.username, Comentar = "", Puntuar = 0)
                    T_noticia.save()
                # Actualizar la fecha de la revista
                revista = Revista.objects.all()
                for N_revista in revista:
                    if (request.user.username == N_revista.User):
                        N_revista.save()
            return HttpResponseRedirect("http://localhost:1234/canales/"+resource)
        else:
            return HttpResponse("Solo se admiten los metodos GET y POST")
    dic = {'fondo': fondo, 'color': color, 'fondoTitulo': fondoTitulo, 'colorTitulo': colorTitulo, 'sizeTitulo': sizeTitulo, 'sizeTexto': sizeTexto}
    dic.update(csrf(request))
    css = render_to_response('style.css', dic)
    dic2 = {'css':css, "page": page, "autenticado":autenticado, 'user':request.user.username}
    dic2.update(csrf(request))
    return render_to_response('channel.html',dic2)
