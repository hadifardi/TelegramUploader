#create unique id
import random

characters = 'MLCSfmrK4wVzTtQv3d9ins1kERZX8UD6W2uoHA7B5blcP0JqejOphyIYgaNFxG'

def gen(length=8) -> str:
    'Generates a random id of any length '
    emp_str = ''
    for _ in range(length):
        rand = random.choice(characters)
        emp_str += rand
    return emp_str
