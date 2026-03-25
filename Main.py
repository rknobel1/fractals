import math
import tkinter as tk
import tkinter.messagebox
from collections import deque

import Fractal_Logic as fl
import Utils as sim


# Tile size used for seed creation
TILE_SIZE = 30

# Tile size used in the result viewer
VIEW_TILE_SIZE = 64


# ----------------------------
# Seed helpers
# ----------------------------
def check_valid_seed(tile_positions):
    valid, error = True, []

    if len(tile_positions) < 1:
        valid = False
        error = "Left click to place tiles"
    else:
        for cord in tile_positions:
            [x, y] = cord.split(',')
            x, y = int(x), int(y)

            if (
                get_tag(x, y - TILE_SIZE * 2) not in tile_positions
                and get_tag(x + TILE_SIZE * 2, y) not in tile_positions
                and get_tag(x - TILE_SIZE * 2, y) not in tile_positions
                and get_tag(x, y + TILE_SIZE * 2) not in tile_positions
            ):
                valid = False
                error = "Fractal must be connected"
                break

    if not valid:
        return [valid, error]

    min_x, max_x, min_y, max_y = math.inf, -1, math.inf, -1
    for cord in tile_positions:
        [x, y] = cord.split(',')
        x, y = int(x), int(y)

        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    n, e, w, s = False, False, False, False
    for cord in tile_positions:
        [x, y] = cord.split(',')
        x, y = int(x), int(y)

        if (x == min_x and get_tag(max_x, y) in tile_positions) or (
            x == max_x and get_tag(min_x, y) in tile_positions
        ):
            e, w = True, True
        if (y == min_y and get_tag(x, max_y) in tile_positions) or (
            y == max_y and get_tag(x, min_y) in tile_positions
        ):
            n, s = True, True

    if not (n and s):
        return [False, "Not feasible generator (north/south)"]
    if not (e and w):
        return [False, "Not feasible generator (east/west)"]

    return [True, error]



def get_tag(x, y):
    return str(x) + ',' + str(y)



def get_xy(x, y):
    step = TILE_SIZE * 2
    return [step * round(x / step), step * round(y / step)]



