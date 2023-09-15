from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms as FForms
from django.db.models import Prefetch
from usuarios.views import verificarRedirect
from usuarios.models import Usuario, Solicitante
from .models import Seccion, Elemento, Opcion, Respuesta, RAgregacion
from .forms import RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm

from django.http import FileResponse
from reportlab.pdfgen import canvas
import io
import os
from reportlab.lib.units import cm
from reportlab.lib import utils
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.graphics.shapes import Line, Drawing
from reportlab.platypus.flowables import KeepInFrame, Flowable
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.enums import TA_CENTER


from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import HTML, CSS
import logging


#logica para crear las instancias de las forms
def crearForms(forms, opcOtro, requestPost, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante):
    for seccion in preguntasEstudio:    
            for elemento in seccion.elemento_set.all():            
                #si la pregunta no es de una opcion de las que se tiene formulario se salta esta iteracion
                if elemento.getRespuestaModel() is None:
                    continue
                formModel = formModels[elemento.getRespuestaModel()]
                esTipoUnico = seccion.tipo == Seccion.TIPOS_CHOICES[0][0]                
                #si ya existe una respuesta de esta pregunta
                if (esTipoUnico and elemento.id in respuestas) and isinstance(respuestas[elemento.id], formModel.Meta.model):                
                    forms[elemento.id] = formModel(requestPost, instance=respuestas[elemento.id], prefix=f'respuesta_{elemento.id}')
                #si no existe una respuesta de esta pregunta    
                else:     
                    #si existe una respuesta pero no coincide con el modelo de la pregunta esta se elimina para crear una nueva
                    if (esTipoUnico and elemento.id in respuestas):
                        respuestas[elemento.id].delete()           
                    forms[elemento.id] = formModel(requestPost, elemento=elemento, solicitante=solicitante, prefix=f'respuesta_{elemento.id}')
                #si son formularios de opcion se asignan las opciones
                if formModel in formModelsConOpcion:
                    choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
                    if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
                        # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
                        choices.insert(0, ("", "---------"))  
                    if elemento.opcionOtro :
                        choices.append((opcOtro.id, opcOtro.nombre) )
                    forms[elemento.id].fields['respuesta'].choices = choices

