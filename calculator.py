#!flask/bin/python

from flask import Flask, jsonify, abort, make_response, request, render_template
import socket
import string
from math import *
import difflib


app = Flask(__name__)


@app.route('/')
def greeting():
    return jsonify({'welcome': u' try going to /calculator'});


@app.route('/user', methods=['GET'])
def print_user():
    return jsonify({'user': socket.gethostname()});


@app.errorhandler(404)
def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/calculator')
def calculator_input():
    return render_template('layout.html', text={})


@app.route('/calculator', methods=['POST'])
def calculator():
    text = request.form['text']
    output = calculate(str(text))
    return render_template('layout.html', text=output)

def isnumeric(val):
    if(val[0] == "-"):
        val = val[1:]
        return val.replace(".","",1).isdigit()
    else:
        return val.replace(".","",1).isdigit()

def calculate_function(func, arg):
    if(func == 'sin'):
        return sin(arg)
    elif(func == 'cos'):
        return cos(arg)
    elif(func == 'tan'):
        return tan(arg)
    elif(func == 'arcsin'):
        return asin(arg)
    elif(func == 'arccos'):
        return acos(arg)
    elif(func == 'arctan'):
        return atan(arg)
    elif(func == 'exp'):
        return exp(arg)
    elif(func == 'log'):
        return log10(arg)
    elif(func == 'ln'):
        return log(arg)
    elif(func == 'sqrt'):
        return sqrt(arg)
    elif(func[0:2] == "rt"):
        base = float(func[2:])
        return pow(float(arg), 1./base)
    elif(func[0:3] == "log"):
        base = float(func[3:])
        return log(float(arg), base)

def calculate_recursive(op_parts):
    if(type(op_parts) is dict):
        return op_parts

    basicOperations = "+-*/!^"
    legalFunctions = ['sin', 'cos', 'tan', 'arcsin', 'arctan', 'arctan', 'exp', 'log', 'ln', 'sqrt']

    for i in range(len(op_parts)):

        if(i > len(op_parts) - 1):
            break

        if(i == 0):
            if(op_parts[i] == "+"):
                return calculate_recursive(op_parts[1:])

        if(op_parts[i] in legalFunctions or op_parts[i][0:2] == "rt" or op_parts[i][0:3] == "log" or op_parts[i] == "(" ):
            deep = 0
            up_limit = 0
            ini = i
            if(op_parts[i] in legalFunctions or op_parts[i][0:2] == "rt" or op_parts[i][0:3] == "log"):
                ini = i + 1
            for j in range(ini,len(op_parts)):
                if(op_parts[j] == '('):
                    deep = deep + 1
                elif(op_parts[j] == ')'):
                    deep = deep - 1

                if(deep == 0):
                    up_limit = j
                    break

            arg = calculate_recursive(op_parts[ini+1:up_limit])
            if(type(arg) is dict):
                return arg
            
            if(op_parts[i] in legalFunctions or op_parts[i][0:2] == "rt" or op_parts[i][0:3] == "log"):
                val = str(calculate_function(op_parts[i], float(arg)))
                del op_parts[i:(up_limit+1)]
                op_parts.insert(i ,val)
            elif(op_parts[i] == "("):
                del op_parts[i:(up_limit+1)]
                op_parts.insert(i ,arg)

    # Check basic operations order
    for i in range(len(op_parts)):
        if(op_parts[i] in basicOperations and op_parts[i+1] in basicOperations):
            return {"Error": "Wrong expression formating!"}


    # Negative number at the beginning
    if(op_parts[0] == "-"):
        if(isnumeric(op_parts[1])):
            new_val = str(-float(op_parts[1]))
            del op_parts[0:2]
            op_parts.insert(0, new_val)

    # Pre-calculate factorials
    while("!" in op_parts):
        idx = op_parts.index("!")
        val = str(factorial(int(float(op_parts[idx-1]))))
        del op_parts[idx-1:idx+1]
        op_parts.insert(idx-1,val)

    # Pre-calculate exponenets
    while("^" in op_parts):
        idx = op_parts.index("^")
        val = str(pow(float(op_parts[idx-1]), float(op_parts[idx+1])))
        del op_parts[idx-1:idx+2]
        op_parts.insert(idx-1,val)

    # Calculate * and /
    while("*" in op_parts or "/" in op_parts):
        idx_m = len(op_parts) + 1
        idx_d = len(op_parts) + 1
        if("*" in op_parts):
            idx_m = op_parts.index("*")
        if("/" in op_parts):
            idx_d = op_parts.index("/")
        if(idx_m < idx_d):
            val = str(float(op_parts[idx_m-1]) * float(op_parts[idx_m+1]))
            del op_parts[idx_m-1:idx_m+2]
            op_parts.insert(idx_m-1,val)
        else:
            if(float(op_parts[idx_d+1]) == 0.):
               return {"Worning": "Division by zero!"}

            val = str(float(op_parts[idx_d-1]) / float(op_parts[idx_d+1]))
            del op_parts[idx_d-1:idx_d+2]
            op_parts.insert(idx_d-1,val)
        
    # Calculate + and -
    while("+" in op_parts or "-" in op_parts):
        idx_sum = len(op_parts) + 1
        idx_sub = len(op_parts) + 1
        if("+" in op_parts):
            idx_sum = op_parts.index("+")
        if("-" in op_parts):
            idx_sub = op_parts.index("-")
        if(idx_sum < idx_sub):
            val = str(float(op_parts[idx_sum-1]) + float(op_parts[idx_sum+1]))
            del op_parts[idx_sum-1:idx_sum+2]
            op_parts.insert(idx_sum-1,val)
        else:
            val = str(float(op_parts[idx_sub-1]) - float(op_parts[idx_sub+1]))
            del op_parts[idx_sub-1:idx_sub+2]
            op_parts.insert(idx_sub-1,val)

    return op_parts[0]

