import datetime
import re
import wikipedia

# Single digits and teens
ONES = {
    "zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,
    "six":6,"seven":7,"eight":8,"nine":9,"ten":10,
    "eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,
    "sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,
}

# Tens
TENS = {
    "twenty":20,"thirty":30,"forty":40,"fifty":50,
    "sixty":60,"seventy":70,"eighty":80,"ninety":90,
}

# Multipliers
MULTIPLIERS = {
    "hundred":100,"thousand":1000,"million":1000000,"billion":1000000000,
}

def words_to_numbers(text: str) -> str:
    """
    Converts number words in a string to digits.
    'three plus four'        → '3 plus 4'
    'twenty five times six'  → '25 times 6'
    'two hundred divided by four' → '200 divided by 4'
    """
    tokens = text.lower().split()
    result = []
    i = 0

    while i < len(tokens):
        token = tokens[i]

        # Start of a number word sequence
        if token in ONES or token in TENS or token in MULTIPLIERS:
            num = 0
            current = 0

            while i < len(tokens):
                t = tokens[i]

                if t in ONES:
                    current += ONES[t]
                    i += 1
                elif t in TENS:
                    current += TENS[t]
                    i += 1
                elif t in MULTIPLIERS:
                    multiplier = MULTIPLIERS[t]
                    if multiplier == 100:
                        current *= multiplier
                    else:
                        # e.g. "two hundred thousand" → (current+num)*1000
                        num = (num + current) * multiplier
                        current = 0
                    i += 1
                else:
                    break

            num += current
            result.append(str(num))
        else:
            result.append(token)
            i += 1

    return " ".join(result)


# Prefixes to strip before sending to Wikipedia
_STRIP_PREFIXES = (
    "what is", "what are", "who is", "who are",
    "when is", "where is", "tell me about",
    "search for", "look up",
)

def _clean_query(q: str) -> str:
    q = q.lower().strip()
    for prefix in _STRIP_PREFIXES:
        if q.startswith(prefix):
            q = q[len(prefix):].strip()
            break
    return q

def calculate(command: str) -> str:
    expr = command.lower()

    # Strip natural language wrappers
    for word in ("calculate", "compute", "what is", "what's"):
        expr = expr.replace(word, "")

    # Convert number words to digits FIRST
    expr = words_to_numbers(expr.strip())

    # Replace spoken operators with symbols
    expr = expr.replace("plus", "+")
    expr = expr.replace("minus", "-")
    expr = expr.replace("times", "*")
    expr = expr.replace("multiplied by", "*")
    expr = expr.replace("divided by", "/")
    expr = expr.replace("by", "/")
    expr = expr.strip()

    # Only allow safe math characters
    safe = re.sub(r'[^0-9\+\-\*\/\.\(\)\s]', '', expr).strip()

    if not safe:
        return "I couldn't parse that calculation. Please try again."

    try:
        result = eval(safe)
        # Clean up float results like 4.0 → 4
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return f"The answer is {result}"
    except Exception:
        return "I couldn't compute that. Please try a simpler expression."

def answer_question(q: str) -> str:
    q = q.lower().strip()

    if "time" in q:
        return "The time is " + datetime.datetime.now().strftime("%I:%M %p")

    if "date" in q or "day" in q:
        return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y")

    topic = _clean_query(q)
    if not topic:
        return "Could you be more specific?"

    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(topic, sentences=2, auto_suggest=True)
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            return wikipedia.summary(e.options[0], sentences=2)
        except Exception:
            return f"I found multiple results for {topic}. Could you be more specific?"
    except wikipedia.exceptions.PageError:
        return f"I couldn't find information on {topic}."
    except Exception:
        return "I had trouble fetching that. Try again in a moment."