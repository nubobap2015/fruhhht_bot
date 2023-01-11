import semantic

print(''.join(semantic.get_ya_lemmas('Выпьем')))

a = semantic.my_vectorizer(semantic.get_ya_lemmas('Выпьем'))
print(a)

