'''MODEL3: In this model we will allow the traids to mutate. But this eviroment also change. We will reducing food over time'''

import random
from statistics import mean
from matplotlib import pyplot

def move(L,vel,lim):
    '''This function simulates the random motion of species'''
    #To simulate the random motion, we will add random number ranging from (-vel,vel) in x and y cordinate
    L = [L[0]+vel*(2*random.random()-1),L[1]+vel*(2*random.random()-1)]
    #If species go beyond the boundary, we will reset its co-ordinate back to inside the boundary
    if L[0]>=lim:
        L[0]=0
    if L[1]>=lim:
        L[1]=0
    return L

def reso(n,lim):
    '''This function give us co-ordinate of food at random location within a bound region'''
    #We will be storing co-ordinates in the list R
    R=[]
    #Now we will generate the food at random location and will add it in the list
    for i in range(n):
        #we will first randomly generate x and y co-ordinates
        x=random.uniform(-lim,lim)
        y=random.uniform(-lim,lim)
        #then append them as list into R
        R.append([x, y])
    return R

def basket(R,spa,lim):
    '''This function will help us finding food in the sensing distance faster. For that we will divide the whole enivronment into grids and will store the grid repsentation as nested dictionary and element of these dictionary will be co-ordintae of food.'''
    #bas will be our dictionary to store the food co-ordinate
    bas = {}
    #Now we will create a nested dictionary
    for i in range(-lim//spa-2*spa,lim//spa+spa):
        bas[i]={}
    #Inside these nested dictionary, we will have list to store the co-ordinate of food
    for i in range(-lim//spa-2*spa,lim//spa+spa):
        for j in range(-lim//spa-2*spa,lim//spa+spa):
            bas[i][j]=[]
    #The index of first dictionary will represent x co-ordinate in the grid and index of nested will be represting y co-ordinate
    for i in range(len(R)):
        #now we will store the grid location of k in xs and ys
        xs = R[i][0]//spa
        ys= R[i][1]//spa
        #finally we will add the element in that basket
        bas[xs][ys].append(R[i])
    return bas

def movto(L,R,vel):
    '''This function simulates motion of organism to move toward food once it has sensed it.'''
    #dx and dy are difference in co-ordinates of L and R
    dx = R[0]-L[0]
    dy = R[1]-L[1]
    #Now we can calculate cos and sin from these two
    sin = dy/(dx**2+dy**2)**(1/2)
    cos = dx/(dx**2+dy**2)**(1/2)
    #now motion of organism toward food with v velocity for which we will add the component of velocity to the x and y co-ordiante
    L = [L[0]+cos*vel,L[1]+sin*vel]
    return L

def close(L,dic,sd,spa):
    '''This function will dectect the closest food in the sensing range and will set it as target'''
    #tar(binary number) will represent whether L has found a food in its sensing range or not
    global tar
    #xs and ys is location of organism in the grid we created in basket function
    xs = L[0]//spa
    ys = L[1]//spa
    #P is list of possible direction we have to check for both x and y
    P = [0,-1,1]
    for i in P:
        for j in P:
            #we will check whether adjacent region has any particle in sensing range or not
            if xs+i<=lim and xs+i>-lim and ys+j<=lim and ys+j>-lim:
                for k in dic[xs+i][ys+j]:
                    #Now if found anything in sensing distance, it will be our target
                    if (L[0]-k[0])**2+(L[1]-k[1])**2<=sd**2:
                        #We have found a target
                        tar = 1
                        #sensed target is k
                        return k
    return 0

def eat(L,k,spa):
    '''This function will remove the food from the list res if organism eats the food it was heading for'''
    global bas
    global res
    global tar
    #if organism come very close to food for a given radius, let's say eating radius(er), it will eat it, in other word, remove from R and basket
    if (L[0]-k[0])**2+(L[1]-k[1])**2<=0.05**2:
        res.remove(k)
        bas[k[0]//spa][k[1]//spa].remove(k)
        #Now we will rest the target to 0 as organism has to look for new food
        tar = 0
        return 1
    return 0


def mutalist(L,f):
    '''This will give generate a mutation which happens with a probality of f each time organism reproduce'''
    #ML will store the location where is their is a possiblity of mutation
    ML=[]
    #Now we will randomly generate the int from 0 to len(L)-1, these are the location where their is a chance of mutation
    for j in range(int(f*len(L))+1):
        ML.append(random.randint(0,len(L)-1))
    return(ML)

def mutation(L,i,dv,ds,vth,sdth):
    '''This function mutate the organism by changing its trad'''
    v=vth[i]+random.choice((-0.01,0.01))
    s=sdth[i]+random.choice((-0.03,0.03))
    return((v,s))


#-----------------------------------------------------------------------------------------------
'''Now as we have defined all necessary functions to simulate our environment, next we declare the values of these variable that we will be using to simulate the environment. Different values of these variable will lead to different environment conditions and consequences'''

#SPECIES CHARATERISTICS

#org is initial size of population and L is initial co-ordinate of these organism
org=10
L=[[0,0]]*org

#Vel will be initial velocity of the sample and vth will store the velocity of each organism as list
vel = 0.1
vth=[vel]*org

#sd is initial sensing distance
sd=0.3
sdth=[sd]*org

#Een will store energy of each organism at the start of each day/generation and Eenth will be list of this for each organism
Een=1000
Eenth=[Een]*org

#tar variable will tell us whether organims is heading toward a food or not and targ will be the list carrying indiviual tar for each organism
tar=0
targ=[tar]*org

#if the target is set, kth will store the individual target food in list
kth=[0]*org

#spam will carry the food that one organism has consumed in one gen in form of list
spam=[0]*org


#ENVIROMENT

#lim represent the size of the our playground
lim=10

#fn is the number of resources that will be available each day and res will store the co-ordinate of the food we generate in the reso function.
fn=200
res = reso(fn,lim)

#As we will be creating grid in the basket function, spa will carry size of grid, and bas will be dictionary of grid representation of res
spa = 2
bas = basket(res,spa,lim)


#-----------------------------------------------------------------------------------------------
'''Now we will simulate one generation of a species and will store which organism were able to survive throughout the process and some might be able to reproduce.'''

def day(L,kth,Eenth,lim,spa,bas,spam):
    '''This function simulates one day/generation of all the organisms in a species'''
    #n is total number of food that has been consumed by the organisms
    n=0
    #c is total number of steps organisms has taken so far
    c=0

    global tar
    global targ
    global vth
    global sdth

    #Now organism will move in environment until minimum food has been consumed or minimum number of steps has been taken
    while n<fn*0.90 and c<100000:
        n=0
        #Now we will be doing the simulation for each organism
        for i in range(len(L)):
            #An organism will only move if it has energy
            if Eenth[i]>0:
                tar=targ[i]
                #Organism will lose energy with each step it make which is per positional to kinetic enrgy and sensing distance
                Eenth[i]=Eenth[i]-(vth[i]**2)-(sd)
                #Organism will move radnomly if it does not have target
                if tar==0:
                    L[i]=move(L[i],vth[i],lim)
                    #Will check its sesnsing range for potential target
                    kth[i]=close(L[i],bas,sdth[i],spa)
                #But it will move toward the target if it already has set one
                elif tar==1:
                    #But it will check if target is still in range or other organims took it
                    if kth[i] in res:
                        L[i]=movto(L[i],kth[i],vth[i])
                        #It will eat the food if it is in eating range
                        ea=eat(L[i],kth[i],spa)
                        #It will increase food count if it eats the food
                        if ea==1:
                            n+=1
                            spam[i]+=1
                    #It will reset the target if kth is not in the reso
                    else:
                        tar=0
                #Now we will the store the state of target in targ list
                targ[i]=tar
        #c will count the number of step
        c+=1


    '''Now once simulation of day is over, we will look which organisms were able to survive and reproduce'''
    #We will generate the list where mutation is possible
    ML = mutalist(L,0.01)

    #Now we will create list to store the values of next generation temporarily. Lth, vtm and sdtm are temporary L,vth and sdth respectivly
    Ltm=[]
    vtm=[]
    sdtm=[]
    #Now we look at each species for surival and reproduction. A minimum criteria is set for survival and reproduction
    for i in range(len(L)):
        #Organism will be check for survival criteria
        if spam[i]!=0:
            #Now we will add the organims in our temporary list if it survive
            Ltm.append(L[i])
            vtm.append(vth[i])
            sdtm.append(sdth[i])
            
            #Now we will check for reproduction criteria
            if spam[i]>=2:
                #We will mutate the offspring if is in mutation list
                if i in ML:
                    Ltm.append(L[i])
                    vtm.append(mutation(L,i,0.01,0.1,vth,sdth)[0])
                    sdtm.append(mutation(L,i,0.01,0.1,vth,sdth)[1])
                #otherwise we will add it as it is
                else:
                    Ltm.append(L[i])
                    vtm.append(vth[i])
                    sdtm.append(sdth[i])
                #organsim count with each reproduction
    #Now we will make our velocity and speed list from temporary to permanent
    vth=vtm[::]
    sdth=sdtm[::]
    return(Ltm)

#----------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------------------------#
#These two lists are to plot graph
plotv=[vel]
plots=[sd]
ppl=[len(L)]

#==============================================================================================#
#Now we will run simulation for multiple generation
for i in range(50):
    #Now we will update our organism list after each generation
    L=day(L,kth,Eenth,lim,spa,bas,spam)
    #We will reduce the number of food after each day. Rate can be alter
    fn-=0.1

    print('genration',i+1)
    print('population',len(L))
    '''--------------------------------------------------------------------------------------'''
    #UPDATING CHARATERISTIC OF SPECIES AND ENVIRONMENT AT THE END OF THE GENERATION
    #Now we will update the length of targ, kth and spam list as it has been updated
    targ=[0]*len(L)
    kth=[0]*len(L)
    spam=[0]*len(L)
    #Organism will again start their day with energy
    Eenth=[Een]*len(L)
    #Now food will appear at new location for the next generation
    res = reso(int(fn),lim)
    bas=basket(res,spa,lim)
    '''--------------------------------------------------------------------------------------'''
    #Now we will collect data to plot graph.
    ppl.append(len(L))
    #We will break the loop if population is zero
    if len(L)==0:
       break

    plotv.append(mean(vth))
    plots.append(mean(sdth))
'''--------------------------------------------------------------------------------------'''
#Now we will be ploting graph between population and day of specis
pyplot.plot(ppl,'-')
pyplot.title('Population of Species over day/Generation')
pyplot.xlabel('generation')
pyplot.ylabel('population')
pyplot.show()

pyplot.plot(plotv,'-')
pyplot.xlabel('generation')
pyplot.ylabel('speed')
pyplot.show()

pyplot.plot(plots,'-')
pyplot.xlabel('generation')
pyplot.ylabel('sesnsing distance')
pyplot.show()

#==============================================================================================#