@login_required
def estudioSE(request):    
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return redirect(url)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.all().prefetch_related('elemento_set__opcion_set')    
    descargarPDF = False
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento__seccion')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)    

    '''        
    for clave, lista in registrosA.items():
        print(f"Clave: {clave}")
        print("Elementos de la lista:")
        for elemento in lista:
            print(elemento)
        print()  #'''

    #generando Forms
    #se genera un diccionario con los tipos de forms
    formModels = {}
    formModelsConOpcion = [ROpcionMultipleForm, RCasillasForm, RDesplegableForm]     
    for formtype in [RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm]:
        formModels[formtype.Meta.model] = formtype    
    
    if request.method == 'GET':  
        crearForms(forms, opcOtro, None, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
    
    if request.method == 'POST':          
        crearForms(forms, opcOtro, request.POST, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
        
        #Solo se validan y guardan las respuestas de secciones de tipo 'unico', las de 'agregacion' se omiten
        todoValido = True
        for form in forms.values():
            tipo = form.instance.elemento.seccion.tipo
            if tipo == Seccion.TIPOS_CHOICES[0][0]:
                if not form.is_valid():
                    todoValido = False
            elif tipo == Seccion.TIPOS_CHOICES[1][0]:
                form.errors.clear()                                
        
        if todoValido:
            for form in forms.values():
                if form.instance.elemento.seccion.tipo == Seccion.TIPOS_CHOICES[0][0]:
                    form.save() 
            messages.success(request, 'Estudio Socioeconómico guardado con éxito')
            #return redirect('estudioSE:estudioSE_PDF')  
            descargarPDF = True
        else:            
            for i, seccion in enumerate(preguntasEstudio):                           
                for j, elemento in enumerate(seccion.elemento_set.all()):                  
                    if elemento.id in forms and forms[elemento.id].errors:   
                        for error in forms[elemento.id].errors.values():                                             
                            messages.error(request, [f'Seccion {seccion.nombre}: Pregunta {elemento.nombre}', error])                    
            messages.warning(request, 'No se pudieron guardar los cambios: Formularios no validos')            
            

    context = {      
            'opcOtro': opcOtro,
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
            'descargarPDF': descargarPDF,
        }


    return render(request, 'solicitante/estudioSE.html', context)



@login_required
def agregarR(request, seccionID):
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.filter(id = seccionID).prefetch_related('elemento_set__opcion_set')    
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}    
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante, respuesta__elemento__seccion_id=seccionID)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)        

    #generando Forms
    #se genera un diccionario con los tipos de forms
    formModels = {}
    formModelsConOpcion = [ROpcionMultipleForm, RCasillasForm, RDesplegableForm]     
    for formtype in [RNumericoForm, RTextoCortoForm, RTextoParrafoForm, RHoraForm, RFechaForm, ROpcionMultipleForm, RCasillasForm, RDesplegableForm]:
        formModels[formtype.Meta.model] = formtype    
        
    if request.method == 'GET':  
        crearForms(forms, opcOtro, None, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)                        

    if request.method == 'POST':          
        crearForms(forms, opcOtro, request.POST, preguntasEstudio, formModels, formModelsConOpcion, respuestas, solicitante)
                    
        
        #Solo se validan y guardan las respuestas de secciones de tipo 'unico', las de 'agregacion' se omiten
        todoValido = True
        for form in forms.values():            
            if not form.is_valid():
                todoValido = False                                        
        
        if todoValido:
            rAgregacionInstance = RAgregacion.objects.create()
            for form in forms.values():     
                form.instance.rAgregacion = rAgregacionInstance
                form.save()                 
            messages.success(request, 'Registro agregado con éxito')
            return redirect('estudioSE:AgregarR', seccionID)  
        else:            
            for i, seccion in enumerate(preguntasEstudio):                           
                for j, elemento in enumerate(seccion.elemento_set.all()):                  
                    if elemento.id in forms and forms[elemento.id].errors:   
                        for error in forms[elemento.id].errors.values():                                             
                            messages.error(request, [f'Seccion {seccion.nombre}: Pregunta {elemento.nombre}', error])                    
            messages.warning(request, 'No se pudo guardar el registro: Formularios no validos')
            

    context = {     
            'mensajes' : 'mensajes.html',
            'opcOtro': opcOtro,
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
        }


    return render(request, 'solicitante/formularioBase.html', context)



@login_required
def eliminarR(request, seccionID, registroID):
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)
    
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    registroAgregacion = get_object_or_404(RAgregacion, pk=registroID)      
    respuestas = Respuesta.objects.filter(rAgregacion=registroAgregacion, solicitante=solicitante).select_subclasses()
    
    if respuestas.exists() and respuestas.first().elemento.seccion_id == seccionID:
        print(f'eliminando {seccionID} - {registroID} - {respuestas.first().getStringValue()}')
        registroAgregacion.delete()
        messages.success(request, 'Registro eliminado con exito')
        return redirect('estudioSE:AgregarR', seccionID)  
    else:
        messages.error(request, 'No se pudo eliminar el Registro')


def get_image(path, width=1*cm):
    img = utils.ImageReader(path)
    iw, ih = img.getSize()
    aspect = ih / float(iw)
    return Image(path, width=width, height=(width * aspect))

# Función para dibujar un cuadrado (marcado o no)
class Check(Flowable):
    def __init__(self, marcado=False, size=10, xOffset=-13, yOffset=2):
        super().__init__()
        self.marcado = marcado
        self.size = size
        self.yOffset = yOffset
        self.xOffset = xOffset

    def draw(self):
        if self.marcado:
            self.canv.setFillColor(colors.black)
        else:
            self.canv.setFillColor(colors.white)
        self.canv.rect(0+self.xOffset, 0+self.yOffset, self.size, self.size, fill=True)

    def __str__(self):
        return '[]'

