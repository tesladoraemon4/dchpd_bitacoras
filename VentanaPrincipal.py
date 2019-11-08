# -*- coding: utf-8 -*-
from  Main import *
import sys
import re
import Connector as c 
import datetime
try:
    _fromUtf8 = QtCore.QString.fromUtf9
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
class VentanaPrincipal(QtGui.QMainWindow):

    __instance = None

    @staticmethod
    def getInstance():
        """Obtiene la instancia ya creada de la ventana principal.
            Parámetros:
                (void)
            Retorno:
                VentanaPrincipal
        """
        if VentanaPrincipal.__instance == None:
            VentanaPrincipal()
        return VentanaPrincipal.__instance 
    def __init__(self, parent=None):
        if VentanaPrincipal.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            QtGui.QWidget.__init__(self,parent)
            self.ui=Ui_MainWindow()
            self.ui.setupUi(self)
            #conector
            self.connector = c.Connector(ssh_servidor =  "126.0.0.2",ssh_usuario =  "http",ssh_clave =  "pendejo01",ssh_puerto   =  22)
            self.subNet = self.connector.consultarSubRedes()
            for net in self.subNet:
                self.ui.net_selector.addItem(net["ip"])
                self.ui.net_selector_2.addItem(net["ip"])
            #salida
            QtCore.QObject.connect(self.ui.net_search,QtCore.SIGNAL("clicked()"),self.search_net)
            QtCore.QObject.connect(self.ui.net_search_2,QtCore.SIGNAL("clicked()"),self.search_net2)


    def search_net2(self):
        posSelec = self.ui.net_selector_2.currentIndex()
        ipRed = self.subNet[posSelec-1]
        filas = self.connector.consultarUsuariosSegmento(ipRed)
        Columnas = 7
        self.ui.tableWidget.setColumnCount(Columnas)
        cont = 0 
        lista = []
        for data in filas:
            d = data["starts"]
            e = data["ends"]
            ahora = datetime.datetime.now()#datetime(int(d["year"]),int(d["month"]), int(d["day"]),int(d["hour"]),int(d["minute"]),int(d["second"]))
            termino = datetime.datetime(int(e["year"]), int(e["month"]), int(e["day"]),int(e["hour"]),int(e["minute"]),int(e["second"]))
            tiempoRestante = termino-ahora
            lista.append({
                "t":QtGui.QTableWidgetItem(str(tiempoRestante)),
                "edo":QtGui.QTableWidgetItem(data["binding state"]["state"]),
                "ip":QtGui.QTableWidgetItem(data["ip"]),
                "mac":QtGui.QTableWidgetItem(data["hardware"]["mac"]),
                "uid":QtGui.QTableWidgetItem(data["uid"]["uid"]),
                "starts":QtGui.QTableWidgetItem(str(datetime.datetime(int(d["year"]),int(d["month"]), int(d["day"]),int(d["hour"]),int(d["minute"]),int(d["second"])))),
                "ends":QtGui.QTableWidgetItem(str(datetime.datetime(int(e["year"]), int(e["month"]), int(e["day"]),int(e["hour"]),int(e["minute"]),int(e["second"]))))
                })
            cont += 1


        self.ui.tableWidget.setRowCount(cont)
        for x in range(cont):
            self.ui.tableWidget.setItem( x, 0, lista[x]["ip"]);
            self.ui.tableWidget.setItem( x, 1, lista[x]["starts"]);
            self.ui.tableWidget.setItem( x, 2, lista[x]["ends"]);
            self.ui.tableWidget.setItem( x, 3, lista[x]["mac"]);
            self.ui.tableWidget.setItem( x, 4, lista[x]["uid"]);
            self.ui.tableWidget.setItem( x, 5, lista[x]["t"]);
            self.ui.tableWidget.setItem( x, 6, lista[x]["edo"]);

    def search_net(self):
        posSelec = self.ui.net_selector.currentIndex()
        ipRed = self.subNet[posSelec-1]
        filas = self.connector.consultarUsuariosSegmento(ipRed)
        Columnas = 4
        self.ui.tableWidget_3.setColumnCount(Columnas)
        cont = 0 
        lista = []
        for data in filas:
            d = data["starts"]
            e = data["ends"]
            ahora = datetime.datetime.now()#datetime(int(e["year"]),int(d["month"]), int(d["day"]),int(d["hour"]),int(d["minute"]),int(d["second"]))
            termino = datetime.datetime(int(e["year"]), int(e["month"]), int(e["day"]),int(e["hour"]),int(e["minute"]),int(e["second"]))
            tiempoRestante = termino-ahora
            if(not termino <= ahora and data["binding state"]["state"] == "active"):
                lista.append({"t":QtGui.QTableWidgetItem(str(tiempoRestante)),"edo":QtGui.QTableWidgetItem(data["binding state"]["state"]),"ip":QtGui.QTableWidgetItem((data["ip"])),"mac":QtGui.QTableWidgetItem((data["hardware"]["mac"]))})
                cont += 1
            #else:
            #    filaActual = self.ui.tableWidget_3.currentRow() 
            #    self.ui.tableWidget_3.removeRow(filaActual)
            #    self.ui.tableWidget_3.setItem( y, 2, QtGui.QTableWidgetItem("Caducado"));
            #    self.ui.tableWidget_3.setItem( y, 3, QtGui.QTableWidgetItem("abandoned"));
        self.ui.tableWidget_3.setRowCount(cont)
        for x in range(cont):
            self.ui.tableWidget_3.setItem( x, 0, lista[x]["t"]);
            self.ui.tableWidget_3.setItem( x, 1, lista[x]["edo"]);
            self.ui.tableWidget_3.setItem( x, 2, lista[x]["ip"]);
            self.ui.tableWidget_3.setItem( x, 3, lista[x]["mac"]);

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = VentanaPrincipal()
    myapp.show()
    sys.exit(app.exec_())