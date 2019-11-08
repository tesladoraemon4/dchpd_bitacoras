import paramiko
import os
import subprocess
import re 
import socket as sock
class Connector(object):
	"""Conector con las bitacoras del sistema"""
	def __init__(self,ssh_servidor,ssh_usuario,ssh_clave,ssh_puerto
		):
		super(Connector, self).__init__()
		self.ssh_servidor = ssh_servidor # "192.168.56.4"
		self.ssh_usuario = ssh_usuario # "http"
		self.ssh_clave = ssh_clave # "pendejo01"
		self.ssh_puerto   = ssh_puerto # 22 # O el puerto SSH que use nuestro servidor
	def consultarArchivo(self,comando):
		#comando = "cat /etc/dhcp/dhcpd.conf"
		# Conectamos al servidor
		conexion = paramiko.Transport((self.ssh_servidor, self.ssh_puerto))
		conexion.connect(username = self.ssh_usuario, password = self.ssh_clave)
		# Abrimos una sesion en el servidor
		canal = conexion.open_session()
		# Ejecutamos el comando, en este caso un sencillo 'ls' para ver
		# el listado de archivos y directorios
		canal.exec_command(comando)
		# Y vamos a ver la salida
		salida = canal.makefile('rb', -1).readlines()
		conexion.close()
		if salida:
			# Si ha ido todo bien mostramos el listado de directorios
			return salida
		else:
			# Si se ha producido algun error lo mostramos
			return canal.makefile_stderr('rb', -1).readlines()

	def andRed(self,ipRed,mask):
		ipList = ipRed.split('.')
		maskList = mask.split('.')
		rs = [int(ipList[x])&int(maskList[x]) for x in range(len(ipList))]
		rs = str(rs[0])+"."+str(rs[1])+"."+str(rs[2])+"."+str(rs[3])
		return rs

	def consultarSubRedes(self):
		redes = []
		ip = r"\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b"
		regIp = re.compile(ip)
		regSubnet = r"^subnet *"+ip+" *netmask *"+ip
		confArch = self.consultarArchivo(comando="cat /etc/dhcp/dhcpd.conf")
		for line in confArch:
			rs = re.search(regSubnet,line)
			if(rs != None):
				resl = re.search(ip,line)
				ipRed = resl.group(0)
				resl = re.search(ip,line[line.index('netmask'):])
				mask = resl.group(0)
				ipRed = self.andRed(ipRed,mask)
				redes.append({"ip":ipRed,"mask":mask})
		return redes


	def consultarUsuariosSegmento(self,ipId):
		ip = r"(?P<ip>\b(?:(?:2(?:[0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9])\.){3}(?:(?:2([0-4][0-9]|5[0-5])|[0-1]?[0-9]?[0-9]))\b)"
		leases = self.consultarArchivo(comando="cat /var/lib/dhcp/dhcpd.leases")
		usu = []
		node = {}
		dateReg = r" (?P<weekday>\d*) (?P<year>\d*)\/(?P<month>\d*)\/(?P<day>\d*) (?P<hour>\d*):(?P<minute>\d*):(?P<second>\d*);"
		for line in leases[1:]:
			rs = re.match(r"^lease "+ip,line) 
			if(rs != None):
				node = {}
				node["ip"] = rs.group("ip") 
			if node!={} and self.andRed(node["ip"],ipId["mask"]) == ipId["ip"]:#si esta en la misma red
				node["mask"] = ipId["mask"]
				node["ipid"] = ipId["ip"]
				if(re.match(r"}",line)!=None):
					usu.append(node)
				elif(re.match(r"^(  )",line)!=None):#cosas de configuracion
					#ATRIBUTOS CON DATE
					#starts
					rs = re.match(r"  starts"+dateReg,line)
					if rs:
						node["starts"] = rs.groupdict()
					#ends
					rs = re.match(r"  ends"+dateReg,line)
					if rs:
						node["ends"] = rs.groupdict()
					#tstp
					rs = re.match(r"  tstp"+dateReg,line)
					if rs:
						node["tstp"] = rs.groupdict()
					#tsfp
					rs = re.match(r"  tsfp"+dateReg,line)
					if rs:
						node["tsfp"] = rs.groupdict()
					#atsfp
					rs = re.match(r"  atsfp"+dateReg,line)
					if rs:
						node["atsfp"] = rs.groupdict()
					#cltt
					rs = re.match(r"  cltt"+dateReg,line)
					if rs:
						node["cltt"] = rs.groupdict()
					#hardware
					rs = re.match(r"  hardware (?P<type>\w+) (?P<mac>(([0-9]|[a-f]){2}:){5}([0-9]|[a-f]){2});",line)
					if rs:
						node["hardware"] = rs.groupdict()
					#uid
					rs = re.match(r"  uid (?P<uid>\".+\")",line)
					if rs:
						node["uid"] = rs.groupdict()
					#binding state
					rs = re.match(r"  binding state (?P<state>\w+)",line)
					if rs:
						node["binding state"] = rs.groupdict()
					#next binding state
					rs = re.match(r"  next binding state (?P<state>\w+)",line)
					if rs:
						node["next binding state"] = rs.groupdict()
					#rewind binding state
					rs = re.match(r"  rewind binding state (?P<state>\w+)",line)
					if rs:
						node["rewind binding state"] = rs.groupdict()
		return usu


if __name__ == '__main__':
	connector = Connector(ssh_servidor =  "126.0.0.2",ssh_usuario =  "http",ssh_clave =  "pendejo01",ssh_puerto   =  22)

