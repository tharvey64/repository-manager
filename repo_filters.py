def name_startswith_filter(string):
    def name_filter(item):
        return item.get('name','').startswith(string)
    return name_filter

def name_in(*args):
    def name_filter(item):
        return item.get('name','') in args
    return name_filter