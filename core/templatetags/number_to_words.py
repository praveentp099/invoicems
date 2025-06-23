# core/templatetags/number_to_words.py
from django import template

register = template.Library()

@register.filter
def amount_in_words(value):
    """
    Converts a number to its representation in UAE Dirhams and Fils.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return ""
    
    # Split into dirhams and fils
    dirhams = int(num)
    fils = round((num - dirhams) * 100)
    
    # Handle cases where rounding makes fils 100
    if fils == 100:
        dirhams += 1
        fils = 0
    
    # Convert dirhams to words
    dirhams_str = number_to_words(dirhams) if dirhams > 0 else ""
    # Convert fils to words
    fils_str = number_to_words(fils) if fils > 0 else ""
    
    result = []
    if dirhams_str:
        result.append(f"{dirhams_str} Dirhams")
    if fils_str:
        result.append(f"{fils_str} Fils")
    
    if not result:
        return "Zero Dirhams"
    
    return " and ".join(result)

def number_to_words(n):
    """
    Convert a number to English words (up to millions).
    """
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", 
             "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    if n == 0:
        return "Zero"
    
    def convert_below_thousand(num):
        if num == 0:
            return ""
        elif num < 10:
            return units[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            return tens[num // 10] + (" " + units[num % 10] if num % 10 != 0 else "")
        else:
            return units[num // 100] + " Hundred" + ((" and " + convert_below_thousand(num % 100)) if num % 100 != 0 else "")
    
    # Handle millions
    if n < 1000:
        return convert_below_thousand(n)
    elif n < 1000000:
        return convert_below_thousand(n // 1000) + " Thousand" + ((" " + convert_below_thousand(n % 1000)) if n % 1000 != 0 else "")
    else:
        return convert_below_thousand(n // 1000000) + " Million" + ((" " + convert_below_thousand(n % 1000000)) if n % 1000000 != 0 else "")