@login_required
def getEstudioPDF(request):        
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)

    ###########OBtener informacion ###############
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.all().prefetch_related('elemento_set__opcion_set')    
    descargarPDF = False
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento__seccion')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta    
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)    

    for seccion in preguntasEstudio:
        for elemento in seccion.elemento_set.all():
            pass
            #print(f'{elemento} --- {any(elemento.tipo == choice[0] for choice in Elemento.TIPO_CHOICES[6:])}')

    '''
    if formModel in formModelsConOpcion:
        choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
        if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
            # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
            choices.insert(0, ("", "---------"))  
        if elemento.opcionOtro :
            choices.append((opcOtro.id, opcOtro.nombre) )
        forms[elemento.id].fields['respuesta'].choices = choices '''



    ########## Estilos #########
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="EstudioSocioeconomico.pdf"'
    #response['Content-Disposition'] = 'attachment; filename="EstudioSocioeconomico.pdf"'  # Cambia 'inline' a 'attachment'
    # Crear un objeto PDF
    marginX = 30
    marginY = 30
    doc = SimpleDocTemplate(response, pagesize=letter, topMargin=marginY, bottomMargin=marginY, leftMargin=marginX, rightMargin=marginX)
    contenido = []
    styles = getSampleStyleSheet()
    '''
    'Normal': Estilo de párrafo normal.
    'Heading1': Encabezado de nivel 1.
    'Heading2': Encabezado de nivel 2.
    'Heading3': Encabezado de nivel 3.
    'Heading4': Encabezado de nivel 4.
    'Heading5': Encabezado de nivel 5.
    'Heading6': Encabezado de nivel 6.
    'Title': Título principal del documento.
    'Subtitle': Subtítulo del documento.
    'BodyText': Estilo de texto del cuerpo del documento.
    'Bullet': Estilo para listas con viñetas.
    'Definition': Estilo para definiciones. '''

    styles['Normal'].fontSize = 12
    estiloNormalCentrado = styles['Normal'].clone(name='MiEstilo')
    estiloNormalCentrado.alignment = TA_CENTER

    estiloNormalCentradoSM = styles['Normal'].clone(name='MiEstilo')
    estiloNormalCentradoSM.fontSize = 10
    estiloNormalCentradoSM.alignment = TA_CENTER
    

    ##########Construccion del documento ##########

    #Creando titulo    
    logo = get_image('static/images/LogoCozcyt.png', 10*cm)
    contenido.append(logo)
    contenido.append(Spacer(1, 10))
    
    titulo = Paragraph("Formato para Estudio Socioeconómico", styles['Title'])
    contenido.append(titulo)
    contenido.append(Spacer(1, 15))

    # Definir el estilo de la tabla
    estiloTablaNormal = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),  # Fondo gris para la fila de encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Letras blancas en la fila de encabezado
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para la fila de encabezado
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Fondo blanco para el cuerpo de la tabla
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para el cuerpo de la tabla        
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Habilitar el ajuste de línea automático
        ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Padding izquierdo de 10 puntos
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding derecho de 10 puntos
        ('TOPPADDING', (0, 0), (-1, -1), 5),  # Padding superior de 5 puntos
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Padding inferior de 5 puntos    
    ])
    estiloTablaSeparador = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),  # Fondo gris oscuro para la fila de encabezado        
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Letras blancas en la fila de encabezado
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fuente en negrita para la fila de encabezado
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Fondo blanco para el cuerpo de la tabla
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Fuente normal para el cuerpo de la tabla        
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Habilitar el ajuste de línea automático
        ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Padding izquierdo de 10 puntos
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Padding derecho de 10 puntos
        ('TOPPADDING', (0, 0), (-1, -1), 5),  # Padding superior de 5 puntos
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Padding inferior de 5 puntos    
    ])      
    estiloTablaOpciones = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),           
        ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Padding izquierdo de 10 puntos
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Padding derecho de 10 puntos
        ('TOPPADDING', (0, 0), (-1, -1), 0),  # Padding superior de 5 puntos
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Padding inferior de 5 puntos    
    ])                                        
    ancho_tabla = 550 

    # Iterar a través de las secciones y elementos    
    for seccion in preguntasEstudio:
        if seccion.tipo == 'agregacion':
            contenido.append(Paragraph(seccion.nombre, styles['Heading2']))
        else:
            contenido.append(Paragraph(seccion.nombre, styles['Heading2']))            
            data = []
            eObjs = []
            headers = []
            body = []
            ultimoRow = None
            for elemento in seccion.elemento_set.all():                                
                if elemento.row != ultimoRow and ultimoRow is not None:
                    data.append(headers)
                    for eObj in eObjs:
                        if eObj is not None:
                            respuesta = respuestas[eObj.id]
                            if any(eObj.tipo == choice[0] for choice in Elemento.TIPO_CHOICES[6:]):
                                opcioness = [[]]
                                opcion = Table([[Check(True, size=8),"aaa"]], style=estiloTablaOpciones)
                                opcioness[0].append(opcion)      
                                opcion = Table([[Check(True, size=8),"aaa"]], style=estiloTablaOpciones)
                                opcioness[0].append(opcion)   
                                opcion = Table([[Check(True, size=8),"aaa"]], style=estiloTablaOpciones)
                                opcioness[0].append(opcion)                             
                                
                                body.append(Table(opcioness, style=estiloTablaOpciones))
                            else:
                                body.append(Paragraph(respuesta.getStringValue(), estiloNormalCentradoSM))
                        else:
                            body.append(None)
                    if len(body) > 0 and any(resp is not None for resp in body):
                        data.append(body)
                        st = estiloTablaNormal
                    else :
                        st = estiloTablaSeparador
                    tabla = Table(data, colWidths=[ancho_tabla / len(data[0])] * len(data[0]))
                    tabla.setStyle(st)                
                    contenido.append(tabla)
                    data = []
                    eObjs = []
                    headers = []
                    body = []
                if elemento.tipo == 'separador':
                    headers.append(Paragraph(elemento.nombre, estiloNormalCentradoSM)) 
                    eObjs.append(None)                   
                else:                    
                    headers.append(Paragraph(elemento.nombre, estiloNormalCentradoSM))                                        
                    eObjs.append(elemento)                   
                ultimoRow = elemento.row
            # Crear una tabla para los elementos de la sección
            

    contenido.append(Spacer(1, 15))
    textoFinal = '<font color="red"><b>NOTA:</b></font> El proporcionar información falsa es motivo suficiente para anular el trámite. El COZCyT se reserva el derecho de investigar la veracidad de lo antes declarado.' \
        '<br/><br/>' \
        f'<b>{solicitante.nombre} {solicitante.ap_paterno} {solicitante.ap_materno}</b>' \
        '<br/><br/>' \
        '<u>'+ '&nbsp;' * 60 +'</u> ' \
        '<br/><br/>' \
        '<b>Firma del (a) Estudiante</b>' \
        '<br/><br/>' \
        'Manifiesto que la información proporcionada es verídica y de buena fe. De caso contrario me atendré a las sanciones correspondientes.'
    contenido.append(Paragraph(texto, estiloNormalCentrado))
    contenido[-1].keepWithNext = True

    # Función para agregar números de página
    def agregar_numero_pagina(canvas, doc):
        numero_pagina = canvas.getPageNumber()
        total_paginas = doc.page
        texto = "Página %d de %d" % (numero_pagina, total_paginas)
        canvas.drawString(525, 15, texto)

    # Construir el PDF
    doc.build(contenido, onFirstPage=agregar_numero_pagina, onLaterPages=agregar_numero_pagina)
    return response




