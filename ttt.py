def parse_string(input_string):
    # Split the input string by space
    input_string = input_string.replace(' ', ' ')
    parts = input_string.split()

    parts_formatted = []
    actual_salary = ''
    for part in parts:
        try:
            int(part)
            actual_salary += part
        except:
            if actual_salary:
                parts_formatted.append(actual_salary)
            actual_salary = ''
            parts_formatted.append(part)

    parts = parts_formatted

    # Initialize variables with empty strings
    from_value = ''
    up_to_value = ''
    currency = ''

    # Check the parts of the string and assign values accordingly
    if 'от' in parts:
        from_index = parts.index('от') + 1
        from_value = parts[from_index]

    if 'до' in parts:
        up_to_index = parts.index('до') + 1
        up_to_value = parts[up_to_index]

    if '-' in parts or '–' in parts:
        hyphen_index = parts.index('-')
        from_value = parts[hyphen_index - 1] if not from_value else from_value
        up_to_value = parts[hyphen_index + 1]

    # Find the currency in the last part of the string
    if parts:
        currency = parts[-1]

    return from_value.strip(), up_to_value.strip(), currency.strip()


# Test cases
string1 = 'до 123 456 ₽'
string2 = 'от 123 456 $'
string3 = '1 500 – 2 000 $'

from1, up_to1, currency1 = parse_string(string1)
from2, up_to2, currency2 = parse_string(string2)
from3, up_to3, currency3 = parse_string(string3)

# print(f"From: {from1}, Up To: {up_to1}, Currency: {currency1}")
# print(f"From: {from2}, Up To: {up_to2}, Currency: {currency2}")
print(f"From: {from3}, Up To: {up_to3}, Currency: {currency3}")
