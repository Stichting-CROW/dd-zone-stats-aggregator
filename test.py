test_dict = {
            "moped": 3,
            "cargo_bicycle": 5,
            "bicycle": 0,
            "car": 0,
            "other": 4444
        }
print(test_dict)

for k, v in test_dict.items():
    if v > 0:
        test_dict[k] = 9999


print(test_dict)
