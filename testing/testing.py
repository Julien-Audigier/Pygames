class bob:
    def __init__(self, name):
        self.name = name
    
    def say_hello(self):
        print(f"Hello, my name is {self.name}!")

class bobJr(bob):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age
    
    def say_hello(self):
        print(f"Hello, my name is {self.name} and I am {self.age} years old!")

dot = bobJr("Bob Jr.", 5)
print(dot.name)
print(dot.age)
GOG = bob("GOG")
print(GOG.name)
GOG.say_hello()
dot.say_hello()