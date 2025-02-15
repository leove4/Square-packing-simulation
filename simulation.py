import random, math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.widgets import TextBox, Button

# Default settings
default_container_area = 100.0    # 100 means a 10x10 container
default_max_failures = 20000
default_attempts_per_frame = 1
default_rearr_attempts_per_frame = 1000
default_trans_step = 0.4
default_rot_step = 0.4
s = 1.0  # Each square is 1x1

# Global simulation variables (updated from UI)
container_area = default_container_area
L_container = math.sqrt(container_area)
max_failures = default_max_failures
attempts_per_frame = default_attempts_per_frame
rearr_attempts_per_frame = default_rearr_attempts_per_frame
trans_step = default_trans_step
rot_step = default_rot_step

failure_count = 0
positions = []  # List of squares (each is (center_x, center_y, rotation))

# Get vertices of a square
def get_square_vertices(center, theta, s):
    cx, cy = center
    half = s / 2.0
    corners = [(-half, -half), (-half, half), (half, half), (half, -half)]
    vertices = []
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    for dx, dy in corners:
        x = cx + dx * cos_t - dy * sin_t
        y = cy + dx * sin_t + dy * cos_t
        vertices.append((x, y))
    return vertices

# Compute the minimum translation vector to separate two polygons
def compute_MTV(poly1, poly2, tol=0.0):
    mtv_distance = float('inf')
    mtv_axis = None
    for poly in (poly1, poly2):
        n = len(poly)
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i+1) % n]
            edge = (p2[0]-p1[0], p2[1]-p1[1])
            norm = math.hypot(edge[0], edge[1])
            if norm == 0:
                continue
            axis = (-edge[1]/norm, edge[0]/norm)
            proj1 = [p[0]*axis[0] + p[1]*axis[1] for p in poly1]
            proj2 = [p[0]*axis[0] + p[1]*axis[1] for p in poly2]
            min1, max1 = min(proj1), max(proj1)
            min2, max2 = min(proj2), max(proj2)
            overlap = min(max1, max2) - max(min1, min2)
            if overlap <= tol:
                return None
            if overlap < mtv_distance:
                mtv_distance = overlap
                mtv_axis = axis
    center1 = (sum(p[0] for p in poly1)/len(poly1), sum(p[1] for p in poly1)/len(poly1))
    center2 = (sum(p[0] for p in poly2)/len(poly2), sum(p[1] for p in poly2)/len(poly2))
    d = (center2[0]-center1[0], center2[1]-center1[1])
    if d[0]*mtv_axis[0] + d[1]*mtv_axis[1] < 0:
        mtv_axis = (-mtv_axis[0], -mtv_axis[1])
    return (mtv_axis[0]*mtv_distance, mtv_axis[1]*mtv_distance)

# Check if a candidate square is valid (inside container and no overlap)
def square_valid(candidate, positions, L_container, s, exclude_index=None):
    poly = get_square_vertices((candidate[0], candidate[1]), candidate[2], s)
    for (x, y) in poly:
        if x < 0 or x > L_container or y < 0 or y > L_container:
            return False
    for i, pos in enumerate(positions):
        if exclude_index is not None and i == exclude_index:
            continue
        poly2 = get_square_vertices((pos[0], pos[1]), pos[2], s)
        if compute_MTV(poly, poly2, 0.0) is not None:
            return False
    return True

# Generate a candidate using a Gaussian centered in the container
def gaussian_candidate(L_container, s):
    mean = L_container / 2
    sigma = L_container / 4
    while True:
        x = random.gauss(mean, sigma)
        y = random.gauss(mean, sigma)
        if 0 <= x <= L_container and 0 <= y <= L_container:
            break
    theta = random.uniform(0, math.pi/2)
    return (x, y, theta)

# Try to rearrange one square (move it away from the center)
def try_rearrange():
    if not positions:
        return
    i = random.randrange(len(positions))
    old = positions[i]
    new_candidate = (
        old[0] + random.uniform(-trans_step, trans_step),
        old[1] + random.uniform(-trans_step, trans_step),
        (old[2] + random.uniform(-rot_step, rot_step)) % (math.pi/2)
    )
    if square_valid(new_candidate, positions, L_container, s, exclude_index=i):
        cx, cy = L_container/2, L_container/2
        old_dist = (old[0]-cx)**2 + (old[1]-cy)**2
        new_dist = (new_candidate[0]-cx)**2 + (new_candidate[1]-cy)**2
        if new_dist > old_dist:
            positions[i] = new_candidate

# Try to insert a new square using Gaussian candidate
def try_insert():
    global failure_count
    candidate = gaussian_candidate(L_container, s)
    if square_valid(candidate, positions, L_container, s):
        positions.append(candidate)
        failure_count = 0
    else:
        failure_count += 1

