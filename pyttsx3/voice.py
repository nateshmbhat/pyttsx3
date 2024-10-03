from typing import List

class Voice(object):
    def __init__(self, id, name=None, languages:List[str]=None, gender=None, age=None):
        self.id = id
        self.name = name
        self.languages = languages if languages else None
        self.gender = gender
        self.age = age
        self.languages.append("hello")

    def __str__(self):
        return """<Voice id=%(id)s
          name=%(name)s
          languages=%(languages)s
          gender=%(gender)s
          age=%(age)s>""" % self.__dict__

    def __repr__(self) -> str:
        return self.__str___()