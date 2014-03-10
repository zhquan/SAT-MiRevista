from django.db import models
import datetime
from django.utils.translation import ugettext_lazy as _
# Create your models here.
class Notices(models.Model):
    Title = models.CharField(max_length = 50)
    DateNow = models.DateTimeField(auto_now_add=True)
    Date = models.DateTimeField(_('date published'), default=datetime.datetime.now)
    Link = models.CharField(max_length = 50)
    Content = models.TextField()
    Canal = models.TextField()
    User = models.CharField(max_length = 50)
    Puntuar = models.IntegerField()
    Comentar = models.TextField()

class Channels(models.Model):
    Title = models.CharField(max_length = 50)
    Date = models.DateTimeField(_('date published'), default=datetime.datetime.now)
    Logo = models.CharField(max_length = 50)
    RSS = models.TextField()
    Url = models.TextField()
    NumMensaje = models.IntegerField()

class CanalesNum(models.Model):
    CanalId = models.CharField(max_length = 50)
    Titular = models.CharField(max_length = 50)
    Titulo = models.CharField(max_length = 50)
    Link = models.TextField()
    Date = models.DateTimeField(_('date published'), default=datetime.datetime.now)
    Descripcion = models.TextField()

class UserCss(models.Model):
    User = models.CharField(max_length = 50)
    Color = models.CharField(max_length = 50)
    Fondo = models.TextField()
    ColorTitulo = models.CharField(max_length = 50)
    FondoTitulo = models.TextField()
    SizeTitulo = models.CharField(max_length = 50)
    SizeTexto = models.CharField(max_length = 50)
    CopyColor = models.CharField(max_length = 50)
    CopySize = models.CharField(max_length = 50)

class Revista(models.Model):
    User = models.CharField(max_length = 50)
    Title = models.CharField(max_length = 50)
    Date = models.DateTimeField(auto_now=True)
