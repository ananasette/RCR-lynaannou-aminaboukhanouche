import re
from sympy import Symbol, Not, And, Or, Implies, Equivalent, true, false

TOKEN = re.compile(r"\s*(<->|->|[~&|()]|[A-Za-z_]\w*(?:\([^()]*\))?)")


def _tokens(text):
    text, pos, out = text.strip(), 0, []
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError(f"Caractère inconnu près de : '{text[pos:pos + 5].strip()}'")
        out.append(m.group(1))
        pos = m.end()
    return out


class _Parser:
    """Recursive descent. Precedence (low -> high): <->, ->, |, &, ~"""

    def __init__(self, toks):
        self.t, self.i = toks, 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def eat(self, expected=None):
        tok = self.peek()
        if tok is None:
            raise ValueError(f"'{expected}' attendu" if expected else "Formule incomplète")
        if expected and tok != expected:
            raise ValueError(f"'{expected}' attendu, trouvé '{tok}'")
        self.i += 1
        return tok

    def equiv(self):
        left = self.imp()
        while self.peek() == "<->":
            self.eat()
            left = Equivalent(left, self.imp())
        return left

    def imp(self):
        left = self.disj()
        if self.peek() == "->":          # right-associative
            self.eat()
            return Implies(left, self.imp())
        return left

    def disj(self):
        left = self.conj()
        while self.peek() == "|":
            self.eat()
            left = Or(left, self.conj())
        return left

    def conj(self):
        left = self.neg()
        while self.peek() == "&":
            self.eat()
            left = And(left, self.neg())
        return left

    def neg(self):
        if self.peek() == "~":
            self.eat()
            return Not(self.neg())
        return self.atom()

    def atom(self):
        tok = self.peek()
        if tok == "(":
            self.eat()
            f = self.equiv()
            self.eat(")")
            return f
        if tok is None:
            raise ValueError("Formule incomplète : opérande manquant")
        if tok in ("->", "<->", "&", "|", ")"):
            raise ValueError(f"Opérande attendu avant '{tok}'")
        self.eat()
        if tok.lower() == "true":
            return true
        if tok.lower() == "false":
            return false
        return Symbol(re.sub(r"\s+", "", tok))


def lire_formule(text):
    if not text or not text.strip():
        raise ValueError("Formule vide")
    p = _Parser(_tokens(text))
    f = p.equiv()
    if p.peek() is not None:
        raise ValueError(f"Symbole inattendu : '{p.peek()}'")
    return f


def _wrap(f):
    s = afficher_formule(f)
    simple = f.is_Symbol or f in (true, false) or isinstance(f, Not)
    return s if simple else f"({s})"


def afficher_formule(f):
    if f == true:
        return "vrai"
    if f == false:
        return "faux"
    if f.is_Symbol:
        return f.name
    if isinstance(f, Not):
        return "¬" + _wrap(f.args[0])
    ops = {And: " ∧ ", Or: " ∨ ", Implies: " → ", Equivalent: " ↔ "}
    for cls, sym in ops.items():
        if isinstance(f, cls):
            return sym.join(_wrap(a) for a in f.args)
    return str(f)


def variables(formulas):
    noms = set()
    for f in formulas:
        noms |= {a.name for a in f.atoms(Symbol)}
    return sorted(noms)


if __name__ == "__main__":
    for t in ["p -> ~v", "a & b | c", "P(x) <-> Q", "true -> p", "(p & q", "p &", "p $ q"]:
        try:
            print(t, "=>", afficher_formule(lire_formule(t)))
        except ValueError as e:
            print(t, "=> ERREUR:", e)