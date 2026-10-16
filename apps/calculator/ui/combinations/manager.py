"""Per-section dialog handle and external session store."""
from tkinter import ttk
from dataclasses import replace

from apps.calculator.application.combinations.adapters import StandardAdapter, seed_session
from apps.calculator.ui.batch_dialogs.dialog_handle import BatchDialogHandle
from apps.calculator.ui.batch_dialogs.shell import BatchDialogShell
from .dialog import CombinationContent


class CombinationManager:
    def __init__(self, parent, source):
        self.parent, self.source = parent, source
        self.adapter = StandardAdapter()
        self.sessions = {}
        self.contexts = []
        self.handle = BatchDialogHandle()
        self.current = None
        self.last_source_identity = None
        parent.bind("<Destroy>", self.on_destroy, add="+")

    def open(self):
        contexts = list(self.source())
        for ctx in contexts:
            if ctx.identity not in self.sessions:
                self.sessions[ctx.identity] = seed_session(ctx, self.adapter)
        self.contexts = contexts
        for session in self.sessions.values():
            if session.context.identity not in {ctx.identity for ctx in self.contexts}:
                self.contexts.append(session.context)
        target = contexts[0].identity
        if target == self.last_source_identity and self.current is not None:
            target = self.current.context.identity
        self.last_source_identity = contexts[0].identity
        if self.handle.dialog and self.current.context.identity != target:
            self.handle.dispose()
        self.current = self.sessions[target]
        return self.handle.open_or_focus(self.create)

    def create(self):
        content = CombinationContent(self, self.current)
        return BatchDialogShell(self.parent.winfo_toplevel(), content,
                                on_close=self.handle.clear, resize_edges=True, content_margins=True)

    def select(self, index):
        context = self.contexts[index]
        if self.current.context.identity == context.identity:
            return
        self.current = self.sessions[context.identity]
        if self.handle.dialog:
            self.handle.dialog.replace_content(CombinationContent(self, self.current))
        else:
            self.handle.open_or_focus(self.create)

    def change_options(self, options):
        if self.current.run is not None and self.current.run.status == "running":
            return
        if self.handle.dialog:
            self.handle.dialog.snapshot()
        context = replace(self.current.context, options=tuple(options.items()))
        if context.options == self.current.context.options:
            return
        self.current.context = context
        self.current.changed()
        if self.handle.dialog:
            self.handle.dialog._adapter.refresh()

    def reload_source(self):
        return next((ctx for ctx in self.source() if ctx.identity == self.current.context.identity), None)

    def reload(self):
        identity = self.current.context.identity
        source = self.reload_source()
        if source is None:
            return
        self.handle.dispose()
        self.current = seed_session(source, self.adapter)
        self.sessions[identity] = self.current
        self.handle.open_or_focus(self.create)

    def on_destroy(self, event):
        if event.widget is self.parent:
            self.handle.dispose()


def add_combination_action(section, source):
    manager = CombinationManager(section._frame, source)
    section.combinations = manager
    section.combination_button = ttk.Button(section.batch_button.master, text="조합 계산", command=manager.open)
    section.combination_button.pack(side="left")
    return manager
