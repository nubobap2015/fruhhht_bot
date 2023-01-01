import semantic

print(''.join(semantic.get_ya_lemmas('мама мыла раму')))

a = semantic.my_vectorizer(semantic.get_ya_lemmas('мама мыла раму'))
print(a)

