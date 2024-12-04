#!/usr/bin/python
import json as json


# Lenient Json parsing:
#
# Parse json so you can access a la
# input: { a: {b: [{c: d}]}
# a.b.first.c -> d
# and a.b[0].c -> d
#
# and always return None-like object if the path is wrong
# Hook it in with the object_hook argument in json.load or json.loads
class Lenient(dict):
    @classmethod
    def from_list(cls, a_list):
        assert isinstance(a_list, list)
        if not len(a_list):  # if empty list, return empty Lenient
            return Lenient()
        # else return populated lenient object
        l = Lenient(enumerate(a_list), last=a_list[-1], first=a_list[0])
        l.as_list = a_list
        return l

    def __getattr__(self, name):
        obj = self[name]
        if not isinstance(obj, list):
            return obj  # if not list, just return it
        return Lenient.from_list(obj)

    def __str__(self):
        return "" if not len(self) else super(Lenient, self).__str__()

    def __eq__(self, other):
        if other is None:
            return False if len(self) else True
        else:
            return NotImplemented

    def __missing__(self, key):
        return Lenient()

    def __iter__(self):
        if self.as_list:
            return iter(self.as_list)
        return super().__iter__()


def loads(string):
    return json.loads(string, object_hook=Lenient)


if __name__ == "__main__":
    test_json = """
    { "a":
        {"b":
            [
                {"c": "d"},
                {"c": 5},
                ["i", "j", "k"]
            ],
         "b2": [],
         "b3": [{"c": "d"}],
         "b4": true,
         "b5": false
        }
    }
    """
    l = loads(test_json)
    assert type(l) == Lenient
    assert type(l["a"]) == Lenient
    assert type(l.a) == Lenient
    assert type(l.a.b.last) == Lenient
    assert type(l.a.X.last) == Lenient
    assert type(l.a.b.first.c) == str
    assert type(l.a.b[1].c) == int
    assert l.a.b.get(1).c == 5
    assert l.a.b.last.first == "i"
    assert l.a.b.first.c == "d"
    assert l.a.b[0].c == "d"
    assert not l.a.X.last
    assert l.a.X.doesnt.exist != True
    assert l.a.X.doesnt.exist == None
    assert l.a.b != None
    assert l.a.b2.last == None
    assert str(l.a.b2.last) == ""
    assert str(l.a.b3.last) == str({"c": "d"})
    assert l.a.b.last.last == "k"
    assert l.a.b.first == {"c": "d"}
    assert dict(l.a.b.first) == {"c": "d"}
    assert l.a.b.last.as_list == ["i", "j", "k"]
    assert list(l.a.b.last) == ["i", "j", "k"]
    assert list(l.a.b3) == [{"c": "d"}]
    assert l.a.b4 == True
    assert l.a.b5 == False
