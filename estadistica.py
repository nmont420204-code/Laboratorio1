class MedidasDescriptivas():
    def __init__(self):
        self.conteo = 0 
        self.suma   = 0 
        self.suma_cuad = 0
        self.max   = None
        self.min   = None
        
    def agregar(self,x):
        self.conteo = self.conteo + 1
        self.suma = self.suma + x
        self.suma_cuad = self.suma_cuad + x*x
        self.max = x if self.max is None or x > self.max else self.max
        self.min = x if self.min is None or x < self.min else self.min 

    def rango(self):  
            if self.conteo == 0:
                 return None 
            else :  
                return self.max - self.min

    def media(self):
        if self.conteo == 0:
             return None 
        else :
             return self.suma / self.conteo

    def varianza(self):
        if self.conteo > 1:
              return (self.suma_cuad - (self.suma**2/self.conteo)) / (self.conteo - 1)
        else:
              return None 

    def desviación(self):
         return self.varianza()**0.5

    def coef_variación(self):
        return self.desviación() / self.media()
        
        
md= MedidasDescriptivas()
for x in [1200,1500,1500,1800,2100,2400,2400,3000,3600,9000]:
    md.agregar(x)
print(md.conteo,md.suma,md.suma_cuad,md.max,md.min)
print(md.rango(),md.media(),md.varianza(),md.desviación(),md.coef_variación())
