import pickle

width, height = 107, 48
positions = []

# Create a grid of parking spaces across the image
for row in range(6):
    for col in range(10):
        x = 150 + col * (width + 10)
        y = 150 + row * (height + 15)
        positions.append((x, y))

with open("CarParkPos", "wb") as f:
    pickle.dump(positions, f)

print(f"Created {len(positions)} parking positions")