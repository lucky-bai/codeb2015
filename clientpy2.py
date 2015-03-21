import socket
import sys
  
def run(*commands):
  HOST, PORT = "codebb.cloudapp.net", 17429
  
  data=OUR_USERNAME + " " + OUR_PASSWORD + "\n" + "\n".join(commands) + "\nCLOSE_CONNECTION\n"
  return_lines = []

  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((HOST, PORT))
    sock.sendall(data)
    sfile = sock.makefile()
    rline = sfile.readline()
    while rline:
      #print(rline.strip())
      return_lines.append(rline.strip())
      rline = sfile.readline()
  finally:
    sock.close()

  return return_lines

def subscribe():
  HOST, PORT = "codebb.cloudapp.net", 17429
  
  data=OUR_USERNAME + " " + OUR_PASSWORD + "\nSUBSCRIBE\n"

  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.connect((HOST, PORT))
    sock.sendall(data)
    sfile = sock.makefile()
    rline = sfile.readline()
    while rline:
      print(rline.strip())
      rline = sfile.readline()
  finally:
    sock.close()


OUR_USERNAME = "/dev/rand_AB"
OUR_PASSWORD = "pi<4"

securities = {}
my_cash = 0
my_securities = {}
my_orders = {}


# Query all the securities
def get_securities():
  inp = run("SECURITIES")[0].split()[1:]
  for i in range(len(inp)/4):
    securities[inp[4*i]] = (float(inp[4*i+1]), float(inp[4*i+2]), float(inp[4*i+3]))

def get_cash():
  global my_cash
  my_cash = float(run("MY_CASH")[0].split()[1])

def get_my_securities():
  inp = run("MY_SECURITIES")[0].split()[1:]
  for i in range(len(inp)/3):
    my_securities[inp[3*i]] = (float(inp[3*i+1]), float(inp[3*i+2]))

def get_my_orders():
  global my_orders
  my_orders = {}
  inp = run("MY_ORDERS")[0].split()[1:]
  for i in range(len(inp)/4):
    my_orders[inp[4*i+1]] = (inp[4*i], float(inp[4*i+2]), float(inp[4*i+3]))
  


get_securities()
get_cash()
get_my_securities()
get_my_orders()

print securities
print my_cash
print my_securities
print my_orders



