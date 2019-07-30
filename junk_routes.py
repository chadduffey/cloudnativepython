



def rev_str(thing):
    return "".join(reversed(thing))

def is_palindrome(word):
    return word == "".join(reversed(word))


def get_catfacts():
    try:
        r = requests.get('https://cat-fact.herokuapp.com/facts')
        print(r.json())
    except:
        return "failed to get cat fact"

def get_longest_prefix(words):
    print(words)
    longest = ""
    if not words:
        return longest
    shortest_string = min(words, key=len)
    print(shortest_string)
    for i in range(len(shortest_string)):
        if all([x.startswith(shortest_string[:i+1]) for x in words]):
            longest = shortest_string[:i+1]
        else:
            break
    return longest


def convert_roman(roman):
    values = {'I':1, 'V' : 5, 'X' : 10, 'L' : 50, 'C' : 100, 'D' : 500, 'M': 1000}
    int_val = 0
    for i in range(len(roman)):
        if i > 0 and values[roman[i]] > values[roman[i - 1]]:
            int_val += values[roman[[i]]] - 2 * values[roman[i - 1]]
        else:
            int_val += values[roman[i]]
    return int_val





@app.route('/api/v2/reverse_string/<string:thing>', methods=['GET'])
def reverse_string(thing):
    return jsonify({'backwards': rev_str(thing)})

@app.route('/api/v2/palindrome/<string:word>',methods=['GET'])
def palindrome(word):
    return jsonify({'is_palindrome': is_palindrome(word)})

@app.route('/api/v2/catfacts', methods=['GET'])
def weather():
    cf = get_catfacts()
    return jsonify(cf, 200)

@app.route('/api/v2/longestprefix', methods=['POST'])
def longestprefix():
    if not request.json or not 'words' in request.json:
        abort(400)
    print(request.json['words'])
    return jsonify({'longest_prefix': get_longest_prefix(request.json['words'])})

@app.route('/api/v2/roman/<string:roman>', methods=['GET'])
def get_roman(roman):
    return jsonify({'number': convert_roman(roman)})