@login_required
def getEstudioPDF2(request):        
    url = verificarRedirect(request.user)    
    if url:          #Verifica si el usuario ha llenaodo su informacion personal por primera vez y tiene los permisos necesarios
        return HttpResponse("", status=401)

    ###########OBtener informacion ###############
    solicitante = get_object_or_404(Solicitante, pk=request.user.id)  
    #obtener los formularios del estudio SE # filter(tipo='unico', nombre='Prueba') 
    preguntasEstudio = Seccion.objects.all().prefetch_related('elemento_set__opcion_set')    
    descargarPDF = False
    forms = {}   
    opcOtro = get_object_or_404(Opcion, nombre = "Otro")
    #se obtienen e indexan las respuestas existentes del usuario
    respuestas = {}
    respuestasExistentes = Respuesta.objects.filter(solicitante = solicitante).select_subclasses().select_related('elemento__seccion')
    for respuesta in respuestasExistentes:        
        respuestas[respuesta.elemento_id] = respuesta    
    
    rAgregacion =RAgregacion.objects.filter(respuesta__solicitante_id=solicitante)\
        .distinct()\
        .prefetch_related('respuesta_set')       

    registrosA = {}
    raSeccion = -1
    for ra in rAgregacion:                
        registros = ra.respuesta_set.all().select_subclasses().select_related('elemento__seccion')
        first = registros.first()
        if first:
            sID = first.elemento.seccion_id        
        if sID != raSeccion:
            raSeccion = sID
            registrosA[raSeccion] = []
        registrosA[raSeccion].append(registros)    

    for seccion in preguntasEstudio:
        for elemento in seccion.elemento_set.all():
            pass
            #print(f'{elemento} --- {any(elemento.tipo == choice[0] for choice in Elemento.TIPO_CHOICES[6:])}')

    '''
    if formModel in formModelsConOpcion:
        choices = [(opcion.id, opcion.nombre) for opcion in elemento.opcion_set.all()]                
        if isinstance(forms[elemento.id].fields['respuesta'].widget, FForms.Select):
            # Agrega la opción en blanco al comienzo solo si el campo es un 'select'
            choices.insert(0, ("", "---------"))  
        if elemento.opcionOtro :
            choices.append((opcOtro.id, opcOtro.nombre) )
        forms[elemento.id].fields['respuesta'].choices = choices '''

    template = get_template('solicitante/pdfTemplate.html')
    context = {               
            'solicitante': solicitante,
            'opcOtro': opcOtro,
            'forms': forms,            
            'preguntasEstudio': preguntasEstudio,   
            'registrosA': registrosA,
            'descargarPDF': descargarPDF,
        }

    logger = logging.getLogger('weasyprint')
    logger.addHandler(logging.FileHandler('./weasyprint.log'))
    # Renderiza el template con los datos
    html_content = template.render(context)

    css_bootstrap_grid = os.path.join(settings.BASE_DIR, "static/css/bootstrap-grid.css")    
    css_main = os.path.join(settings.BASE_DIR, "static/css/main.css")   
    css_FA = os.path.join(settings.BASE_DIR, "static/css/font-awesome.css")   
    # Crea un objeto HTML a partir del contenido HTML
    html = HTML(string=html_content, base_url=request.build_absolute_uri())
    print('aaaaaa')
    # Genera el PDF
    pdf_file = html.write_pdf(stylesheets=[CSS(css_bootstrap_grid), CSS(css_main), CSS(css_FA)])
    print('bbbbbbbbbb')
    # Devuelve el PDF como una respuesta HTTP
    response = HttpResponse(pdf_file, content_type='application/pdf')
    #response['Content-Disposition'] = 'filename="mi_pdf.pdf"'
    response['Content-Disposition'] = 'inline; filename="EstudioSocioeconomico.pdf"'
    return response