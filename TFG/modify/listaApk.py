import sys
import shlex, subprocess

#El parametro pasado es un txt y en cada linea se pasa un apk de la siguiente forma:

#NombreAPK;KeyStoreParaFirmar;AliasKeyStore

listaApp = sys.argv[1]

fin = open(listaApp, 'r') # in file
for app in fin:
	
	elements = app.rstrip('\n').split(";")
	folder = elements[0]
	apk = folder + '.apk'
	keyStore = elements[1]
	alias = elements[2]
	subprocess.call(shlex.split("apktool d "+apk+" -o "+ folder))
	subprocess.call(shlex.split("cp network_security_config.xml " + folder+ "/res/xml/"))
	print(folder+"/AndroidManifest.xml")
	
	manifest = open(folder+"/AndroidManifest.xml", 'r')
	modified = open('AndroidManifest.xml', 'w')
	for line in manifest:
		if "<application" in line:
			modified.write(line.split(">")[0]+ ' android:networkSecurityConfig="@xml/network_security_config"> ')
		else:
			modified.write(line)
	manifest.close()
	modified.close()
	subprocess.call(shlex.split("cp AndroidManifest.xml " + folder+ "/AndroidManifest.xml"))
	subprocess.call(shlex.split("rm AndroidManifest.xml"))
	#print("apktool b "+folder+" -o "+ folder+"Modified.apk")
	newApk = folder+"Mod.apk"
	subprocess.call(shlex.split("apktool b "+folder+" -o "+ newApk))
	subprocess.call(shlex.split('jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore ' + keyStore + '.keystore ' + newApk + ' ' + alias))

fin.close()





