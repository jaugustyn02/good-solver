private_key = 583654

def encode_int(num: int, private_key=private_key) -> str:
    encoded_result = num ^ private_key
    
    rotation_count = sum(int(digit) for digit in str(encoded_result)) % len(str(encoded_result))
    encoded_result = str(encoded_result)[-rotation_count:] + str(encoded_result)[:-rotation_count]
    return encoded_result

def decode_int(encoded_num: str, private_key=private_key) -> int:
    rotation_count = sum(int(digit) for digit in str(encoded_num)) % len(encoded_num)
    encoded_num = int(encoded_num[rotation_count:] + encoded_num[:rotation_count])
    
    decoded_result = encoded_num ^ private_key
    return decoded_result