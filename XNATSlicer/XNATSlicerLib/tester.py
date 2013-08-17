def upload():

    login = "sunilk"
    password = "ambuSa5t"
    localSrc = "C:/Users/Sunil Kumar/Desktop/XNATSlicer/XNATSlicer/XNATSlicerLib/data/temp/upload/test1.mrb"
    f=open(localSrc, 'rb')
    filebody = f.read()
    f.close()
    
    
    #url = 'http://central.xnat.org/data' + XNATDst;
    url = 'http://central.xnat.org/data/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/resources/Slicer/files/test3.mrb'
    
    print "*******************URL: ", url
    
    
    req = urllib2.Request (url)
    connection = httplib.HTTPSConnection (req.get_host ())
    #userAndPass = b64encode(b"%s:%s"%(self.user,self.password)).decode("ascii")     
    userAndPass = b64encode(b"%s:%s"(login, password)).decode("ascii")       
    header = { 'Authorization' : 'Basic %s' %  userAndPass, 'content-type': 'application/octet-stream'}
    
    connection.request ('PUT', req.get_selector (), body=b64encode(filebody).decode("utf-8"), headers=header)
    response = connection.getresponse ()
    print "response: ", response.read()
    return response


def macCopy():
    import os, shutil
    sdMap = {}
    for root, dirs, files in os.walk('//vmware-host/Shared Folders/XNATSlicer'):
        for f in files:
            if not f.startswith("."):

                sdMap[f] = {}
                sdMap[f]['src'] = (os.path.join(root, f).replace("\\", "/"))
                
    for s in sdMap:
        dVal = ('C:\Users\Sunil Kumar\Desktop' +  sdMap[s]['src'].split("Shared Folders")[1]).replace("\\","/")
        sdMap[s]['dst'] = dVal

    try:
        shutil.rmtree('C:\Users\Sunil Kumar\Desktop\XNATSlicer')
    except:
        print "Shutil error"

    for key in sdMap:
        src = sdMap[key]['src']
        dst = sdMap[key]['dst']
        dirname = os.path.dirname(dst)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        print "Copying %s to:\n\t%s"%(src, dst)
        if not '.git' in dst:
            try:
                shutil.copy(src, dst)
            except:
                print "********Copy error: %s to %s"%(src,dst)
            

    


for root, dirs, files in os.walk('C:\Program Files\Slicer 4.2.0-2013-07-31'):
    print root
    for f in files:
        print f

        
def urlGet():
            
    XNATSrc = 'https://central.xnat.org/data/projects/XNATSlicerTest/subjects/DE-IDENTIFIED/experiments/UCLA_1297/scans/6/resources/DICOM/files?format=zip'
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, XNATSrc, 'sunilk', 'ambuSa5t')
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener(opener)
    print ("\nDownloading %s...\n"%(XNATSrc))
    response = urllib2.urlopen(XNATSrc)
    print "\n\n\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
    if "Content-Length" in response.headers:
        size = int (response.headers["Content-Length"])
    else:
        size = len (response.read ());
    print size
    return f


r = urlGet()



from __main__ import vtk, ctk, qt, slicer

layout = qt.QFormLayout()
window = qt.QWidget()
window.setLayout(layout)

r1 = qt.QLabel('asdf')
r2 = qt.QLabel('2asdf')
r3 = qt.QLabel('3asdf')

layout.addRow(r1)
layout.addRow(r2)
layout.addRow(r3)
    
window.show()

r1.setText("2222")
window.show()

    

makeWindow()
