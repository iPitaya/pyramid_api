import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from update import update_star_sku

if __name__ == '__main__': 
    server = SimpleXMLRPCServer(("192.168.1.100", 8000))
    print "Listening on port 8000..."
    server.register_function(update_star_sku, "update_star_sku")
    server.serve_forever()
