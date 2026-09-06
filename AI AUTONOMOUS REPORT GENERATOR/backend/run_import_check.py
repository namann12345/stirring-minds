import importlib
mods=['fastapi','pandas','pymongo','motor','openai','groq']
for m in mods:
    try:
        importlib.import_module(m)
        print(m, 'OK')
    except Exception as e:
        print(m, 'FAILED:', type(e).__name__, str(e))
