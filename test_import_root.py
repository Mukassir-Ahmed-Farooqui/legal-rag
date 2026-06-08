import traceback

try:
    import src.api.main
    print("Import successful!")
except Exception as e:
    with open("crash2.txt", "w") as f:
        f.write(traceback.format_exc())
    print("Crash recorded.")
