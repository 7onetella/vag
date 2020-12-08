import hashlib

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!


def sha1sum(file_path):
    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


# print(sha1sum("/Users/seos/.vagrant/boxes/7onetella/password/package.box"))