def calculate(text):
    # remove empty spaces
    text = text.replace(" ", "")
    text = text.lower()

    output = text

    if(len(text) == 0):
        return {"Error": "No input"}

    elif("help" in text):
        if(text == "help"):
            help_text = """Here you can do basic operations like summation (+), subtraction (-), multiplication (*) and division (/).
                        <br>Prioritize operations by using parenthesis '(' and ')'.
                        <br><br>Other operations are also available:
                        <br>
                        <br><b>Trigonometric functions</b>
                        <br>Sine: sin(...)
                        <br>Cosine: cos(...)
                        <br>Tangent: tan(...)
                        <br>Inverse sine: arcsin(...)
                        <br>Inverse cosine: arccos(...)
                        <br>Inverse tangent: arctan(...)
                        <br>
                        <br><b>Exponent function</b>
                        <br>Exponent: exp(...)
                        <br>General exponent: ^
                        <br>
                        <br><b>Logaritmic function</b>
                        <br>Natural logarithm: ln(...)
                        <br>Base 10 logarithm: log(...)
                        <br>Generic base logarithm: log2(...), log5(...), ...
                        <br>
                        <br><b>Other functions:</b>
                        <br>Factorial: ...!
                        <br>Squared root: sqrt(...)
                        <br>General root: rt3(...), rt4(...), ...
                        <br>
                        <br><b>Constants</b>
                        <br>Pi: <b>pi</b> (3.14159265359)
                        <br>Euler constant: <b>e</b> (2.7182818285)
                        <br>Golden ratio: <b>gold</b> (1.6180339887)
                        <br>
                        <br><b>Example of valid operations:</b>
                        <br>cos(pi/2)+exp(cot(2)*3)
                        <br>-((sqrt(3)/e)-(2^3))
                        """

            return {"Help": help_text}
        else:
            return {"Help": "Did you mean 'help'?"}
    else:

        # **************************************************************************************
        # ******************************** Evaluate operation **********************************
        # **************************************************************************************
            

        # READ INPUT AND SEGMENT INTO LOGICAL PARTS

        basicOperations = "+-*/!^"
        legalSymbols = "!()+-*/^."
        legalFunctions = ['sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'exp', 'log', 'ln', 'sqrt']
        legalConstantsDict = {
            "pi": "3.14159265359",
            "e": "2.7182818285",
            "gold": "1.6180339887"
        }

        readingString = False
        readingNumber = False
        readingSymbol = False

        if(text[0].isdigit()):
            readingNumber = True
        elif(text[0].isalpha()):
            readingString = True
        elif(text[0] in legalSymbols):
            readingSymbol = True

        op_parts = []
        accum = ''

        for i in range(len(text)):

            # ************* DIGITS ***************
            if(text[i].isdigit()):
                if(readingNumber):
                    accum = accum + text[i]
                
                # Any order root
                elif(accum[0:2] == 'rt'):
                    accum = accum + text[i]
                    readingString = False
                    readingNumber = False
                    readingSymbol = False

                # Any order log
                elif(accum[0:3] == 'log'):
                    accum = accum + text[i]
                    readingString = False
                    readingNumber = False
                    readingSymbol = False

                else:
                    op_parts.append(accum)
                    accum = text[i]
                    readingString = False
                    readingSymbol = False
                    readingNumber = True

            # ************* SYMBOLS ***************
            elif(text[i] in legalSymbols):
                if(text[i] == '.'):
                    if(readingNumber and text[i-1].isdigit()):
                        accum = accum + '.'
                    elif(not(readingNumber)):
                        op_parts.append(accum)
                        accum = '0.'
                        readingNumber = True
                        readingString = False
                        readingSymbol = False

                elif(text[i] == '(' or text[i] == ')' or text[i] == '!' or text[i] == '+' or text[i] == '-'):
                    op_parts.append(accum)
                    op_parts.append(text[i])
                    accum = ''
                    readingString = False
                    readingNumber = False
                    readingSymbol = True

                else:
                    if(readingSymbol):
                        accum = accum + text[i]
                    else:
                        op_parts.append(accum)
                        accum = text[i]
                        readingString = False
                        readingNumber = False
                        readingSymbol = True

            # ************* STRING ***************
            elif(text[i].isalpha()):
                if(readingString):
                    accum = accum + text[i]
                else:
                    op_parts.append(accum)
                    accum = text[i]
                    readingString = True
                    readingNumber = False
                    readingSymbol = False


        op_parts.append(accum)

        op_parts[:] = (value for value in op_parts if value != '')

        # Check if operations are legal and order of parenthesis
        deep = 0
        for i in range(len(op_parts)):
            if(op_parts[i] == '('):
                deep = deep + 1
            elif(op_parts[i] == ')'):
                deep = deep - 1

            if(op_parts[i].isalpha()):
                if(op_parts[i] in legalConstantsDict.keys()):
                    op_parts[i] = legalConstantsDict[op_parts[i]]

                elif(op_parts[i] in legalFunctions):
                    if(i < len(op_parts) - 1):
                        if(op_parts[i+1] != "("):
                            return {"Error": "Function '" + op_parts[i] + "' expects an open parenthesis to hold the input. Try '" + op_parts[i] + "(...)'."}

                elif(not(op_parts[i] in legalFunctions) and not(op_parts[i] in legalConstantsDict.keys())):
                    closest = difflib.get_close_matches(op_parts[i], legalFunctions + legalConstantsDict.keys(), 1)
                    if(not closest):
                        text_answer = "'" + op_parts[i] + "' not recognized!"
                    else:
                        text_answer = "'" + op_parts[i] + "' not recognized!<br>Did you mean '" + closest[0] + "' ?"
                    return {"Error": text_answer}

        if(deep > 0):
            # return {"Warning": "Did you mean: "+ text + ")"*deep}
            output = output + ")"*deep
            output = "Warning! Assuming you meant: " + output + "<br><br>" + output
            for i in range(deep):
                op_parts.append(")")

        elif(deep < 0):
            # return {"Error": "Wrong parenthesis closing!"}
            output = "("*(-deep) + output
            output = "Warning! Assuming you meant: " + output + "<br><br>" + output
            for i in range(-deep):
                op_parts.insert(0, "(")

        # LOGIC FOR CALCULATING EXPRESSION
        ans = calculate_recursive(op_parts)
        if(type(ans) is dict):
            return ans
        else:
            output = output + " = " + ans
            return {"Result": output}
        



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

