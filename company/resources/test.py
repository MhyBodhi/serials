with open("com3dst.jpg","rb") as f:
    f.seek(2048,0)
    with open("test.jpg","wb") as fl:
        fl.write(f.read(141483))