# Update simulation for one frame
def update_simulation(frame):
    global failure_count
    for _ in range(rearr_attempts_per_frame):
        try_rearrange()
    for _ in range(attempts_per_frame):
        try_insert()
    if failure_count > max_failures:
        print("No free space. Final count:", len(positions))
        anim.event_source.stop()
    ax_sim.clear()
    ax_sim.set_xlim(0, L_container)
    ax_sim.set_ylim(0, L_container)
    ax_sim.set_aspect('equal')
    ax_sim.add_patch(patches.Rectangle((0,0), L_container, L_container, fill=False, edgecolor='black'))
    for pos in positions:
        poly = get_square_vertices((pos[0], pos[1]), pos[2], s)
        ax_sim.add_patch(patches.Polygon(poly, closed=True, facecolor='blue', edgecolor='blue', alpha=0.8))
    ax_sim.set_title("Squares packed: " + str(len(positions)))
    return ax_sim.patches

# Set up UI
fig = plt.figure(figsize=(8,8))
ax_sim = fig.add_axes([0.1, 0.55, 0.8, 0.35])

# Helper function to add a labeled TextBox
def add_labeled_box(coords, label, initial):
    ax_box = fig.add_axes(coords)
    x, y, w, h = coords
    fig.text(x, y+h+0.005, label, fontsize=10)
    return TextBox(ax_box, "", initial=initial)

text_box_area = add_labeled_box([0.1, 0.40, 0.25, 0.06], "Container Area", str(default_container_area))
text_box_max_fail = add_labeled_box([0.37, 0.40, 0.25, 0.06], "Max Failures", str(default_max_failures))
text_box_attempts = add_labeled_box([0.64, 0.40, 0.25, 0.06], "Attempts/Frame", str(default_attempts_per_frame))
text_box_rearr = add_labeled_box([0.1, 0.30, 0.25, 0.06], "Rearr/Frame", str(default_rearr_attempts_per_frame))
text_box_trans = add_labeled_box([0.37, 0.30, 0.25, 0.06], "Trans Step", str(default_trans_step))
text_box_rot = add_labeled_box([0.64, 0.30, 0.25, 0.06], "Rot Step", str(default_rot_step))

ax_button_start = fig.add_axes([0.1, 0.20, 0.25, 0.08])
ax_button_stop = fig.add_axes([0.37, 0.20, 0.25, 0.08])
ax_button_reset = fig.add_axes([0.64, 0.20, 0.25, 0.08])
button_start = Button(ax_button_start, "Start Simulation")
button_stop = Button(ax_button_stop, "Stop Simulation")
button_reset = Button(ax_button_reset, "Reset Simulation")

anim = None

def start_simulation(event):
    global container_area, L_container, max_failures, attempts_per_frame
    global rearr_attempts_per_frame, trans_step, rot_step, failure_count, positions, anim
    try:
        container_area = float(text_box_area.text)
    except:
        container_area = default_container_area
    L_container = math.sqrt(container_area)
    try:
        max_failures = int(text_box_max_fail.text)
    except:
        max_failures = default_max_failures
    try:
        attempts_per_frame = int(text_box_attempts.text)
    except:
        attempts_per_frame = default_attempts_per_frame
    try:
        rearr_attempts_per_frame = int(text_box_rearr.text)
    except:
        rearr_attempts_per_frame = default_rearr_attempts_per_frame
    try:
        trans_step = float(text_box_trans.text)
    except:
        trans_step = default_trans_step
    try:
        rot_step = float(text_box_rot.text)
    except:
        rot_step = default_rot_step
    failure_count = 0
    positions = []
    text_box_area.set_active(False)
    text_box_max_fail.set_active(False)
    text_box_attempts.set_active(False)
    text_box_rearr.set_active(False)
    text_box_trans.set_active(False)
    text_box_rot.set_active(False)
    button_start.label.set_text("Running...")
    global anim
    anim = FuncAnimation(fig, update_simulation, frames=1000, interval=50, blit=False)
    plt.draw()

def stop_simulation(event):
    global anim
    if anim is not None:
        anim.event_source.stop()
        button_stop.label.set_text("Stopped")

def reset_simulation(event):
    global failure_count, positions, anim
    if anim is not None:
        anim.event_source.stop()
    failure_count = 0
    positions = []
    text_box_area.set_active(True)
    text_box_max_fail.set_active(True)
    text_box_attempts.set_active(True)
    text_box_rearr.set_active(True)
    text_box_trans.set_active(True)
    text_box_rot.set_active(True)
    button_start.label.set_text("Start Simulation")
    button_stop.label.set_text("Stop Simulation")
    plt.draw()

button_start.on_clicked(start_simulation)
button_stop.on_clicked(stop_simulation)
button_reset.on_clicked(reset_simulation)

plt.show()