def create_seed(tile_positions, origin_tile_cords):
    tile_positions = dict(tile_positions)
    new_tiles = dict([])
    stack = deque()
    stack.append([origin_tile_cords[0], origin_tile_cords[1], None])
    seed_tile = None

    visited = []

    min_x, max_x, min_y, max_y = math.inf, -1, math.inf, -1
    for cord in tile_positions:
        [x, y] = cord.split(',')
        x, y = int(x), int(y)

        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y

    while len(stack) > 0:
        [x, y, prev] = stack.popleft()
        next_dirs = []

        if [x, y] not in visited:
            visited.append([x, y])

        if get_tag(x, y - TILE_SIZE * 2) in tile_positions and get_tag(x, y - TILE_SIZE * 2) not in visited:
            stack.append([x, y - TILE_SIZE * 2, 'S'])
            visited.append(get_tag(x, y - TILE_SIZE * 2))
            next_dirs.append('N')
        if get_tag(x + TILE_SIZE * 2, y) in tile_positions and get_tag(x + TILE_SIZE * 2, y) not in visited:
            stack.append([x + TILE_SIZE * 2, y, 'W'])
            visited.append(get_tag(x + TILE_SIZE * 2, y))
            next_dirs.append('E')
        if get_tag(x - TILE_SIZE * 2, y) in tile_positions and get_tag(x - TILE_SIZE * 2, y) not in visited:
            stack.append([x - TILE_SIZE * 2, y, 'E'])
            visited.append(get_tag(x - TILE_SIZE * 2, y))
            next_dirs.append('W')
        if get_tag(x, y + TILE_SIZE * 2) in tile_positions and get_tag(x, y + TILE_SIZE * 2) not in visited:
            stack.append([x, y + TILE_SIZE * 2, 'N'])
            visited.append(get_tag(x, y + TILE_SIZE * 2))
            next_dirs.append('S')

        if get_tag(x, y) in tile_positions:
            del tile_positions[get_tag(x, y)]

        if len(next_dirs) == 0:
            next_dirs = None

        if prev is None:
            tile = fl.Tile(prev, next_dirs)
        else:
            tile = fl.Tile([prev], next_dirs)

        if prev is None or next_dirs is None:
            tile.terminal = True
        new_tiles[get_tag(x, y)] = tile

        if prev == 'N':
            tile.tile_to_N = new_tiles[get_tag(x, y - TILE_SIZE * 2)]
            new_tiles[get_tag(x, y - TILE_SIZE * 2)].tile_to_S = tile
            tile.N = 'N'
        if prev == 'E':
            tile.tile_to_E = new_tiles[get_tag(x + TILE_SIZE * 2, y)]
            new_tiles[get_tag(x + TILE_SIZE * 2, y)].tile_to_W = tile
            tile.E = 'N'
        if prev == 'W':
            tile.tile_to_W = new_tiles[get_tag(x - TILE_SIZE * 2, y)]
            new_tiles[get_tag(x - TILE_SIZE * 2, y)].tile_to_E = tile
            tile.W = 'N'
        if prev == 'S':
            tile.tile_to_S = new_tiles[get_tag(x, y + TILE_SIZE * 2)]
            new_tiles[get_tag(x, y + TILE_SIZE * 2)].tile_to_N = tile
            tile.S = 'N'

        if next_dirs is not None:
            for d in next_dirs:
                if d == 'N':
                    tile.N = 'N'
                if d == 'E':
                    tile.E = 'N'
                if d == 'W':
                    tile.W = 'N'
                if d == 'S':
                    tile.S = 'N'

        if [x, y] == origin_tile_cords:
            seed_tile = tile
            tile.original_seed = True
            if tile.next is not None and len(tile.next) > 1:
                tile.terminal = False

    ktn, kte, ktw, kts = None, None, None, None

    for cord in new_tiles:
        [x, y] = cord.split(',')
        x, y = int(x), int(y)

        if (x == min_x and get_tag(max_x, y) in new_tiles) or (x == max_x and get_tag(min_x, y) in new_tiles):
            if [x, y] == origin_tile_cords:
                ktw, kte = new_tiles[get_tag(min_x, y)], new_tiles[get_tag(max_x, y)]
            elif ktw is None and kte is None:
                ktw, kte = new_tiles[get_tag(min_x, y)], new_tiles[get_tag(max_x, y)]
        if (y == min_y and get_tag(x, max_y) in new_tiles) or (y == max_y and get_tag(x, min_y) in new_tiles):
            if [x, y] == origin_tile_cords:
                ktn, kts = new_tiles[get_tag(x, min_y)], new_tiles[get_tag(x, max_y)]
            elif ktn is None and kts is None:
                ktn, kts = new_tiles[get_tag(x, min_y)], new_tiles[get_tag(x, max_y)]

    ktn.key_tile_N = None
    kte.key_tile_E = None
    ktw.key_tile_W = None
    kts.key_tile_S = None

    visited_tiles = []
    stack = deque([ktn])
    while stack:
        cur_tile = stack.pop()
        visited_tiles.append(cur_tile)
        if cur_tile.next is not None:
            for n in cur_tile.next:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_N = [fl.opp(n)]
                    stack.append(adj_tile)
        if cur_tile.previous is not None:
            for n in cur_tile.previous:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_N = [fl.opp(n)]
                    stack.append(adj_tile)

    visited_tiles = []
    stack = deque([kte])
    while stack:
        cur_tile = stack.pop()
        visited_tiles.append(cur_tile)
        if cur_tile.next is not None:
            for n in cur_tile.next:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_E = [fl.opp(n)]
                    stack.append(adj_tile)
        if cur_tile.previous is not None:
            for n in cur_tile.previous:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_E = [fl.opp(n)]
                    stack.append(adj_tile)

    visited_tiles = []
    stack = deque([ktw])
    while stack:
        cur_tile = stack.pop()
        visited_tiles.append(cur_tile)
        if cur_tile.next is not None:
            for n in cur_tile.next:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_W = [fl.opp(n)]
                    stack.append(adj_tile)
        if cur_tile.previous is not None:
            for n in cur_tile.previous:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_W = [fl.opp(n)]
                    stack.append(adj_tile)

    visited_tiles = []
    stack = deque([kts])
    while stack:
        cur_tile = stack.pop()
        visited_tiles.append(cur_tile)
        if cur_tile.next is not None:
            for n in cur_tile.next:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_S = [fl.opp(n)]
                    stack.append(adj_tile)
        if cur_tile.previous is not None:
            for n in cur_tile.previous:
                adj_tile = fl.retrieve_tile(cur_tile, n)
                if adj_tile not in visited_tiles:
                    adj_tile.key_tile_S = [fl.opp(n)]
                    stack.append(adj_tile)

    return seed_tile


