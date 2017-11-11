#Riley Karp
#view.py
#02/27/2017

import numpy as np
import math

class View:

    def __init__(self):
    	#sets up the View
        self.reset()

    def reset(self):
    	#resets the view parameters to their original values
        self.vrp = np.matrix([0.5,0.5,1.0])
        self.vpn = np.matrix([0.0,0.0,-1.0])
        self.vup = np.matrix([0.0,1.0,0.0])
        self.u = np.matrix([-1.0,0.0,0.0])
        self.extent = [1.0,1.0,1.0]
        self.screen = [400.0,400.0]
        self.offset = [20.0,20.0]

    def build(self):
        #move VRP to origin
        vtm = np.identity(4,float)
        t1 = np.matrix( [[1,0,0,-self.vrp[0,0]],
                        [0,1,0,-self.vrp[0,1]],
                        [0,0,1,-self.vrp[0,2]],
                        [0,0,0,1]],dtype=float )
        vtm = t1*vtm

        #calculate tu, tvup, and tvpn
        tu = np.cross( self.vup,self.vpn )
        tvup = np.cross( self.vpn,tu )
        tvpn = self.vpn

        #normalize tu, tvup, tvpn to unit length
        for v in [tu,tvup,tvpn]:
            self.normalize(v)

        self.u = tu
        self.vup = tvup
        self.vpn = tvpn

        #align view reference axes
        r1 = np.matrix( [[ tu[0,0], tu[0,1], tu[0,2], 0.0 ],
                         [ tvup[0,0], tvup[0,1], tvup[0,2], 0.0 ],
                         [tvpn[0,0], tvpn[0,1], tvpn[0,2], 0.0 ],
                         [ 0.0, 0.0, 0.0, 1.0 ]], dtype=float )
        vtm = r1*vtm

        #translate lower left corner of view space to origin
        t2 = np.matrix( [[ 1,0,0,0.5*self.extent[0] ],
                         [ 0,1,0,0.5*self.extent[1] ],
                         [ 0,0,1,0 ],
                         [ 0,0,0,1 ]], dtype=float  )
        vtm = t2*vtm

        #scale the screen
        s1 = np.matrix( [[ -self.screen[0]/self.extent[0],0,0,0 ],
                         [ 0,-self.screen[1]/self.extent[1],0,0 ],
                         [ 0,0,1.0/self.extent[2],0 ],
                         [ 0,0,0,1 ]], dtype=float  )
        vtm = s1*vtm

        #translate lower left corner to origin & add view offset
        t3 = np.matrix( [[ 1,0,0,self.screen[0]+self.offset[0] ],
                         [ 0,1,0,self.screen[1]+self.offset[1] ],
                         [ 0,0,1,0 ],
                         [ 0,0,0,1 ]], dtype=float  )
        vtm = t3*vtm

        return vtm

    def normalize(self,v):
    	#normalizes the given vector
        length = math.sqrt(v[0,0]*v[0,0] + v[0,1]*v[0,1] + v[0,2]*v[0,2])
        if length != 0:
            v[0,0] = v[0,0]/length
            v[0,1] = v[0,1]/length
            v[0,2] = v[0,2]/length

    def clone(self):
    	#creates and returns a clone of the current view object
        newView = View()
        newView.vrp = self.vrp
        newView.vpn = self.vpn
        newView.vup = self.vup
        newView.u = self.u
        newView.extent = self.extent
        newView.screen = self.screen
        newView.offset = self.offset
        return newView
        
    def rotateVRC(self,VUPangle,Uangle):
    	#rotates the center of the view volume around the the VUP and U axes based on
    	#the given angles
    	cor = self.vrp + self.vpn*self.extent[2]*0.5
    	t1 = np.matrix( [[1,0,0,-cor[0,0]],
    					 [0,1,0,-cor[0,1]],
    					 [0,0,1,-cor[0,2]],
    					 [0,0,0,1]], dtype=float  )
    	Rxyz = np.matrix( [ [self.u[0,0],self.u[0,1],self.u[0,2],0],
    						[self.vup[0,0],self.vup[0,1],self.vup[0,2],0],
    						[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0],
    						[0,0,0,1] ], dtype=float  )
    	cosVUP = math.cos( math.radians(VUPangle) )
    	sinVUP = math.sin( math.radians(VUPangle) )
    	cosU = math.cos( math.radians(Uangle) )
    	sinU = math.sin( math.radians(Uangle) )
    	r1 = np.matrix( [[cosVUP,0,sinVUP,0],
    					 [0,1,0,0],
    					 [-sinVUP,0,cosVUP,0],
    					 [0,0,0,1]], dtype=float  )
    	r2 = np.matrix( [[1,0,0,0],
    					 [0,cosU,-sinU,0],
    					 [0,sinU,cosU,0],
    					 [0,0,0,1]], dtype=float  )
    	t2 = np.matrix( [[1,0,0,cor[0,0]],
    					 [0,1,0,cor[0,1]],
    					 [0,0,1,cor[0,2]],
    					 [0,0,0,1]], dtype=float  )
    	tvrc = np.matrix( [ [self.vrp[0,0],self.vrp[0,1],self.vrp[0,2],1],
    						[self.u[0,0],self.u[0,1],self.u[0,2],0],
    						[self.vup[0,0],self.vup[0,1],self.vup[0,2],0],
    						[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0] ], dtype=float  )
    	tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T
    	
    	#copy values from tvrc back to VPR, U, VUP, and VPN
    	self.vrp = np.matrix( tvrc.tolist()[0][0:-1], dtype=float  )
    	self.u = np.matrix( tvrc.tolist()[1][0:-1], dtype=float  )
    	self.vup = np.matrix( tvrc.tolist()[2][0:-1], dtype=float  )
    	self.vpn = np.matrix( tvrc.tolist()[3][0:-1], dtype=float )
    	
    	#normalize U, VUP, and VPN
    	for v in [self.u,self.vup,self.vpn]:
    		self.normalize(v)

def main():
    v = View()
    print v.build()

if __name__ == '__main__':
    main()
