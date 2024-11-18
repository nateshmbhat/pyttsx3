class Voice:
    def __init__(self, id, name=None, languages=None, gender=None, age=None) -> None:
        self.id = id
        self.name = name
        self.languages = languages or []
        self.gender = gender
        self.age = age

    def __str__(self) -> str:
        return """<Voice id={id}
          name={name}
          languages={languages}
          gender={gender}
          age={age}>""".format(**self.__dict__)
