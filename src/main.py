from lexer import Lexer, LexerError

def run_file(filepath):
    print(f"=== Reading: {filepath} ===")
    with open(filepath, "r", encoding="utf-8") as file:
        source_code = file.read()

    try:
        lexer = Lexer(source_code)
        tokens = lexer.make_tokens()
        for token in tokens:
            print(f"  {token}")
    except LexerError as e:
        print(f"  [REJECTED] {e}")
    print()

if __name__ == "__main__":
    run_file("examples/valid/test1.nia")
    run_file("examples/invalid/bad_char.nia")