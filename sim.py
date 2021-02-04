#Imports
import random
#Global Constants
MAX_START_SCORE = 1000
MAX_USER_COUNT = 10        
FOLLOWER_RATIO = 4          #Number of followers for each creator
ITTERATIONS = 1000
LUV_MINT_FACTOR = 1000
ETH_POOL_START = 1000
LUV_POOL_START = 10000
BUY_AMMOUNT = .03125           #average number of ETH users spend on LUV

#Global Dynamics
GlobalScore = 0
GlobalLuvSupply = 10000
GlobalBurn = 0
userCount = 0
users = {}
creators = []       #user ID of creators

#Classes
class user:
    #attributes
    id = 0                  #Users have an id,
    score = 0               #A score,
    balance = 0             #A LUV balance,
    matches = []            #an array of matches,
    burn_flavor = 5       #likelyhood out of 10 user will burn LUV
    buy_flavor = 5          #likeyhood out of 10 user will buy more LUV
    sell_flavor = 5         #likeyhood out of 10 user will sell existing LUV

    #Private methods
    def _increaseScore(self, x):
        global GlobalScore
        self.score += x
        GlobalScore += x
    
    def _mint(self,x):
        global GlobalLuvSupply
        self.balance += x
        GlobalLuvSupply += x

    #Constuctors
    def __init__(self,id,score,balance,burnf,buyf,sellf):
        global userCount
        userCount += 1
        self.id = id
        self.score = score
        self.balance = balance
        self.burn_flavor = burnf
        self.buy_flavor = buyf
        self.sell_flavor = sellf

        print("Signing up new user: \t %s"%self.serialize())
    def __init__(self,id):
        global userCount
        userCount += 1
        self.id = id
        self._increaseScore(random.randint(0,MAX_START_SCORE))
        self.burn_flavor = random.randint(0,10)
        self.buy_flavor = random.randint(0,10)
        self.sell_flavor = random.randint(0,10)

        print("Signing up new user: \t %s"%self.serialize())

    #Public Methods   
    def serialize(self):
        return("[ID: %d, SCORE: %d, BALANCE: %d]" % (self.id,self.score,self.balance))


class creator(user):
    likes = []              #an array of likes (not also matches),
    def accept(self,who):
        if(self not in who.matches):        
            print("\t"+who.serialize())
            self.matches.append(who)
            who.matches.append(self)
            who._increaseScore(9+self.score)
            #Mint new LUV
            LUV = ((self.score + who.score )/GlobalScore) * LUV_MINT_FACTOR
            self._mint(LUV)
            who._mint(LUV)

class follower(user):   
    def like(self, who):
        if(self not in who.likes):
            print("\t"+who.serialize())
            who.likes.append(self)
            who._increaseScore(1+self.score)

class exchange():
    eth = 0
    luv = 0
    def getPrice(self):
        return (self.eth/self.luv)
    def __init__(self,_eth,_luv):
        self.eth = _eth
        self.luv = _luv
    def buy(self,_eth):
        if(_eth/self.getPrice() > self.luv):
            return False
        else:
            self.eth += _eth
            self.luv -= (_eth/self.getPrice())
            return True
    def sell(self, _luv):
        if(_luv * self.getPrice() > self.eth):
            return False
        else:
            self.eth -= _luv * self.getPrice()
            self.luv += _luv


#MAIN CODE
ex = exchange(ETH_POOL_START,LUV_POOL_START)
results = open('results.csv','w')
results.write("Itteration,User Count, Global Score, Global LUV supply, price, Total Burn Ammount\n")
#HELPER FUNCTIONS

#Create new user in accordance with config info
def newUser(id):
    user = {}  
    isCreator = random.randint(0,FOLLOWER_RATIO)
    if(isCreator==0):
        creators.append(id)
        user = creator(id)  
    else:
        user = follower(id)
    users[id] = user        #add our new user to the global users dic

#have user buy, burn, buy&burn or sell
def tokenAction(user):
    x = random.randint(0,10)
    if(x<user.buy_flavor):
        buy(user)
    if(x<user.burn_flavor):
        burn(user)
    elif(x>=user.buy_flavor and x<user.sell_flavor):
        sell(user)

def buy(user):
    global GlobalLuvSupply
    if(ex.buy(user.balance / ex.getPrice())):
        print("BUY EVENT!!!: %f LUV bought for %f ETH"%(user.balance,user.balance * ex.getPrice()))
        GlobalLuvSupply += user.balance
        user.balance += user.balance / ex.getPrice()

def sell(user):
    global GlobalLuvSupply
    if(ex.sell(user.balance)):
        print("SELL EVENT!!!: %f LUV sold for %f ETH"%(user.balance,user.balance * ex.getPrice()))
        GlobalLuvSupply -= user.balance
        user.balance = 0

def burn(user):
    global GlobalLuvSupply, GlobalScore, GlobalBurn
    score = (user.balance / LUV_MINT_FACTOR) * GlobalScore
    user.score += score
    GlobalLuvSupply -= user.balance     #decrase LUV in circulation
    GlobalScore += score                #increase global score
    GlobalBurn += user.balance
    print("BURN EVENT!!! %f LUV burned for %f Score"%(user.balance,user.score))
    user.balance = 0

#Create our focused user
focus = follower(MAX_USER_COUNT+1)
#MAINLOOP
index = 0
while(index < ITTERATIONS):
    index+=1
    #PRINT ITERATION DETAILS
    print("===============ITTERATION #%d==============="%(index))
    print("User Count: %d"%(userCount))
    print("Global Score: %f"%(GlobalScore))
    print("Global LUV Supply: %f"%(GlobalLuvSupply))
    print("LUV Price: %f"%(ex.getPrice()))
    results.write('%d,%d,%f,%f,%f,%f\n'%(index,userCount,GlobalScore,GlobalLuvSupply,ex.getPrice(),GlobalBurn))

    #pick random user
    userID = random.randint(0,MAX_USER_COUNT)
    #If not existing. Create new user
    if(userID not in users):
        newUser(userID)
    elif(type(users[userID]) is creator):
        print("LIKES FOR THE CREATOR: "+users[userID].serialize())
        for like in users[userID].likes:
            #Evaluate accept here
            users[userID].accept(like)
    else:
        print("CREATORS BEING LIKED BY FOLLOWER: "+users[userID].serialize())
        for creatorId in creators:
            #Evaluate like here
            users[userID].like(users[creatorId])            #Call like function

    #decide if user will take action to buy/sell/burn LUV
    if(users[userID].balance > 0):
        tokenAction(users[userID])
    

results.close()