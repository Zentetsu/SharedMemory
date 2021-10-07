from nClient import nClient
 
if __name__ == '__main__':
    c = nClient(name="test", value=10, exist=True)
    c = nClient(name="test", value=10, exist=True)
    print(c)
    c.close()