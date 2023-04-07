class Voice(object):
    def __init__(self, id, name=None, languages=[], gender=None, age=None):
        self.id = id
        self.name = name
        self.languages = languages
        self.gender = gender
        self.age = age

    def __str__(self):
        return """<Voice id=%(id)s
          name=%(name)s
          languages=%(languages)s
          gender=%(gender)s
          age=%(age)s>""" % self.__dict__
