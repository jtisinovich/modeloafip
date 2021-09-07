import requests
import pandas as pd
import threading
from flask import Flask, render_template, request

app = Flask(__name__)


    
a=[]

url = "https://afip.tangofactura.com/Rest/GetContribuyenteFull?cuit="
headers = {"Cache_Control":"no-cache"}

resultados = []
def get_data(CUIT):
    
    try:
        response = requests.request("GET", url+CUIT,headers=headers)
        AFIP_json = response.json()
        impuestos = pd.DataFrame(AFIP_json)
        impuestos.drop(columns="errorGetData", inplace=True)
        impuestos.dropna(inplace=True)
        print("Correcto")
        if len(impuestos.Contribuyente.ErroresObteniendoDatos) > 0:
            return
        
        global a
        a.append(impuestos)
        #time.sleep(0.7)
        return 
    
        
    except:
        return
    
def consultabaseapoc(cuit):
    with open('FacturasApocrifas.txt') as f:
        if cuit in f.read():
            return True
        else:
            return False



#loop = asyncio.get_event_loop()


@app.route('/')
def principal():

    
    return render_template('principal.html',
                           passstatic_url_path='/static')


@app.route('/apocindividual', methods = ["POST"])
def apocindividual():
    cuit = request.form["cuit"]
    resultado = consultabaseapoc(cuit)
    if resultado:
        mensaje = "La cuit " + str(cuit) + " se encuentra incluídad dentro de la base APOC"
        
        return render_template("error.html", error=mensaje)
    else:
        mensaje = "La cuit " + str(cuit) + " NO se encuentra incluídad dentro de la base APOC"
        
        return render_template("error.html", error=mensaje)




    

@app.route('/individual', methods = ["POST"])
def individual():
    cuit = request.form["cuit"]
    
    try:
        response = requests.request("GET", url+cuit,headers=headers)
        AFIP_json = response.json()

        data = pd.DataFrame(AFIP_json)
    except:
        error = "Error Obteniendo Datos"
        return render_template("error.html", error=error)
    
    data.drop(columns="errorGetData", inplace=True)
    data.dropna(inplace=True)
    
     
    if len(data.Contribuyente.ErroresObteniendoDatos) > 0:
        error = data.Contribuyente.ErroresObteniendoDatos
        
        return render_template("error.html", error=error)
    
    nombre=data.Contribuyente.nombre
    domFiscal=data.Contribuyente.domicilioFiscal["direccion"]
    provincia = data.Contribuyente.domicilioFiscal["nombreProvincia"]
    codpostal=data.Contribuyente.domicilioFiscal["codPostal"]
    actividades = data.Contribuyente.ListaActividades
    idactividad=actividades[0]["idActividad"]
    descactividad=actividades[0]["descActividad"]
    activ = str(idactividad) + " " + descactividad
    impuestos = data.Contribuyente.ListaImpuestos
    lisimpuestos = []
    for i in range(0, len(impuestos)):
        idimpuesto = impuestos[i]["idImpuesto"]
        descimpuesto = impuestos[i]["descImpuesto"]
        lisimpuestos.append(str(idimpuesto) + " " + descimpuesto)
    tipopersona=data.Contribuyente.tipoPersona
    mescierre=data.Contribuyente.mesCierre
    
    
    return render_template('info.html',
                           nombre=nombre,
                           domfiscal=domFiscal,
                           provincia=provincia,
                           codpostal=codpostal,
                           actividades=activ,
                           impuestos=lisimpuestos,
                           cuit=cuit,
                           tipopersona=tipopersona,
                           mescierre=mescierre,
                           
                           passstatic_url_path='/static')


@app.route('/individualportabla/<cuit>', methods = ["GET"])
def individualportabla(cuit):
    
    
    try:
        response = requests.request("GET", url+cuit,headers=headers)
        AFIP_json = response.json()

        data = pd.DataFrame(AFIP_json)
    except:
        error = "Error Obteniendo Datos"
        return render_template("error.html", error=error)
    
    data.drop(columns="errorGetData", inplace=True)
    data.dropna(inplace=True)
    
     
    if len(data.Contribuyente.ErroresObteniendoDatos) > 0:
        error = data.Contribuyente.ErroresObteniendoDatos
        
        return render_template("error.html", error=error)
    
    nombre=data.Contribuyente.nombre
    domFiscal=data.Contribuyente.domicilioFiscal["direccion"]
    provincia = data.Contribuyente.domicilioFiscal["nombreProvincia"]
    codpostal=data.Contribuyente.domicilioFiscal["codPostal"]
    actividades = data.Contribuyente.ListaActividades
    idactividad=actividades[0]["idActividad"]
    descactividad=actividades[0]["descActividad"]
    activ = str(idactividad) + " " + descactividad
    impuestos = data.Contribuyente.ListaImpuestos
    lisimpuestos = []
    for i in range(0, len(impuestos)):
        idimpuesto = impuestos[i]["idImpuesto"]
        descimpuesto = impuestos[i]["descImpuesto"]
        lisimpuestos.append(str(idimpuesto) + " " + descimpuesto)
    tipopersona=data.Contribuyente.tipoPersona
    mescierre=data.Contribuyente.mesCierre
    
    
    return render_template('info.html',
                           nombre=nombre,
                           domfiscal=domFiscal,
                           provincia=provincia,
                           codpostal=codpostal,
                           actividades=activ,
                           impuestos=lisimpuestos,
                           cuit=cuit,
                           tipopersona=tipopersona,
                           mescierre=mescierre,
                           
                           passstatic_url_path='/static')




@app.route('/resultados', methods=["POST"])
def resultados():
    global a 
    a= []
    tabla = pd.DataFrame()
    f = request.files['file']
    data_xls = pd.read_excel(f)
    data_xls.columns = ["cuit"]
    print(data_xls)
    cuits = list(data_xls.cuit.astype(str))
    

    threads = list()
    for i in range(0, len(cuits)):
        t = threading.Thread(target=get_data, args=(cuits[i],))
        threads.append(t)
        t.start()

    for process in threads:
        process.join()
    


    for i in range(0, len(a)):
        tabla.loc[i, "CUIT"]= str(int(a[i]["Contribuyente"]["idPersona"]))
        tabla.loc[i, "Nombre"] = a[i]["Contribuyente"]["nombre"]
        tabla.loc[i, "Direccion"] = a[i]["Contribuyente"]["domicilioFiscal"]["direccion"]
        tabla.loc[i, "Actividad Principal"] = a[i]["Contribuyente"]["ListaActividades"][0]["descActividad"]
        tabla.loc[i, "Provincia"] = a[i].Contribuyente.domicilioFiscal["nombreProvincia"]
    cols = tabla.columns
    return render_template('resultados.html',
                           data=tabla, 
                           cols = cols,
                           titulo = "Consulta datos por lote",
                           passstatic_url_path='/static')


@app.route('/consultaapocrifas', methods=["POST"])
def consultaapocrifas():
    global a 
    a= []
    tabla = pd.DataFrame()
    f = request.files['file1']
    data_xls = pd.read_excel(f)
    data_xls.columns = ["cuit"]
    for i in range(0,len(data_xls)):
        tabla.loc[i, "CUIT"] = str(data_xls.cuit[i])
        tabla.loc[i, "Incluido Base Apoc"] = str(consultabaseapoc(str(data_xls.cuit[i])))
        
    cols = tabla.columns
    return render_template('consultaapocrifas.html',
                           data=tabla, 
                           cols = cols, 
                           passstatic_url_path='/static')
