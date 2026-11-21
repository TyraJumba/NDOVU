# Ndovu Language Grammar Specification (BNF)

This document has the formal Context-Free Grammar (CFG) for Ndovu

## Production Rules

1. `<program>` ::= `<statement_list>` `EOF`

2. `<statement_list>` ::= `<statement>` | `<statement>` `<statement_list>`

3. `<statement>` ::= `<assignment>`
                   | `<output>`
                   | `<conditional>`
                   | `<while_loop>`
                   | `<repeat_loop>`

4. `<assignment>` ::= `"WEKA"` `<identifier>` `"="` `<expression>`

5. `<output>` ::= `"ONYESHA"` `<expression>`

6. `<conditional>` ::= `"KAMA"` `<comparison>` `"{"` `<statement_list>` `"}"`
                     | `"KAMA"` `<comparison>` `"{"` `<statement_list>` `"}"` `"VINGINEVYO"` `"{"` `<statement_list>` `"}"`

7. `<while_loop>` ::= `"WAKATI"` `<comparison>` `"{"` `<statement_list>` `"}"`

8. `<repeat_loop>` ::= `"RUDIA"` `<number>` `"{"` `<statement_list>` `"}"`

9. `<comparison>` ::= `<expression>` `<comp_op>` `<expression>`

10. `<comp_op>` ::= `"=="` | `"!="` | `">"` | `"<"` | `">="` | `"<="`

11. `<expression>` ::= `<term>` ( (`"+"` | `"-"`) `<term>` )*

12. `<term>` ::= `<factor>` ( (`"*"` | `"/"`) `<factor>` )*

13. `<factor>` ::= `<number>`
                 | `<string>`
                 | `<boolean>`
                 | `<identifier>`
                 | `"("` `<expression>` `")"`

14. `<boolean>` ::= `"KWELI"` | `"UONGO"`

<!--
 MEANING OF THE RULES
1. <program>: A complete Ndovu program is just a list of statements that stops at the end of the file (EOF).
2. <statement_list>: A list of statements is either one single line of code, or one line followed by more lines.
3. <statement>: Any valid command in Ndovu must be one of 5 things: a variable, a print statement, an if-statement, a while-loop, or a repeat-loop.
4. <assignment>: To create or update a variable, write WEKA, then a name, then =, then a value (e.g., WEKA umri = 20).
5. <output>: To print something to the screen, write ONYESHA followed by a value or calculation (e.g., ONYESHA "Habari").
6. <conditional>: An if-statement is KAMA, a comparison, and code inside { }. You can optionally add VINGINEVYO (else) with another { } block.
7. <while_loop>: A while-loop is WAKATI, a comparison, and code inside { } that keeps running as long as the comparison is true.
8. <repeat_loop>: A repeat-loop is RUDIA, a number, and code inside { } that runs that exact number of times.
9. <comparison>: A comparison puts a comparison symbol between two values (e.g., alama >= 50).
10. <comp_op>: The only allowed comparison symbols are ==, !=, >, <, >=, and <=.
11. <expression>: Handles addition (+) and subtraction (-).
12. <term>: Handles multiplication (*) and division (/) first to enforce BODMAS.
13. <factor>: The smallest piece of a calculation—either a number, a string, a boolean, a variable name, or another calculation inside parentheses ( ).
14. <boolean>: True or false is written as KWELI or UONGO.
-->