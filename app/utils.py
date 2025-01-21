import random
import string
from django.contrib.auth import get_user_model


User = get_user_model()

def generate_random_username(length, max_attempts=100):
    for _ in range(max_attempts):
        random_username = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
        if not User.objects.filter(username=random_username).exists():
            return random_username
    raise ValueError('Could not generate a unique username after {} attempts'.format(max_attempts))

random_username = generate_random_username(6)
# print(random_username)



