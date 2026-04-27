"""
Marching Cube Case Visualizer
==============================

Vertex & Edge Convention (from reference images):
-------------------------------------------------

Vertices (V0–V7):
  Bottom face (Z=0):  V0=(0,0,0), V1=(1,0,0), V2=(1,1,0), V3=(0,1,0)  [wait — see below]
  Top face    (Z=1):  V4=(0,0,1), V5=(1,0,1), V6=(0,1,1), V7=(1,1,1)

  Corrected layout matching the images (Y goes into the screen, X goes right, Z goes up):
    V0 = (0, 0, 0)  bottom-left-front
    V1 = (1, 0, 0)  bottom-right-front
    V2 = (1, 1, 0)  bottom-right-back
    V3 = (0, 1, 0)  bottom-left-back   [V3 appears right-side in image due to perspective]
    V4 = (0, 0, 1)  top-left-front
    V5 = (1, 0, 1)  top-right-front
    V6 = (0, 1, 1)  top-left-back
    V7 = (1, 1, 1)  top-right-back

  The case number encodes which vertices are "high" (above the iso-surface):
    bit 0 → V0, bit 1 → V1, ..., bit 7 → V7
    e.g. case 15 = 0b00001111 means V0,V1,V2,V3 are high.

Edges (E0–E11) — midpoints used for triangle vertices:
  Image 1 (bottom-face edges):
    E0 = midpoint of V0–V1   (bottom front)
    E1 = midpoint of V1–V2   (bottom right)
    E2 = midpoint of V2–V3   (bottom back)
    E3 = midpoint of V3–V0   (bottom left)

  Image 2 (top-face edges):
    E4 = midpoint of V4–V5   (top front)
    E5 = midpoint of V5–V7   (top right)
    E6 = midpoint of V6–V7   (top back)
    E7 = midpoint of V4–V6   (top left)

  Image 3 (vertical/side edges):
    E8  = midpoint of V0–V4  (front-left vertical)
    E9  = midpoint of V1–V5  (front-right vertical)
    E10 = midpoint of V3–V7  (back-left vertical)  [shown on left side in image due to perspective]
    E11 = midpoint of V2–V6  (back-right vertical)

Usage:
  python marching_cube_viz.py <case_number> [edge1 edge2 edge3 ...]

  <case_number>  : integer 0-255 (bits encode which vertices are "high")
  [edge list]    : flat list of edge indices; every 3 form one triangle

Examples:
  # Case 1: only V0 is high, one triangle cutting edges E0, E3, E8
  python marching_cube_viz.py 1 0 3 8

  # Case 15: V0-V3 high, two triangles
  python marching_cube_viz.py 15 0 9 8  3 11 10   [adjust to your actual tables]
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from itertools import combinations

# ── Geometry ──────────────────────────────────────────────────────────────────

# Vertex coordinates: index → (x, y, z)
# X: right, Y: into screen (depth/back), Z: up
VERTICES = np.array([
    [0, 0, 0],  # V0  bottom-front-left
    [1, 0, 0],  # V1  bottom-front-right
    [0, 1, 0],  # V2  bottom-back-left
    [1, 1, 0],  # V3  bottom-back-right
    [0, 0, 1],  # V4  top-front-left
    [1, 0, 1],  # V5  top-front-right
    [0, 1, 1],  # V6  top-back-left
    [1, 1, 1],  # V7  top-back-right
], dtype=float)

# Edge endpoints: edge index → (vertex_a, vertex_b)
# Bottom face: V0=front-left, V1=front-right, V2=back-left, V3=back-right
EDGES = [
    (0, 1),  # E0  — bottom front       (V0–V1)
    (1, 3),  # E1  — bottom right       (V1–V3)
    (3, 2),  # E2  — bottom back        (V3–V2)
    (2, 0),  # E3  — bottom left        (V2–V0)
    (4, 5),  # E4  — top front          (V4–V5)
    (5, 7),  # E5  — top right          (V5–V7)
    (7, 6),  # E6  — top back           (V7–V6)
    (6, 4),  # E7  — top left           (V6–V4)
    (0, 4),  # E8  — vertical front-left  (V0–V4)
    (1, 5),  # E9  — vertical front-right (V1–V5)
    (2, 6),  # E10 — vertical back-left   (V2–V6)
    (3, 7),  # E11 — vertical back-right  (V3–V7)
]

# Cube faces for drawing the wireframe background (each face = 4 vertex indices)
CUBE_FACES = [
    [0, 1, 2, 3],  # bottom
    [4, 5, 6, 7],  # top
    [0, 1, 5, 4],  # front
    [2, 3, 7, 6],  # back
    [0, 3, 7, 4],  # left
    [1, 2, 6, 5],  # right
]

# Cube edges for wireframe
CUBE_EDGES = [
    (0,1),(1,3),(3,2),(2,0),  # bottom ring
    (4,5),(5,7),(7,6),(6,4),  # top ring
    (0,4),(1,5),(2,6),(3,7),  # verticals
]


def edge_midpoint(edge_idx):
    """Return the 3D midpoint of a cube edge."""
    a, b = EDGES[edge_idx]
    return (VERTICES[a] + VERTICES[b]) / 2.0


def parse_args():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    case = int(sys.argv[1])
    edges = [int(x) for x in sys.argv[2:]]

    if len(edges) % 3 != 0:
        print(f"Error: edge list length {len(edges)} is not a multiple of 3.")
        sys.exit(1)

    triangles = []
    for i in range(0, len(edges), 3):
        tri = edges[i:i+3]
        for e in tri:
            if e < 0 or e > 11:
                print(f"Error: edge index {e} is out of range [0, 11].")
                sys.exit(1)
        triangles.append(tri)

    return case, triangles


def high_vertices(case):
    """Return list of vertex indices that are 'high' (above iso-surface)."""
    return [i for i in range(8) if (case >> i) & 1]


# ── Drawing ───────────────────────────────────────────────────────────────────

def draw(case, triangles):
    high = high_vertices(case)
    low  = [i for i in range(8) if i not in high]

    fig = plt.figure(figsize=(10, 8), facecolor='#1a1a2e')
    ax  = fig.add_subplot(111, projection='3d', facecolor='#1a1a2e')

    # ── Cube wireframe ────────────────────────────────────────────────────────
    for a, b in CUBE_EDGES:
        xs = [VERTICES[a][0], VERTICES[b][0]]
        ys = [VERTICES[a][1], VERTICES[b][1]]
        zs = [VERTICES[a][2], VERTICES[b][2]]
        ax.plot(xs, ys, zs, color='#4a4a6a', linewidth=1.2, zorder=1)

    # ── Vertices ──────────────────────────────────────────────────────────────
    OFFSET = 0.07  # label offset from vertex

    for vi, v in enumerate(VERTICES):
        is_high = vi in high
        color  = '#ff6b6b' if is_high else '#4ecdc4'
        marker = 'o'
        size   = 80
        ax.scatter(*v, color=color, s=size, zorder=5, depthshade=False,
                   edgecolors='white', linewidths=0.5)

        # Label offset: push slightly away from cube centre (0.5, 0.5, 0.5)
        centre = np.array([0.5, 0.5, 0.5])
        direction = v - centre
        lp = v + direction * OFFSET + np.array([0, 0, 0.04])
        ax.text(lp[0], lp[1], lp[2],
                f'V{vi}',
                color='white', fontsize=8, fontweight='bold',
                ha='center', va='center', zorder=10)

    # ── Edge midpoints & labels ───────────────────────────────────────────────
    used_edges = sorted(set(e for tri in triangles for e in tri))

    for ei in range(12):
        mp = edge_midpoint(ei)
        if ei in used_edges:
            ax.scatter(*mp, color='#ffd93d', s=50, zorder=6,
                       depthshade=False, edgecolors='white', linewidths=0.5)
            # Offset label away from cube centre
            centre = np.array([0.5, 0.5, 0.5])
            direction = mp - centre
            if np.linalg.norm(direction) < 1e-6:
                direction = np.array([0, 0, 1])
            direction = direction / np.linalg.norm(direction)
            lp = mp + direction * 0.10
            ax.text(lp[0], lp[1], lp[2],
                    f'E{ei}',
                    color='#ffd93d', fontsize=7.5, fontweight='bold',
                    ha='center', va='center', zorder=10)

    # ── Triangles ─────────────────────────────────────────────────────────────
    COLORS = ['#ff9f43', '#48dbfb', '#ff6b9d', '#a29bfe', '#55efc4']
    for ti, tri_edges in enumerate(triangles):
        pts = np.array([edge_midpoint(e) for e in tri_edges])
        poly = Poly3DCollection([pts],
                                alpha=0.45,
                                facecolor=COLORS[ti % len(COLORS)],
                                edgecolor='white',
                                linewidth=1.5,
                                zorder=4)
        ax.add_collection3d(poly)

    # ── Axes & labels ────────────────────────────────────────────────────────
    ax.set_xlim(-.2, 1.3)
    ax.set_ylim(-.2, 1.3)
    ax.set_zlim(-.2, 1.3)
    ax.set_xlabel('X', color='#aaaacc', labelpad=6)
    ax.set_ylabel('Y', color='#aaaacc', labelpad=6)
    ax.set_zlabel('Z', color='#aaaacc', labelpad=6)
    ax.tick_params(colors='#aaaacc', labelsize=7)
    for spine in ax.spines.values():
        spine.set_edgecolor('#4a4a6a')

    ax.view_init(elev=22, azim=-55)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_elements = [
        mpatches.Patch(facecolor='#ff6b6b', edgecolor='white', label=f'High vertices: {[f"V{v}" for v in high]}'),
        mpatches.Patch(facecolor='#4ecdc4', edgecolor='white', label=f'Low vertices:  {[f"V{v}" for v in low]}'),
        mpatches.Patch(facecolor='#ffd93d', edgecolor='white', label=f'Active edges:  {[f"E{e}" for e in used_edges]}'),
    ]
    for ti, tri_edges in enumerate(triangles):
        legend_elements.append(
            mpatches.Patch(facecolor=COLORS[ti % len(COLORS)], edgecolor='white',
                           label=f'Triangle {ti}: E{tri_edges[0]}–E{tri_edges[1]}–E{tri_edges[2]}')
        )
    ax.legend(handles=legend_elements,
              loc='upper left', fontsize=8,
              facecolor='#2d2d4a', edgecolor='#4a4a6a',
              labelcolor='white', framealpha=0.85)

    # ── Title ────────────────────────────────────────────────────────────────
    bin_str = format(case, '08b')
    title = (f'Marching Cube — Case {case}  (0b{bin_str})\n'
             f'{len(triangles)} triangle(s) | '
             f'{len(high)} high vertex/vertices: {[f"V{v}" for v in high]}')
    fig.suptitle(title, color='white', fontsize=11, fontweight='bold', y=0.97)

    plt.tight_layout()
    plt.show()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    case, triangles = parse_args()
    draw(case, triangles)
