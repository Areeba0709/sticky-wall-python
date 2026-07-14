import customtkinter as ctk
import random
import json
import os
from datetime import datetime
from tkinter import messagebox

ctk.set_appearance_mode("dark")

class StickyNote:
    def __init__(self, parent, x, y, text, color, note_id=None, created_date=None, 
                 completed=False, pinned=False, on_delete=None, on_complete=None, on_pin=None, on_edit=None):
        self.parent = parent
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.note_id = note_id or str(datetime.now().timestamp())
        self.created_date = created_date or datetime.now().strftime("%Y-%m-%d")
        self.completed = completed
        self.pinned = pinned
        self.on_delete = on_delete
        self.on_complete = on_complete
        self.on_pin = on_pin
        self.on_edit = on_edit
        
        self.create_note()
    
    def create_note(self):
        self.frame = ctk.CTkFrame(
            self.parent,
            fg_color=self.color,
            corner_radius=10,
            width=230,
            height=160
        )
        self.frame.place(x=self.x, y=self.y)
        self.frame.pack_propagate(False)
        
        if self.pinned:
            self.pin_indicator = ctk.CTkLabel(
                self.frame,
                text="📌",
                font=("Segoe UI", 12),
                text_color="#f39c12",
                fg_color="transparent"
            )
            self.pin_indicator.place(x=8, y=5)
        
        # DATE LABEL - Made more visible (darker, more readable color)
        self.date_label = ctk.CTkLabel(
            self.frame,
            text=f"📅 {self.created_date}",
            font=("Segoe UI", 10, "bold"),
            text_color="#2C1810",  # Changed from #666666 to dark brown for better visibility
            fg_color="#E8D5B7",    # Added light parchment background
            corner_radius=8,
            padx=8,
            pady=2
        )
        self.date_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        display_text = f"✓ {self.text}" if self.completed else self.text
        
        self.label = ctk.CTkLabel(
            self.frame,
            text=display_text,
            font=("Segoe UI", 13, "bold"),
            text_color="#000000",
            wraplength=200,
            justify="left"
        )
        self.label.pack(pady=(5, 35), padx=10, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.place(relx=0.5, rely=0.9, anchor="center")
        
        self.edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            text_color="#3498db",
            font=("Segoe UI", 12),
            command=self.edit_note
        )
        self.edit_btn.pack(side="left", padx=2)
        
        self.pin_btn = ctk.CTkButton(
            btn_frame,
            text="📍" if self.pinned else "📌",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            text_color="#f39c12",
            font=("Segoe UI", 12),
            command=self.toggle_pin
        )
        self.pin_btn.pack(side="left", padx=2)
        
        self.complete_btn = ctk.CTkButton(
            btn_frame,
            text="✅" if not self.completed else "✔️",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            text_color="#27ae60",
            font=("Segoe UI", 12),
            command=self.toggle_complete
        )
        self.complete_btn.pack(side="left", padx=2)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=28,
            height=28,
            corner_radius=14,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d",
            text_color="#e74c3c",
            font=("Segoe UI", 12),
            command=self.delete
        )
        self.delete_btn.pack(side="left", padx=2)
        
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.frame.bind("<Button-1>", self.start_drag)
        self.frame.bind("<B1-Motion>", self.on_drag)
    
    def start_drag(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.note_start_x = self.frame.winfo_x()
        self.note_start_y = self.frame.winfo_y()
    
    def on_drag(self, event):
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        new_x = self.note_start_x + dx
        new_y = self.note_start_y + dy
        self.frame.place(x=new_x, y=new_y)
        self.x = new_x
        self.y = new_y
    
    def edit_note(self):
        if self.completed:
            messagebox.showinfo("Task Completed", "Uncomplete this task to edit it.")
            return
        
        dialog = ctk.CTkToplevel(self.frame)
        dialog.title("Edit Note")
        dialog.geometry("400x350")
        dialog.transient(self.frame.winfo_toplevel())
        
        ctk.CTkLabel(dialog, text="Edit your note:", font=("Segoe UI", 16, "bold")).pack(pady=15)
        
        text_edit = ctk.CTkTextbox(dialog, height=150, font=("Segoe UI", 13))
        text_edit.pack(fill="both", expand=True, padx=20, pady=10)
        text_edit.insert("1.0", self.text)
        
        def save_edit():
            new_text = text_edit.get("1.0", "end-1c").strip()
            if new_text:
                self.text = new_text
                self.label.configure(text=new_text)
                dialog.destroy()
                if self.on_edit:
                    self.on_edit(self.note_id, new_text)
            else:
                messagebox.showwarning("Empty", "Note cannot be empty!")
        
        ctk.CTkButton(dialog, text="Save Changes", command=save_edit, fg_color="#27ae60", height=40).pack(pady=15)
    
    def toggle_pin(self):
        self.pinned = not self.pinned
        if self.pinned:
            self.pin_btn.configure(text="📍")
            self.pin_indicator = ctk.CTkLabel(
                self.frame,
                text="📌",
                font=("Segoe UI", 12),
                text_color="#f39c12",
                fg_color="transparent"
            )
            self.pin_indicator.place(x=8, y=5)
        else:
            self.pin_btn.configure(text="📌")
            if hasattr(self, 'pin_indicator'):
                self.pin_indicator.destroy()
        
        if self.on_pin:
            self.on_pin(self.note_id, self.pinned)
    
    def toggle_complete(self):
        if not self.completed:
            self.show_celebration()
            self.completed = True
            self.label.configure(text=f"✓ {self.text}", text_color="#888888")
            self.complete_btn.configure(text="✔️", text_color="#2ecc71")
        else:
            self.completed = False
            self.label.configure(text=self.text, text_color="#000000")
            self.complete_btn.configure(text="✅", text_color="#27ae60")
        
        if self.on_complete:
            self.on_complete(self.note_id, self.completed)
    
    def show_celebration(self):
        popup = ctk.CTkToplevel()
        popup.title("🎉 Congratulations!")
        popup.geometry("300x200")
        ctk.CTkLabel(popup, text="🎊 WELL DONE! 🎊", font=("Segoe UI", 20, "bold"), text_color="#2ecc71").pack(pady=20)
        ctk.CTkLabel(popup, text="✨ Task Completed! ✨", font=("Segoe UI", 14), text_color="#f39c12").pack(pady=5)
        ctk.CTkLabel(popup, text="Keep it up! 💪", font=("Segoe UI", 12)).pack(pady=10)
        popup.after(2000, popup.destroy)
    
    def delete(self):
        if self.pinned:
            result = messagebox.askyesno("Pinned Note", "This note is PINNED.\n\nDelete anyway?")
            if result:
                self.frame.destroy()
                if self.on_delete:
                    self.on_delete(self.note_id)
        else:
            if messagebox.askyesno("Delete Note", "Delete this note?"):
                self.frame.destroy()
                if self.on_delete:
                    self.on_delete(self.note_id)
    
    def get_data(self):
        return {
            'id': self.note_id,
            'text': self.text,
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'created_date': self.created_date,
            'completed': self.completed,
            'pinned': self.pinned
        }

class StickyWall:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Sticky Wall - Wooden Theme")
        self.window.geometry("1400x850")
        
        self.notes = {}
        self.pinned_notes = []
        self.load_notes()
        self.setup_ui()
        self.check_overdue()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def check_overdue(self):
        today = datetime.now().date()
        overdue = []
        for note in self.notes.values():
            if not note.completed:
                note_date = datetime.strptime(note.created_date, "%Y-%m-%d").date()
                if note_date < today:
                    overdue.append(note.text[:40])
        
        if overdue:
            messagebox.showwarning("Reminder", f"😔 You have {len(overdue)} pending tasks from previous days!")
    
    def update_pinned_positions(self):
        y_offset = 20
        visible_count = 0
        for note in self.pinned_notes:
            if note.pinned:
                if visible_count < 5:
                    new_x = 20
                    new_y = y_offset
                    note.frame.place(x=new_x, y=new_y)
                    note.x = new_x
                    note.y = new_y
                    y_offset += 170
                    visible_count += 1
                else:
                    note.frame.place_forget()
        
        total_pinned = len(self.pinned_notes)
        if total_pinned > 5:
            self.pinned_info_label.configure(
                text=f"📌 Top 5 pinned notes ({total_pinned - 5} more hidden)",
                text_color="#FFD700"
            )
        elif total_pinned > 0:
            self.pinned_info_label.configure(
                text=f"📌 {total_pinned} pinned note{'s' if total_pinned > 1 else ''}",
                text_color="#FFD700"
            )
        else:
            self.pinned_info_label.configure(text="")
    
    def on_note_pin(self, note_id, pinned):
        note = self.notes[note_id]
        
        if pinned:
            if note not in self.pinned_notes:
                self.pinned_notes.append(note)
        else:
            if note in self.pinned_notes:
                self.pinned_notes.remove(note)
            if hasattr(note, 'original_x') and note.original_x:
                note.frame.place(x=note.original_x, y=note.original_y)
                note.x = note.original_x
                note.y = note.original_y
            else:
                w = max(400, self.wall.winfo_width())
                h = max(300, self.wall.winfo_height())
                note.x = random.randint(10, w - 240)
                note.y = random.randint(10, h - 180)
                note.frame.place(x=note.x, y=note.y)
        
        self.update_pinned_positions()
        self.save_notes()
        self.update_stats()
    
    def on_note_edit(self, note_id, new_text):
        self.save_notes()
    
    def setup_ui(self):
        # Main container - Dark walnut wood color
        main = ctk.CTkFrame(self.window, fg_color="#4A2F1D")
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # TOP BAR - Lighter wood like oak
        top = ctk.CTkFrame(main, height=60, fg_color="#8B6914", corner_radius=15)
        top.pack(fill="x", pady=(0, 15))
        
        # Wood grain lines on top bar
        wood_line1 = ctk.CTkFrame(top, height=2, fg_color="#6B4F12", corner_radius=0)
        wood_line1.pack(fill="x", padx=10, pady=(5,0))
        wood_line2 = ctk.CTkFrame(top, height=1, fg_color="#A07818", corner_radius=0)
        wood_line2.pack(fill="x", padx=10, pady=(2,0))
        
        ctk.CTkLabel(
            top, 
            text="🌲 STICKY WALL 🌲", 
            font=("Segoe UI", 26, "bold"),
            text_color="#FFE4B5"  # Moccasin color
        ).pack(side="left", padx=25)
        
        self.stats_label = ctk.CTkLabel(
            top, 
            text="", 
            font=("Segoe UI", 14, "bold"),
            text_color="#FFE4B5"
        )
        self.stats_label.pack(side="right", padx=25)
        
        wood_line3 = ctk.CTkFrame(top, height=1, fg_color="#A07818", corner_radius=0)
        wood_line3.pack(fill="x", padx=10, pady=(0,2))
        wood_line4 = ctk.CTkFrame(top, height=2, fg_color="#6B4F12", corner_radius=0)
        wood_line4.pack(fill="x", padx=10, pady=(0,5))
        
        # CONTENT
        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)
        
        # LEFT PANEL - Darker wood (mahogany)
        left = ctk.CTkFrame(content, width=380, corner_radius=15, fg_color="#3E2010")
        left.pack(side="left", fill="y", padx=(0, 15))
        left.pack_propagate(False)
        
        # Wood grain effect on left panel
        for i in range(3):
            wood_grain = ctk.CTkFrame(left, height=1, fg_color="#5A3020", corner_radius=0)
            wood_grain.pack(fill="x", padx=5, pady=(3,0))
        
        note_frame = ctk.CTkFrame(left, corner_radius=12, fg_color="#5C3A21")
        note_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            note_frame, 
            text="✏️ Write Your Note", 
            font=("Georgia", 20, "bold"),
            text_color="#FFE4B5"
        ).pack(pady=15)
        
        self.text_input = ctk.CTkTextbox(
            note_frame, 
            height=200, 
            font=("Georgia", 14),
            fg_color="#FFF8DC",  # Cornsilk - like parchment paper
            text_color="#3E2010",
            corner_radius=10
        )
        self.text_input.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            note_frame, 
            text="🎨 Choose Color:", 
            font=("Georgia", 14, "bold"),
            text_color="#FFE4B5"
        ).pack(pady=(10,5))
        
        self.color_var = ctk.StringVar(value="#FFD700")
        color_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
        color_frame.pack(pady=5)
        
        colors = ["#FFD700", "#FF6B6B", "#4ECDC4", "#95E77E", "#DDA0DD", "#FFA500", "#87CEEB"]
        for color in colors:
            btn = ctk.CTkButton(
                color_frame, 
                text="  ", 
                width=35, 
                height=35, 
                corner_radius=17,
                fg_color=color, 
                command=lambda c=color: self.color_var.set(c)
            )
            btn.pack(side="left", padx=4)
        
        button_frame = ctk.CTkFrame(note_frame, fg_color="transparent")
        button_frame.pack(pady=15, padx=20, fill="x")
        
        add_btn = ctk.CTkButton(
            button_frame, 
            text="📌 ADD TO WALL", 
            command=self.add_note,
            font=("Georgia", 14, "bold"), 
            fg_color="#8B6914",
            hover_color="#6B4F12",
            text_color="#FFE4B5",
            height=45
        )
        add_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ CLEAR WALL",
            command=self.clear_all_notes,
            font=("Georgia", 14, "bold"),
            fg_color="#8B6914",
            hover_color="#6B4F12",
            text_color="#FFE4B5",
            height=45
        )
        clear_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # ========== STATS SECTION ==========
        stats_frame = ctk.CTkFrame(note_frame, fg_color="#3E2010", corner_radius=10)
        stats_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            stats_frame, 
            text="📊 STATISTICS", 
            font=("Georgia", 16, "bold"),
            text_color="#FFD700"
        ).pack(pady=(10, 5))
        
        self.total_label = ctk.CTkLabel(
            stats_frame,
            text="📝 Total Notes: 0",
            font=("Georgia", 13, "bold"),
            text_color="#FFE4B5",
            anchor="w"
        )
        self.total_label.pack(anchor="w", padx=15, pady=3)
        
        self.completed_label = ctk.CTkLabel(
            stats_frame,
            text="✅ Completed: 0",
            font=("Georgia", 13, "bold"),
            text_color="#95E77E",
            anchor="w"
        )
        self.completed_label.pack(anchor="w", padx=15, pady=3)
        
        self.pending_label = ctk.CTkLabel(
            stats_frame,
            text="⏳ Pending: 0",
            font=("Georgia", 13, "bold"),
            text_color="#FF6B6B",
            anchor="w"
        )
        self.pending_label.pack(anchor="w", padx=15, pady=3)
        
        self.pinned_stat_label = ctk.CTkLabel(
            stats_frame,
            text="📌 Pinned: 0",
            font=("Georgia", 13, "bold"),
            text_color="#87CEEB",
            anchor="w"
        )
        self.pinned_stat_label.pack(anchor="w", padx=15, pady=3)
        
        ctk.CTkFrame(stats_frame, height=2, fg_color="#5C3A21").pack(fill="x", padx=15, pady=8)
        
        self.pinned_info_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=("Georgia", 11),
            text_color="#FFE4B5",
            wraplength=280
        )
        self.pinned_info_label.pack(padx=15, pady=(0, 10))
        
        # RIGHT PANEL - Wall area (bark-like texture color)
        right = ctk.CTkFrame(content, corner_radius=15, fg_color="#2D1A0F")
        right.pack(side="right", fill="both", expand=True)
        
        # Wood border frame for the wall
        wood_border = ctk.CTkFrame(right, fg_color="#6B4F12", corner_radius=12)
        wood_border.pack(fill="both", expand=True, padx=8, pady=8)
        
        ctk.CTkLabel(
            wood_border, 
            text="📌 STICKY WALL", 
            font=("Georgia", 22, "bold"), 
            text_color="#FFD700"
        ).pack(pady=12)
        
        # Wood grain lines on wall frame
        for i in range(2):
            grain = ctk.CTkFrame(wood_border, height=1, fg_color="#8B6914")
            grain.pack(fill="x", padx=20, pady=2)
        
        self.wall = ctk.CTkFrame(wood_border, fg_color="#2D1A0F", corner_radius=10)
        self.wall.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.window.after(500, self.restore_notes)
    
    def clear_all_notes(self):
        if not self.notes:
            messagebox.showinfo("No Notes", "No notes to clear!")
            return
        
        result = messagebox.askyesno("Clear Wall", f"Delete all {len(self.notes)} notes?")
        
        if result:
            for note in self.notes.values():
                note.frame.destroy()
            self.notes.clear()
            self.pinned_notes.clear()
            self.save_notes()
            self.update_stats()
            self.update_pinned_positions()
            
            label = ctk.CTkLabel(self.wall, text="🗑️ All notes cleared!", font=("Georgia", 14, "bold"), text_color="#FF6B6B")
            label.place(x=10, y=10)
            self.window.after(2000, label.destroy)
    
    def restore_notes(self):
        for data in self.saved_notes:
            note = StickyNote(
                self.wall, data['x'], data['y'], data['text'], data['color'],
                note_id=data['id'], created_date=data.get('created_date'),
                completed=data.get('completed', False),
                pinned=data.get('pinned', False),
                on_delete=self.delete_note,
                on_complete=self.on_note_change,
                on_pin=self.on_note_pin,
                on_edit=self.on_note_edit
            )
            self.notes[note.note_id] = note
            if note.pinned:
                self.pinned_notes.append(note)
        
        self.update_pinned_positions()
        self.update_stats()
    
    def add_note(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Empty", "Please write something!")
            return
        
        w = self.wall.winfo_width()
        h = self.wall.winfo_height()
        
        if w < 100:
            w = 800
        if h < 100:
            h = 500
        
        x = random.randint(20, max(100, w - 250))
        y = random.randint(20, max(100, h - 180))
        
        note = StickyNote(
            self.wall, x, y, text, self.color_var.get(),
            created_date=datetime.now().strftime("%Y-%m-%d"),
            on_delete=self.delete_note,
            on_complete=self.on_note_change,
            on_pin=self.on_note_pin,
            on_edit=self.on_note_edit
        )
        self.notes[note.note_id] = note
        self.text_input.delete("1.0", "end")
        self.save_notes()
        self.update_stats()
        
        label = ctk.CTkLabel(self.wall, text="✓ Note added!", font=("Georgia", 14, "bold"), text_color="#95E77E")
        label.place(x=10, y=10)
        self.window.after(2000, label.destroy)
    
    def on_note_change(self, note_id, completed):
        self.save_notes()
        self.update_stats()
    
    def delete_note(self, note_id):
        if note_id in self.notes:
            note = self.notes[note_id]
            if note.pinned and note in self.pinned_notes:
                self.pinned_notes.remove(note)
            del self.notes[note_id]
            self.update_pinned_positions()
            self.save_notes()
            self.update_stats()
    
    def update_stats(self):
        total = len(self.notes)
        completed = sum(1 for n in self.notes.values() if n.completed)
        pending = total - completed
        pinned = len(self.pinned_notes)
        
        self.total_label.configure(text=f"📝 Total Notes: {total}")
        self.completed_label.configure(text=f"✅ Completed: {completed}")
        self.pending_label.configure(text=f"⏳ Pending: {pending}")
        self.pinned_stat_label.configure(text=f"📌 Pinned: {pinned}")
        self.stats_label.configure(text=f"📊 {completed}/{total} | 📌 {pinned}")
    
    def save_notes(self):
        with open("stickynotes.json", "w") as f:
            json.dump([n.get_data() for n in self.notes.values()], f, indent=2)
    
    def load_notes(self):
        self.saved_notes = []
        if os.path.exists("stickynotes.json"):
            try:
                with open("stickynotes.json", "r") as f:
                    self.saved_notes = json.load(f)
            except:
                pass
    
    def on_close(self):
        self.save_notes()
        self.window.destroy()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = StickyWall()
    app.run()