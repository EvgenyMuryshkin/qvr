def load(file):
    f = open("web/" + file)
    content = f.read().encode('utf-8')
    f.close()
    return content