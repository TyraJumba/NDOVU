# NDOVU

**NDOVU** is a Swahili-inspired programming language project designed for native Swahili speakers who experience difficulties with English. The project aims to embrace Africanacity and promote technology through language.

NDOVU is the language users will write programs in. **Python** is being used to implement the tools that process and run NDOVU programs.

## Why NDOVU?

Many programming languages and learning resources use English keywords and explanations. NDOVU explores how familiar Swahili-inspired language can support people who find English a barrier to engaging with programming. The project also celebrates African identity and encourages wider participation in technology.

## Project goals

- Design an original, small programming language inspired by Swahili.
- Define NDOVU's purpose, intended users, keywords, operators, literals, and syntax.
- Support the core programming concepts required for the project: variables, output, conditions, and repetition.
- Build a lexer, parser, program representation (AST or parse tree), semantic checks, and interpreter in Python.
- Test valid programs and meaningful lexical, syntax, and semantic errors.
- Explain and demonstrate the complete path from source code to program output.

## Language design

The vocabulary and syntax below are an **initial proposal** and should be confirmed by the project group, including spelling and intended meanings, before being treated as the final NDOVU specification.

| Concept | Proposed word |
|---|---|
| Variable assignment | `WEKA` |
| Output | `ONYESHA` |
| Conditional | `KAMA` |
| Alternative branch | `LAKINI` |
| Repeat | `RUDIA` |
| While / during | `WAKATI` |
| True | `KWELI` |
| False | `SIKWELI` |
| End a block | `MWISHO` |

The lexer starter also recognizes proposed logical words `NA`, `AU`, and `SIO`. The group should agree on the final keyword list and complete the operator, literal, identifier, delimiter, and grammar rules in the language specification.

## Example program

This illustrates the **proposed** syntax currently used in the lexer example. It is a tokenization example; a complete parser and interpreter are still required before it can be executed as an NDOVU program.

```text
WEKA umri = 20
KAMA umri >= 18
  ONYESHA "Mtu mzima"
MWISHO
```

## How the language pipeline works

```text
NDOVU source program
        ↓
Lexer: groups characters into lexemes and tokens
        ↓
Parser: checks the token sequence against NDOVU grammar
        ↓
AST or parse tree: represents program structure
        ↓
Semantic checks: checks meaning, including variable use
        ↓
Interpreter: executes a valid program
        ↓
Program output
```

## Implementation

- **Implementation language:** Python
- **External dependencies:** None required for the current lexer starter
- **Current repository contents:** lexer, token specification, lexer tests, and sample inputs; parser and interpreter files are placeholders for future implementation

## Getting started

Use Python 3.10 or newer. Clone or download the repository, then run commands from its root directory.

### Tokenize an example

```bash
python src/lexer.py examples/valid/demo.kis
```

The lexer prints each token's category, lexeme, and source location. It reports lexical errors, such as an illegal character, with a location.

### Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project requirements and deliverables

The project brief asks the group to design and implement a small language, including at least eight keywords; operators, literals, and delimiters; syntax for variables, output, conditions, and repetition; and at least ten sample programs. The implementation work includes token definitions and patterns, a lexer, grammar rules, a parser, an AST or parse tree, basic semantic checks, and an interpreter. The team should also prepare tests, a technical report, and a live demonstration.

The required project stages are:

1. **Design:** language purpose, target users, name, initial specification, and ten example programs.
2. **Lexical analysis:** token categories and patterns, lexer, tests, and token-stream examples.
3. **Syntax analysis:** at least eight meaningful grammar rules, parser, syntax tests, and an AST or parse-tree example.
4. **Semantics and execution:** variable storage, expression evaluation, output, conditions, repetition, and checks such as undeclared-variable errors.
5. **Integration and demonstration:** combine the stages, test valid and invalid programs, document the repository, and explain the full pipeline.

## Repository structure

```text
NDOVU/
├── README.md
├── docs/
│   ├── project-checklist.md
│   ├── sample-token-stream.txt
│   └── token-spec.md
├── src/
│   ├── interpreter.py
│   ├── lexer.py
│   └── parser.py
├── examples/
│   ├── invalid/
│   └── valid/
└── tests/
    └── test_lexer.py
```

As development continues, add the final language specification, grammar, ten or more sample programs, parser and interpreter tests, execution examples, and report materials.

## Testing and demonstration plan

The final demonstration should include:

- A variable declaration or assignment and arithmetic expression.
- A conditional statement.
- A repetition construct.
- At least one lexical error and one syntax error.
- An explanation of how the lexer, parser, and interpreter handle the example programs.

The project should also show at least five complete valid programs and at least three different error cases.

## Contributing

This is a group project. Group members should coordinate language-design decisions, implementation, testing, and documentation so that everyone can explain how NDOVU works. Add contributors and their contributions through the GitHub repository and project report.

## Acknowledgements

List any external code, libraries, tutorials, or AI assistance used by the group, following the course's acknowledgement requirements.

## Project status

This repository is a starting point for NDOVU. The current lexer is a starter implementation; the proposed vocabulary and example syntax must be reviewed by the group. The parser, AST or parse tree, semantic checks, interpreter, complete program set, and final demonstration materials remain to be completed by the project team.

