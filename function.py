class Function:
    def __init__(self, function_id, function_imports, function_size):
        self.function_id = function_id
        self.function_imports = function_imports
        self.function_size = function_size

    def getLargestPackage(self):
        if(len(self.function_imports)>1):
            return {"", self.function_imports[0],self.function_imports[1]}
        elif(len(self.function_imports)==1):
            return {"", self.function_imports[0],None}
        return {"Do not Have any packages to import from lambda : ", None, None}
