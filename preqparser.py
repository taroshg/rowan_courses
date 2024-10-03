import re

# thanks to bing chat
class PreqParser():
    """parses prerequisites from Rowan's detailed course information
    """
    def __init__(self, inp: str) -> None:
        self.inp = inp
        self.tokens = re.findall(r'([A-Z]{2,4} \d{5}|\(|\)|or|and)', inp)

        # this is to filter out possible empty parentheses, which raises mismatched parentheses error 
        self.tokens = []
        tokens = re.findall(r'([A-Z]{2,4} \d{5}|\(|\)|or|and)', inp)
        for i in range(len(tokens)):
            if tokens[i] == '(' and tokens[i+1] == ')':
                continue
            if tokens[i] == ')' and tokens[i-1] == '(':
                continue
            self.tokens.append(tokens[i])

        # abstract syntax tree
        self.ast = self.parse()
        
    def parse(self):
        index, ast = self._parse_or(0)
        if index != len(self.tokens):
            raise ValueError(f"Unexpected tokens at the end: {self.inp}")
        return ast

    def _parse_expression(self, index):
        if self.tokens[index] == '(':
            index, node = self._parse_or(index + 1)
            if self.tokens[index] != ')':
                raise ValueError(f"Mismatched parentheses: {self.inp}")
            return index + 1, node
        else:
            return index + 1, self.tokens[index]

    def _parse_and(self, index):
        index, left = self._parse_expression(index)
        while index < len(self.tokens) and self.tokens[index] == 'and':
            index, right = self._parse_expression(index + 1)
            left = ('and', left, right)
        return index, left

    def _parse_or(self, index):
        index, left = self._parse_and(index)
        while index < len(self.tokens) and self.tokens[index] == 'or':
            index, right = self._parse_and(index + 1)
            left = ('or', left, right)
        return index, left


    def evaluate(self, context: dict) -> bool:
        """returns if preqs are vaild, given the courses taken
        Args:
            context: dict where keys are courses, and values is boolean
                example - context = {
                                        'CS 10337': True,
                                        'MIS 02337': False,
                                        'CS 04430': True,
                                        'CS 02435': False,
                                        'CS 10338': True,
                                        'CS 10339': True
                                    }
        Returns:
            True or False of if the context is qualified for this course preq
        """
        if isinstance(self.ast, str):
            return context.get(self.ast, False)
        op, left, right = self.ast
        if op == 'and':
            return self.evaluate(left, context) and self.evaluate(right, context)
        elif op == 'or':
            return self.evaluate(left, context) or self.evaluate(right, context)
        else:
            raise ValueError(f"Unknown operator: {op}")