import re

# Token Types
TOKEN_KEYWORD = 'KEYWORD'
TOKEN_IDENTIFIER = 'IDENTIFIER'
TOKEN_NUMBER = 'NUMBER'
TOKEN_STRING = 'STRING'
TOKEN_ASSIGN = 'ASSIGN'
TOKEN_OP = 'OPERATOR'
TOKEN_EOF = 'EOF'

KEYWORDS = {
    'WEKA', 'ONYESHA', 'KAMA', 'VINGINEVYO', 
    'RUDIA', 'WAKATI', 'MWISHO', 'KWELI', 'UONGO'
}

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, Line: {self.line}, Col: {self.column})"

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.length = len(source_code)

    def error(self, message):
        raise LexerError(f"Lexical Error: {message} at line {self.line}, column {self.column}")

    def advance(self):
        if self.position < self.length:
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def peek(self):
        if self.position + 1 < self.length:
            return self.source[self.position + 1]
        return None

    def current_char(self):
        if self.position < self.length:
            return self.source[self.position]
        return None

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char() in ' \t\r':
            self.advance()

    def skip_comment(self):
        # Optional: Support comments starting with '#'
        if self.current_char() == '#':
            while self.current_char() is not None and self.current_char() != '\n':
                self.advance()

    def tokenize_number(self):
        start_col = self.column
        num_str = ''
        while self.current_char() is not None and self.current_char().isdigit():
            num_str += self.current_char()
            self.advance()
        return Token(TOKEN_NUMBER, int(num_str), self.line, start_col)

    def tokenize_identifier_or_keyword(self):
        start_col = self.column
        ident_str = ''
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            ident_str += self.current_char()
            self.advance()
        
        token_type = TOKEN_KEYWORD if ident_str in KEYWORDS else TOKEN_IDENTIFIER
        return Token(token_type, ident_str, self.line, start_col)

    def tokenize_string(self):
        start_col = self.column
        self.advance() # Skip opening quote
        string_val = ''
        while self.current_char() is not None and self.current_char() != '"':
            if self.current_char() == '\n':
                self.error("Unterminated string literal across lines")
            string_val += self.current_char()
            self.advance()
        
        if self.current_char() is None:
            self.error("Unterminated string literal")
        
        self.advance() # Skip closing quote
        return Token(TOKEN_STRING, string_val, self.line, start_col)

    def make_tokens(self):
        tokens = []
        while self.current_char() is not None:
            char = self.current_char()

            if char in ' \t\r':
                self.advance()
                continue
            if char == '\n':
                self.advance()
                continue
            if char == '#':
                self.skip_comment()
                continue

            # Numbers
            if char.isdigit():
                tokens.append(self.tokenize_number())
                continue

            # Identifiers & Keywords
            if char.isalpha() or char == '_':
                tokens.append(self.tokenize_identifier_or_keyword())
                continue

            # Strings
            if char == '"':
                tokens.append(self.tokenize_string())
                continue

            # Multi-character Operators
            if char == '=' and self.peek() == '=':
                start_col = self.column
                self.advance()
                self.advance()
                tokens.append(Token(TOKEN_OP, '==', self.line, start_col))
                continue
            if char == '!' and self.peek() == '=':
                start_col = self.column
                self.advance()
                self.advance()
                tokens.append(Token(TOKEN_OP, '!=', self.line, start_col))
                continue
            if char == '>' and self.peek() == '=':
                start_col = self.column
                self.advance()
                self.advance()
                tokens.append(Token(TOKEN_OP, '>=', self.line, start_col))
                continue
            if char == '<' and self.peek() == '=':
                start_col = self.column
                self.advance()
                self.advance()
                tokens.append(Token(TOKEN_OP, '<=', self.line, start_col))
                continue

            # Single-character Operators & Assign
            if char in '+-*/><=':
                start_col = self.column
                t_type = TOKEN_ASSIGN if char == '=' else TOKEN_OP
                tokens.append(Token(t_type, char, self.line, start_col))
                self.advance()
                continue
# Delimiters (Braces and Parentheses)
            if char in '{}()':
                start_col = self.column
                tokens.append(Token('DELIMITER', char, self.line, start_col))
                self.advance()
                continue
            # Lexical Error: Illegal character encountered (e.g., @, $, %)
            self.error(f"Illegal character '{char}'")

        tokens.append(Token(TOKEN_EOF, 'EOF', self.line, self.column))
        return tokens