# ----------------------------
# Result viewer
# ----------------------------
class TileViewer(tk.Toplevel):
    def __init__(self, master, title, snapshots, mode_name):
        super().__init__(master)
        self.title(title)
        self.geometry("1500x900")
        self.minsize(1200, 700)
        self.configure(bg="#f4f6fb")

        self.snapshots = snapshots
        self.snapshot_index = len(snapshots) - 1
        self.mode_name = mode_name
        self.canvas_items = {}
        self.selected_rect = None

        self._build_ui()
        self._render_current_snapshot()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header = tk.Frame(self, bg="#ffffff", bd=1, relief="solid")
        header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=12, pady=(12, 8))
        header.columnconfigure(1, weight=1)

        self.title_label = tk.Label(
            header,
            text="Simulation Viewer",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, padx=14, pady=12, sticky="w")

        self.summary_label = tk.Label(
            header,
            text="",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#334155",
            anchor="w",
            justify="left",
            wraplength=700,
        )
        self.summary_label.grid(row=0, column=1, padx=8, pady=12, sticky="w")

        controls = tk.Frame(header, bg="#ffffff")
        controls.grid(row=0, column=2, padx=12, pady=8, sticky="e")

        self.prev_btn = tk.Button(controls, text="◀ Prev", command=self.prev_snapshot, width=10)
        self.prev_btn.grid(row=0, column=0, padx=4)
        self.next_btn = tk.Button(controls, text="Next ▶", command=self.next_snapshot, width=10)
        self.next_btn.grid(row=0, column=1, padx=4)
        fit_btn = tk.Button(controls, text="Fit View", command=self.fit_view, width=10)
        fit_btn.grid(row=0, column=2, padx=4)

        viewport_frame = tk.Frame(self, bg="#f4f6fb")
        viewport_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 12))
        viewport_frame.rowconfigure(0, weight=1)
        viewport_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            viewport_frame,
            bg="#edf2f7",
            highlightthickness=0,
            xscrollincrement=20,
            yscrollincrement=20,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        x_scroll = tk.Scrollbar(viewport_frame, orient="horizontal", command=self.canvas.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        y_scroll = tk.Scrollbar(viewport_frame, orient="vertical", command=self.canvas.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)

        sidebar = tk.Frame(self, bg="#ffffff", bd=1, relief="solid", width=420)
        sidebar.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        sidebar.rowconfigure(1, weight=1)
        sidebar.columnconfigure(0, weight=1)

        mode_chip = tk.Label(
            sidebar,
            text=f"Mode: {self.mode_name}",
            bg="#e2e8f0",
            fg="#0f172a",
            font=("Segoe UI", 10, "bold"),
            padx=0,
            pady=0,
        )
        mode_chip.grid(row=0, column=0, sticky="ew", padx=0, pady=0)

        detail_frame = tk.Frame(sidebar, bg="#ffffff")
        detail_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        detail_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)

        self.detail_text = tk.Text(
            detail_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="#ffffff",
            fg="#0f172a",
            relief="flat",
            bd=0,
            highlightthickness=0,
            padx=8,
            pady=8,
        )
        self.detail_text.grid(row=0, column=0, sticky="nsew")

        detail_scroll = tk.Scrollbar(detail_frame, orient="vertical", command=self.detail_text.yview)
        detail_scroll.grid(row=0, column=1, sticky="ns")
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        self.detail_text.insert("1.0", "Click a tile to inspect it.\n")
        self.detail_text.config(state="disabled")

        legend = tk.Label(
            sidebar,
            justify="left",
            anchor="nw",
            bg="#ffffff",
            fg="#475569",
            font=("Segoe UI", 9),
            text=(
                "Legend\n"
                "• Black = original seed\n"
                "• Gold = pseudo seed\n"
                "• Red = wall\n"
                "• Green = active/copied status\n"
                "• Gray = neutral tile\n\n"
                "Step mode here is stage-by-stage.\n"
                "It does not yet expose every internal\n"
                "transition inside run_simulation()."
            ),
        )
        legend.grid(row=2, column=0, sticky="ew", padx=8, pady=8)

    def _color_for_tile(self, item):
        if item["original_seed"]:
            return "#111827"
        if item["pseudo_seed"]:
            return "#f59e0b"
        if item["wall"]:
            return "#ef4444"
        if item["status"] in {"P", "W", "M", "C", "R", "Y"}:
            return "#22c55e"
        if item["terminal"]:
            return "#cbd5e1"
        return "#94a3b8"

    def _render_current_snapshot(self):
        snapshot = self.snapshots[self.snapshot_index]
        layout = snapshot["layout"]
        summary = snapshot["summary"]

        self.canvas.delete("all")
        self.canvas_items.clear()
        self.selected_rect = None

        if not layout:
            return

        xs = [item["x"] for item in layout]
        ys = [item["y"] for item in layout]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        margin = 80
        width = (max_x - min_x + 1) * VIEW_TILE_SIZE + margin * 2
        height = (max_y - min_y + 1) * VIEW_TILE_SIZE + margin * 2
        self.canvas.configure(scrollregion=(0, 0, width, height))

        for item in layout:
            gx = item["x"] - min_x
            gy = max_y - item["y"]
            x0 = margin + gx * VIEW_TILE_SIZE
            y0 = margin + gy * VIEW_TILE_SIZE
            x1 = x0 + VIEW_TILE_SIZE - 10
            y1 = y0 + VIEW_TILE_SIZE - 10
            color = self._color_for_tile(item)

            rect = self.canvas.create_rectangle(
                x0,
                y0,
                x1,
                y1,
                fill=color,
                outline="#1e293b",
                width=1,
                tags=("tile", f"tile_{id(item['tile'])}"),
            )

            label = item["copy_direction"] or item["status"] or ""
            text_color = "#ffffff" if color in {"#111827", "#ef4444"} else "#0f172a"
            self.canvas.create_text(
                (x0 + x1) / 2,
                (y0 + y1) / 2,
                text=label,
                fill=text_color,
                font=("Segoe UI", 10, "bold"),
            )

            self.canvas_items[rect] = item

        title_text = snapshot["title"]
        status_summary = ", ".join(f"{k}: {v}" for k, v in sorted(summary["status_counts"].items())) or "None"
        self.title_label.config(text=title_text)
        self.summary_label.config(
            text=(
                f"Tiles: {summary['tile_count']}    "
                f"Bounds: x[{summary['bounds'][0]}, {summary['bounds'][1]}], "
                f"y[{summary['bounds'][2]}, {summary['bounds'][3]}]\n"
                f"Statuses: {status_summary}"
            )
        )

        self._set_detail(snapshot["explanation"])
        self.fit_view()
        self._update_nav_state()

    def _pretty_value(self, value, indent="  "):
        if isinstance(value, dict):
            if not value:
                return "{}"
            parts = []
            for k, v in value.items():
                parts.append(f"{indent}{k}: {self._pretty_value(v, indent + '  ')}")
            return "\n".join(parts)
        if isinstance(value, (list, tuple, set)):
            seq = list(value)
            if not seq:
                return "[]"
            return "\n".join(f"{indent}- {item}" for item in seq)
        if value is None:
            return "None"
        return str(value)

    def _set_detail(self, text):
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("1.0", text)
        self.detail_text.config(state="disabled")

    def _on_canvas_click(self, event):
        item_id = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        if not item_id:
            return
        item_id = item_id[0]
        if item_id not in self.canvas_items:
            return

        tile_info = self.canvas_items[item_id]
        if self.selected_rect is not None:
            self.canvas.itemconfig(self.selected_rect, width=1)
        self.selected_rect = item_id
        self.canvas.itemconfig(item_id, width=4)

        details = [
            f"Grid position: ({tile_info['x']}, {tile_info['y']})",
            f"Status: {tile_info['status']}",
            f"Copy direction: {tile_info['copy_direction']}",
            f"Original seed: {tile_info['original_seed']}",
            f"Pseudo seed: {tile_info['pseudo_seed']}",
            f"Wall: {tile_info['wall']}",
            f"Terminal: {tile_info['terminal']}",
            "",
            "Caps:",
            self._pretty_value(tile_info['caps']),
            "",
            "Next:",
            self._pretty_value(tile_info['next']),
            "",
            "Previous:",
            self._pretty_value(tile_info['previous']),
            "",
            "Breadcrumbs:",
            self._pretty_value(tile_info['breadcrumbs']),
            "",
            "Key tiles:",
            self._pretty_value(tile_info['key_tiles']),
        ]
        self._set_detail("\n".join(details))

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def fit_view(self):
        self.update_idletasks()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def prev_snapshot(self):
        if self.snapshot_index > 0:
            self.snapshot_index -= 1
            self._render_current_snapshot()

    def next_snapshot(self):
        if self.snapshot_index < len(self.snapshots) - 1:
            self.snapshot_index += 1
            self._render_current_snapshot()

    def _update_nav_state(self):
        if len(self.snapshots) <= 1:
            self.prev_btn.config(state="disabled")
            self.next_btn.config(state="disabled")
            return
        self.prev_btn.config(state=("normal" if self.snapshot_index > 0 else "disabled"))
        self.next_btn.config(state=("normal" if self.snapshot_index < len(self.snapshots) - 1 else "disabled"))


