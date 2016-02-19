import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from hichao.publish.crontab.update_hot_starusers_info import updata_hot_staruser_info

if __name__ == '__main__': 
    server = SimpleXMLRPCServer(("192.168.1.100", 8001))
    print "Listening on port 8000..."
    server.register_function(updata_hot_staruser_info, "updata_hot_staruser_info")
    server.serve_forever()
