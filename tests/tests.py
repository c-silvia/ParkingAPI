# import random
#
# chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# nums = '0123456789'
# letters = ''
# numbers = ''
# quantity = 36
# for c in range(3):
#     letters += random.choice(chars)
#
# for c in range(4):
#     numbers += random.choice(nums)
#
# for i in range(quantity):
#     print(''.join([random.choice(chars) for i in range(1)]+["-"]+[random.choice(nums) for i in range(3)]+["-"]+[random.choice(chars) for i in range(2)]))
#
# print(random.sample(range(1, 100), 2))

# from re import compile
# license_plate_format = compile(r'^[a-zA-Z0-9]{1-3}-[A-Z0-9]{1-3}-[A-Z0-9]{1-3}$')
#     if license_plate_format.match(license_plate):
#         print("Correct plate")
#     else:
#         print("Incorrect plate")