# ----------------------------
# App frames
# ----------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.tile_positions = {}
        self.origin_tile = None
        self.stages = 1
        self.run_mode = tk.StringVar(value="pure")

        self.title('Fractals in Seeded TA')
        self.geometry('1100x700')
        self.configure(bg="#f4f6fb")

        container = tk.Frame(self, bg="#f4f6fb")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for frame_cls in (DrawSeedFrame, ChooseOriginFrame, SelectStagesFrame):
            frame = frame_cls(container, self)
            self.frames[frame_cls] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(DrawSeedFrame)

    def show_frame(self, frame_cls):
        frame = self.frames[frame_cls]
        frame.tkraise()
        frame.refresh()

    def finish(self):
        if self.origin_tile is None:
            return

        base_seed = create_seed(self.tile_positions, self.origin_tile)

        try:
            if self.run_mode.get() == "pure":
                seed_for_run = sim.clone_seed(base_seed)
                seed_tile, states, transitions, affinities, _ = sim.run_simulation_clean(seed_for_run, self.stages)
                layout = sim.extract_tile_layout(seed_tile)
                summary = sim.summarize_layout(layout)
                snapshots = [
                    {
                        "title": f"Pure simulation result (stages={self.stages})",
                        "layout": layout,
                        "summary": summary,
                        "explanation": (
                            f"Simulation completed to stage {self.stages}.\n"
                            f"Rules generated: {len(states)} states, {len(transitions)} transitions, {len(affinities)} affinities.\n"
                            f"This is the final assembly view."
                        ),
                    }
                ]
                TileViewer(self, "Simulation Result", snapshots, mode_name="Pure")
            else:
                snapshots = []
                for stage_idx in range(1, self.stages + 1):
                    stage_seed = sim.clone_seed(base_seed)
                    seed_tile, states, transitions, affinities, _ = sim.run_simulation_clean(stage_seed, stage_idx)
                    layout = sim.extract_tile_layout(seed_tile)
                    summary = sim.summarize_layout(layout)
                    snapshots.append(
                        {
                            "title": f"Step mode — stage {stage_idx} of {self.stages}",
                            "layout": layout,
                            "summary": summary,
                            "explanation": (
                                f"This snapshot shows the assembly after stage {stage_idx}.\n"
                                f"Current tiles: {summary['tile_count']}\n"
                                f"Accumulated rules in this run: {len(states)} states, {len(transitions)} transitions, {len(affinities)} affinities.\n\n"
                                f"Note: this step mode is stage-by-stage rather than every internal transition inside run_simulation()."
                            ),
                        }
                    )
                TileViewer(self, "Step Viewer", snapshots, mode_name="Step")
        except Exception as exc:
            tk.messagebox.showerror("Simulation error", str(exc))


class DrawSeedFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6fb")
        self.controller = controller

        self.header = tk.Frame(self, bg="#ffffff", bd=1, relief="solid")
        self.header.pack(fill="x", padx=16, pady=(16, 10))

        tk.Label(
            self.header,
            text="Draw your seed",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
        ).pack(anchor="w", padx=14, pady=(12, 2))

        tk.Label(
            self.header,
            text="Left click to place tiles. Right click to delete. Then choose the origin tile and the run mode.",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#475569",
        ).pack(anchor="w", padx=14, pady=(0, 12))

        body = tk.Frame(self, bg="#f4f6fb")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(body, bg="#e2e8f0", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self.add_tile)
        self.canvas.bind("<Button-3>", self.remove_tile)

        side = tk.Frame(body, bg="#ffffff", bd=1, relief="solid", width=260)
        side.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        side.grid_propagate(False)

        tk.Label(side, text="Seed settings", font=("Segoe UI", 13, "bold"), bg="#ffffff").pack(anchor="w", padx=14, pady=(14, 8))

        tk.Label(side, text="Run mode", font=("Segoe UI", 10, "bold"), bg="#ffffff").pack(anchor="w", padx=14, pady=(6, 4))
        tk.Radiobutton(side, text="Pure simulation", variable=self.controller.run_mode, value="pure", bg="#ffffff").pack(anchor="w", padx=18)
        tk.Radiobutton(side, text="Step mode", variable=self.controller.run_mode, value="step", bg="#ffffff").pack(anchor="w", padx=18)

        self.seed_count_label = tk.Label(side, text="Tiles: 0", font=("Segoe UI", 10), bg="#ffffff", fg="#334155")
        self.seed_count_label.pack(anchor="w", padx=14, pady=(16, 8))

        tk.Button(side, text="Done", command=self.go_to_origin, width=18).pack(anchor="w", padx=14, pady=(6, 14))

    def refresh(self):
        self.redraw_seed()

    def redraw_seed(self):
        self.canvas.delete("all")
        for cord, (_, x, y, is_origin) in self.controller.tile_positions.items():
            fill = "#111827" if is_origin else "#ffffff"
            self.canvas.create_rectangle(x - TILE_SIZE, y - TILE_SIZE, x + TILE_SIZE, y + TILE_SIZE, fill=fill, outline="#334155")
        self.seed_count_label.config(text=f"Tiles: {len(self.controller.tile_positions)}")

    def add_tile(self, event):
        x, y = get_xy(event.x, event.y)
        tag = get_tag(x, y)
        if tag not in self.controller.tile_positions:
            self.controller.tile_positions[tag] = (None, x, y, 0)
            self.redraw_seed()

    def remove_tile(self, event):
        x, y = get_xy(event.x, event.y)
        tag = get_tag(x, y)
        if tag in self.controller.tile_positions:
            if self.controller.origin_tile == [x, y]:
                self.controller.origin_tile = None
            del self.controller.tile_positions[tag]
            self.redraw_seed()

    def go_to_origin(self):
        valid, error = check_valid_seed(self.controller.tile_positions)
        if valid:
            self.controller.show_frame(ChooseOriginFrame)
        else:
            tk.messagebox.showinfo("Invalid seed", error)


class ChooseOriginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6fb")
        self.controller = controller

        header = tk.Frame(self, bg="#ffffff", bd=1, relief="solid")
        header.pack(fill="x", padx=16, pady=(16, 10))
        tk.Label(header, text="Choose the origin tile", font=("Segoe UI", 18, "bold"), bg="#ffffff").pack(anchor="w", padx=14, pady=(12, 2))
        tk.Label(header, text="Left click one tile to mark it as the origin.", font=("Segoe UI", 10), bg="#ffffff", fg="#475569").pack(anchor="w", padx=14, pady=(0, 12))

        self.canvas = tk.Canvas(self, bg="#e2e8f0", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.canvas.bind("<Button-1>", self.choose_origin)

        bottom = tk.Frame(self, bg="#f4f6fb")
        bottom.pack(fill="x", padx=16, pady=(0, 16))
        tk.Button(bottom, text="Back", command=lambda: self.controller.show_frame(DrawSeedFrame), width=12).pack(side="left")
        tk.Button(bottom, text="Done", command=self.go_to_stages, width=12).pack(side="right")

    def refresh(self):
        self.canvas.delete("all")
        for cord, (_, x, y, is_origin) in self.controller.tile_positions.items():
            fill = "#111827" if is_origin else "#ffffff"
            self.canvas.create_rectangle(x - TILE_SIZE, y - TILE_SIZE, x + TILE_SIZE, y + TILE_SIZE, fill=fill, outline="#334155")

    def choose_origin(self, event):
        x, y = get_xy(event.x, event.y)
        tag = get_tag(x, y)
        if tag not in self.controller.tile_positions:
            return

        updated = {}
        for cord, (_, tx, ty, _) in self.controller.tile_positions.items():
            updated[cord] = (None, tx, ty, 1 if cord == tag else 0)
        self.controller.tile_positions = updated
        self.controller.origin_tile = [x, y]
        self.refresh()

    def go_to_stages(self):
        if self.controller.origin_tile is not None:
            self.controller.show_frame(SelectStagesFrame)


class SelectStagesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f4f6fb")
        self.controller = controller
        self.stage_var = tk.StringVar(value="1")

        card = tk.Frame(self, bg="#ffffff", bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(card, text="Choose the number of stages", font=("Segoe UI", 18, "bold"), bg="#ffffff").pack(anchor="w", padx=18, pady=(18, 4))
        tk.Label(card, text="Higher stages can grow very quickly. Step mode currently shows one snapshot per stage.", font=("Segoe UI", 10), bg="#ffffff", fg="#475569").pack(anchor="w", padx=18, pady=(0, 18))

        self.dropdown_holder = tk.Frame(card, bg="#ffffff")
        self.dropdown_holder.pack(anchor="w", padx=18, pady=(0, 16))

        controls = tk.Frame(card, bg="#ffffff")
        controls.pack(fill="x", padx=18, pady=(0, 18))
        tk.Button(controls, text="Back", command=lambda: self.controller.show_frame(ChooseOriginFrame), width=12).pack(side="left")
        tk.Button(controls, text="Run", command=self.run, width=12).pack(side="right")

    def refresh(self):
        for child in self.dropdown_holder.winfo_children():
            child.destroy()

        options = []
        num_tiles = max(1, len(self.controller.tile_positions))
        stage = 1
        actual_stage = 1

        while num_tiles < 30000:
            options.append(f"{stage} - (stage: {actual_stage})")
            num_tiles *= num_tiles
            stage += 1
            actual_stage *= 2

        if not options:
            options = ["1 - (stage: 1)"]

        self.stage_var.set(options[0])
        tk.OptionMenu(self.dropdown_holder, self.stage_var, *options).pack(anchor="w")

    def run(self):
        self.controller.stages = int(self.stage_var.get().split(' ')[0])
        self.controller.finish()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
