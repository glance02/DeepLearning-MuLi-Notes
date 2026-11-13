# 类
class Man:
    def __init__(self, name) -> None:
        self.name = name
        print("initialized!")

    def hello(self):
        print("Hello " + self.name + "!")

    def goodbye(self):
        print("goodbye" + self.name + " !")


m = Man("Glance")
m.hello()
m.goodbye()
