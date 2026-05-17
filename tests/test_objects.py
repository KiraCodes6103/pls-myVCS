from core.objects import hash_object, read_object

def test_hash_and_read_blob():
    sha = hash_object(b'hello world', 'blob', '.')
    object_type, content = read_object(sha, '.')

    assert object_type == 'blob'
    assert content == b'hello world'
