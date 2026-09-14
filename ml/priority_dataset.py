import csv
import random

output_file = "ml/priority_training_data.csv"

categories = [
    "Assault",
    "Harassment",
    "Medical Emergency",
    "Accident",
    "Suspicious Activity",
    "Unsafe Location",
    "Threat",
    "Other"
]

locations = [
    "Road",
    "Hostel",
    "College",
    "Bus Stop",
    "Railway Station",
    "Market",
    "Park",
    "Residential Area"
]

priority_rules = {
    "CRITICAL": [
        ("Threat", 5, 5),
        ("Assault", 5, 5),
        ("Medical Emergency", 5, 5),
    ],
    "HIGH": [
        ("Threat", 4, 4),
        ("Harassment", 4, 4),
        ("Accident", 4, 4),
        ("Assault", 4, 4),
    ],
    "MEDIUM": [
        ("Harassment", 3, 3),
        ("Suspicious Activity", 3, 3),
        ("Accident", 3, 3),
        ("Unsafe Location", 3, 3),
    ],
    "LOW": [
        ("Unsafe Location", 1, 1),
        ("Other", 1, 1),
        ("Suspicious Activity", 1, 1),
    ]
}

rows = []

for _ in range(1000):

    category = random.choice(categories)
    location = random.choice(locations)

    severity = random.randint(1, 5)
    urgency = random.randint(1, 5)

    if severity >= 5 and urgency >= 5:
        priority = "CRITICAL"

    elif severity >= 4 and urgency >= 4:
        priority = "HIGH"

    elif severity >= 3 or urgency >= 3:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    rows.append([
        category,
        location,
        severity,
        urgency,
        priority
    ])


with open(output_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Category",
        "Location",
        "Severity",
        "Urgency",
        "Priority"
    ])

    writer.writerows(rows)


print("=" * 45)
print("SAFESHIELD AI PRIORITY DATASET CREATED")
print("=" * 45)

print(f"Total records: {len(rows)}")

print("\nPriority distribution:")

counts = {}

for row in rows:

    priority = row[4]

    counts[priority] = counts.get(priority, 0) + 1

for priority, count in counts.items():

    print(f"{priority}: {count}")

print("\nFirst 10 records:")

for row in rows[:10]:

    print(row)