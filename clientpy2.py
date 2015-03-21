import socket
import sys
import time
  
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
orders = {}
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

def get_orders(stock):
  inp = run("ORDERS " + stock)[0].split()[1:]
  out = []
  for i in range(len(inp)/4):
    out.append( (inp[4*i], inp[4*i+1], float(inp[4*i+2]), int(inp[4*i+3])) )
  orders[stock] = out


# Max buy and min sell prices
def get_buy_and_sell_prices(order):
  cur_buy = 0
  cur_sell = 1000
  for bid_ask, name, price, nshare in order:
    if bid_ask == "BID":
      if price > cur_buy:
        cur_buy = price
    if bid_ask == "ASK":
      if price < cur_sell:
        cur_sell = price
  return (cur_buy, cur_sell)


def how_many_can_buy(order, money):
  sell_list = []
  for bid_ask, name, price, nshare in order:
    if bid_ask == "ASK":
      sell_list = sell_list + nshare * [price]
  sell_list = sorted(sell_list)
  count = 0
  for s in sell_list:
    if money < 0:
      break
    money -= s
    count += 1
  return count


def get_100th_buy_and_sell(order):
  cur_buy = 0
  cur_sell = 1000
  buy_list = []
  sell_list = []
  for bid_ask, name, price, nshare in order:
    if bid_ask == "BID":
      buy_list = buy_list + nshare * [price]
    if bid_ask == "ASK":
      sell_list = sell_list + nshare * [price]
  buy_list = sorted(buy_list)
  sell_list = sorted(sell_list)

  # Get 100th from both sides, if less than 100 then it's bad
  if len(buy_list) < 105 or len(sell_list) < 105:
    return (0,1000)

  return buy_list[-100], sell_list[100]


# assumes that get_orders was just called on everything
def sum_orders(stock):
  s = 0
  for _,_,_,n in orders[stock]:
    s += n
  return s



def buy_stock(stock):
  """
  Buy a stock with all our money

  while we haven't bought enough:
    get lowest seller
    bid that much
  """
  while True:
    get_cash()
    get_orders(stock)
    this_ord = orders[stock]

    cur_buy, cur_sell = get_buy_and_sell_prices(this_ord)

    # assume we can buy at cur_sell
    buying_price = cur_sell + 0.1
    num_shares = int(my_cash / buying_price)

    print "Buying %s: %d shares at %f" % (stock, num_shares, buying_price)
    print run("BID %s %f %d" % (stock, buying_price, num_shares))


def sell_stock(stock):
  """
  Dump everything instantly (don't do this lol)

  while we still have stock:
    get highest buyer
    ask that much
  """
  while True:
    get_my_securities()
    get_orders(stock)
    this_ord = orders[stock]

    cur_buy, cur_sell = get_buy_and_sell_prices(this_ord)

    # assume we can sell at cur_buy
    selling_price = cur_buy - 0.1
    num_shares = int(my_securities[stock][0])

    print "Selling %s: %d shares at %f" % (stock, num_shares, selling_price)
    run("ASK %s %f %d"% (stock, selling_price, num_shares))


def smart_sell(stock):
  """
  Dump a stock in a smart way

  cur_bid = current lowest bid - 5
  while still has stock:
    try to sell everything at cur bid
    subtract 5 from cur bid
    wait 3 second and loop again
  """
  want_price = None
  while True:
    get_my_securities()
    get_orders(stock)
    this_ord = orders[stock]

    _, cur_sell = get_buy_and_sell_prices(this_ord)
    if not want_price:
      want_price = cur_sell

    num_shares = int(my_securities[stock][0])
    print "Selling %s: %d shares at %f" % (stock, num_shares, want_price)
    run("ASK %s %f %d"% (stock, want_price, num_shares))

    time.sleep(3)
    want_price -= 0.05




def find_differences():
  get_securities()
  get_cash()
  for sec,_ in securities.iteritems():
    print "fetching orders", sec
    get_orders(sec)

  min_diff = 1000
  best_stock = None

  for sec,_ in securities.iteritems():
    buy_p, sell_p = get_100th_buy_and_sell(orders[sec])
    diff = sell_p - buy_p
    print sec, buy_p, sell_p, diff
    if diff < min_diff:
      min_diff = diff
      best_stock = sec

  print "best stock is", best_stock, min_diff

  for sec,_ in securities.iteritems():
    E = securities[sec][0]
    N = how_many_can_buy(orders[sec], my_cash)
    D = securities[sec][1]
    M = sum_orders(sec)
    magic_andrei_number = (E*N*D)+0.0 / (M+0.0)
    print sec, E, N, D, magic_andrei_number




get_securities()
get_cash()
get_my_securities()
get_my_orders()

#print "SECURITIES:", securities
print "MY SECURITIES:"
for sec,vs in my_securities.iteritems():
  if vs[0] > 0:
    print sec, vs

print "MY ORDERS:", my_orders
print "MY CASH:", my_cash

#find_differences()
#buy_stock("FB")
#smart_sell("SNY")
#print run("ASK FB 4.5 356")


